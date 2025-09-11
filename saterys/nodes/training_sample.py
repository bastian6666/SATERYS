"""
SATERYS node: raster.manual_labeler
Refined UI + instant server binding + UI class manager (ID/name/color with ID change)
+ Attribute Table (search/sort/pan/edit/delete/CSV)

- Manual pixel labeling with imagery basemap and professional toolbar.
- Add/edit/remove classes from UI. Editing a class can also change its ID:
  The backend will recode the entire class raster (old_id -> new_id) and update all points.
- Attribute Table: search, sort, pan-to, edit class per row, delete (optional unpaint), CSV export.

Endpoints:
  GET  /labeler                         -> Leaflet UI
  GET  /labeler/points                  -> GeoJSON of labeled points (EPSG:4326) + pid
  GET  /labeler/points_table            -> rows [{id, lon, lat, class_id, class_name}]
  GET  /labeler/points.csv              -> CSV of current rows
  POST /labeler/click                   -> add/paint at lon/lat with class
  POST /labeler/save                    -> write points to Shapefile/GPKG (class_id, class_name)
  POST /labeler/undo                    -> undo last N paints
  GET  /labeler/classes                 -> list classes
  POST /labeler/classes/add             -> add class {name, id?, color?}
  POST /labeler/classes/update          -> update class {id, name?, color?, new_id?}
  POST /labeler/classes/remove          -> remove class {id}
  POST /labeler/points/update           -> update row {id, class_id}
  POST /labeler/points/delete           -> delete rows {ids:[...], unpaint:bool}

Dependencies:
  pip install fastapi uvicorn rasterio pyproj shapely fiona
"""

NAME = "manual_labeler"

DEFAULT_ARGS = {
    "input_path": "",                                # your raster to label against
    "class_raster_path": "./results/labels.tif",     # uint8 class raster (0 = unlabeled)
    "points_path": "./results/labels_points.gpkg",   # output vector (GPKG recommended)

    # Initial classes; 0 reserved for unlabeled
    "classes": [
        {"id": 1, "name": "Class 1", "color": "#EF4444"},
        {"id": 2, "name": "Class 2", "color": "#22C55E"},
        {"id": 3, "name": "Class 3", "color": "#3B82F6"},
    ],
    "classes_path": "./results/labels_classes.json",
    "persist_classes": True,

    "brush_size_px": 1,
    "raster_tile_url_template": "",   # optional base raster tiles under the clicks

    # Server
    "host": "127.0.0.1",
    "port": 8090,
    "open_browser": True,
    "port_autoselect": True,
    "max_port_scans": 10,
}

# ---------------- Implementation ----------------

import os
import json
import threading

_STATE = {
    "points": [],          # list of dicts: {"id":pid, "lon":..., "lat":..., "class": int}
    "next_pid": 1,
    "history": [],         # paint ops for undo (window + prev array)
    "server_running": False,
    "labeler_url": None,
    "host": None,
    "port": None,
    "classes": None,       # list[{"id","name","color"}]
}

# ---------- helpers: ports & readiness ----------

def _port_is_free(host, port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, int(port))) != 0

def _pick_port(host, port, autoselect=True, scans=10):
    if not autoselect:
        return int(port)
    p = int(port)
    for _ in range(int(scans)):
        if _port_is_free(host, p):
            return p
        p += 1
    return int(port)

def _wait_ready(url, timeout=6.0):
    import time, urllib.request
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(url, timeout=0.8) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False

# ---------- classes load/save/validate ----------

def _next_color(idx):
    import colorsys
    h = (idx * 0.145) % 1.0
    r, g, b = [int(255*x) for x in colorsys.hsv_to_rgb(h, 0.65, 0.95)]
    return f"#{r:02x}{g:02x}{b:02x}"

def _validate_classes(classes):
    used = set()
    out = []
    for i, c in enumerate(classes):
        cid = int(c.get("id", 0))
        if cid < 1 or cid > 255 or cid in used:
            cid = 1
            while cid in used and cid <= 255:
                cid += 1
        used.add(cid)
        name = str(c.get("name", f"Class {cid}"))
        color = str(c.get("color", _next_color(i)))
        if not color.startswith("#") or len(color) not in (4,7):
            color = _next_color(i)
        out.append({"id": cid, "name": name, "color": color})
    out.sort(key=lambda x: x["id"])
    return out

def _load_classes(args):
    path = args.get("classes_path") or ""
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return _validate_classes(json.load(f))
        except Exception:
            pass
    return _validate_classes(args.get("classes") or [])

def _save_classes(args, classes):
    if not bool(args.get("persist_classes", True)):
        return
    path = args.get("classes_path") or ""
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_validate_classes(classes), f, ensure_ascii=False, indent=2)

# ---------- raster ops ----------

def _ensure_class_raster(base_path, class_path):
    import rasterio
    import numpy as np
    if os.path.exists(class_path):
        return
    with rasterio.open(base_path) as src:
        profile = src.profile.copy()
        profile.update(driver="GTiff", count=1, dtype="uint8", nodata=0)
        os.makedirs(os.path.dirname(class_path), exist_ok=True)
        arr = np.zeros((src.height, src.width), dtype="uint8")
        with rasterio.open(class_path, "w", **profile) as dst:
            dst.write(arr, 1)
            try:
                from rasterio.enums import Resampling
                dst.build_overviews([2,4,8,16,32], Resampling.nearest)
            except Exception:
                pass

def _rc_from_lonlat(input_path, lon, lat):
    import rasterio
    from pyproj import Transformer
    with rasterio.open(input_path) as ref:
        crs = ref.crs
        H, W = ref.height, ref.width
        transform = ref.transform
    x, y = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform(lon, lat)
    row, col = rasterio.transform.rowcol(transform, x, y)
    return row, col, H, W, transform

def _paint_pixels(input_path, class_raster_path, lon, lat, cls, brush):
    import rasterio
    import numpy as np
    row, col, H, W, _ = _rc_from_lonlat(input_path, lon, lat)
    if row < 0 or col < 0 or row >= H or col >= W:
        return {"painted": 0, "reason": "outside raster"}
    half = max(0, int(brush)//2)
    r0, r1 = max(0, row - half), min(H, row + half + 1)
    c0, c1 = max(0, col - half), min(W, col + half + 1)
    with rasterio.open(class_raster_path, "r+") as dst:
        prev = dst.read(1, window=((r0, r1), (c0, c1))).copy()
        new = prev.copy()
        new[:, :] = np.uint8(cls)
        dst.write(new, 1, window=((r0, r1), (c0, c1)))
    _STATE["history"].append({"window": (r0, r1, c0, c1), "prev": prev})
    return {"painted": int((r1-r0)*(c1-c0))}

def _unpaint_pixels(input_path, class_raster_path, lon, lat, brush):
    # best-effort "erase": set to 0 in the same brush window
    import rasterio
    import numpy as np
    row, col, H, W, _ = _rc_from_lonlat(input_path, lon, lat)
    if row < 0 or col < 0 or row >= H or col >= W:
        return 0
    half = max(0, int(brush)//2)
    r0, r1 = max(0, row - half), min(H, row + half + 1)
    c0, c1 = max(0, col - half), min(W, col + half + 1)
    with rasterio.open(class_raster_path, "r+") as dst:
        prev = dst.read(1, window=((r0, r1), (c0, c1))).copy()
        new = prev.copy()
        new[:, :] = np.uint8(0)
        dst.write(new, 1, window=((r0, r1), (c0, c1)))
    _STATE["history"].append({"window": (r0, r1, c0, c1), "prev": prev})
    return int((r1-r0)*(c1-c0))

def _undo(class_raster_path, n=1):
    import rasterio
    undone = 0
    with rasterio.open(class_raster_path, "r+") as dst:
        while n > 0 and _STATE["history"]:
            op = _STATE["history"].pop()
            r0, r1, c0, c1 = op["window"]
            dst.write(op["prev"], 1, window=((r0, r1), (c0, c1)))
            undone += 1
            n -= 1
    return undone

def _recode_raster_values(class_raster_path, old_id, new_id):
    """Replace all pixel values == old_id with new_id in the class raster."""
    import rasterio
    import numpy as np
    if old_id == new_id:
        return 0
    changed_blocks = 0
    with rasterio.open(class_raster_path, "r+") as ds:
        for _, window in ds.block_windows(1):
            arr = ds.read(1, window=window)
            m = arr == np.uint8(old_id)
            if m.any():
                arr[m] = np.uint8(new_id)
                ds.write(arr, 1, window=window)
                changed_blocks += 1
    return changed_blocks

def _write_points(points_path, crs_wkt, points, classes):
    import fiona
    from shapely.geometry import Point, mapping
    name_map = {int(c["id"]): str(c.get("name","")) for c in (classes or [])}
    driver = "GPKG" if points_path.lower().endswith(".gpkg") else "ESRI Shapefile"
    schema = {"geometry": "Point", "properties": {"class_id": "int", "class_name": "str:64"}}
    os.makedirs(os.path.dirname(points_path), exist_ok=True)
    if os.path.exists(points_path):
        try: os.remove(points_path)
        except Exception: pass
    with fiona.open(points_path, "w", driver=driver, schema=schema, crs=crs_wkt, encoding="utf-8") as dst:
        for p in points:
            cid = int(p["class"])
            cname = name_map.get(cid, "")
            geom = mapping(Point(float(p["lon"]), float(p["lat"])))
            dst.write({"geometry": geom, "properties": {"class_id": cid, "class_name": cname}})
    return len(points), driver

def _rows(points, classes):
    name_map = {int(c["id"]): str(c.get("name","")) for c in (classes or [])}
    rows = []
    for p in points:
        rows.append({
            "id": int(p["id"]),
            "lon": float(p["lon"]),
            "lat": float(p["lat"]),
            "class_id": int(p["class"]),
            "class_name": name_map.get(int(p["class"]), "")
        })
    return rows

def _csv_text(points, classes):
    import io, csv
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["id","lon","lat","class_id","class_name"])
    for r in _rows(points, classes):
        w.writerow([r["id"], f'{r["lon"]:.8f}', f'{r["lat"]:.8f}', r["class_id"], r["class_name"]])
    return out.getvalue()

# ---------- server ----------

def _start_server(args, input_path, class_raster_path, crs_wkt):
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
    import uvicorn, webbrowser

    app = FastAPI(title="SATERYS Manual Labeler")

    _STATE["classes"] = _load_classes(args)
    BRUSH = int(args.get("brush_size_px", 1))
    TILE_TEMPLATE = args.get("raster_tile_url_template") or ""

    host = args.get("host", "127.0.0.1")
    req_port = int(args.get("port", 8090))
    port = _pick_port(host, req_port, args.get("port_autoselect", True), args.get("max_port_scans", 10))

    @app.get("/labeler", response_class=HTMLResponse)
    async def page():
        classes_json = json.dumps(_STATE["classes"])
        tile_template_js = json.dumps(TILE_TEMPLATE)

        html_template = """<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>SATERYS Training Sample Manager</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  :root { --bg:#0b0e11; --panel:#101418; --muted:#6b7280; --text:#e5e7eb; --accent:#60a5fa; --border:#1f2937; }
  * { box-sizing: border-box; }
  html, body { height:100%; margin:0; background:var(--bg); color:var(--text); font:14px/1.45 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  #map { position: absolute; inset: 0; }
  .topbar {
    position: absolute; top:12px; left:12px; right:12px;
    background:rgba(16,20,24,0.92); border:1px solid var(--border); border-radius:12px; backdrop-filter: blur(4px);
    display:flex; align-items:center; gap:12px; padding:10px 12px; z-index:1000; box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }
  .brand { font-weight:600; letter-spacing:.2px; color:#cbd5e1; margin-right:4px; }
  .sep { width:1px; height:24px; background:var(--border); margin:0 2px; }
  .palette { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .chip { display:flex; align-items:center; gap:8px; padding:6px 10px; border:1px solid var(--border); border-radius:999px; background:#0f1317; cursor:pointer; user-select:none; transition: transform .05s ease; }
  .chip:hover { transform: translateY(-1px); }
  .chip .sw { width:14px; height:14px; border-radius:999px; border:1px solid rgba(255,255,255,.5); }
  .chip .lbl { opacity:.95 }
  .chip .edit { margin-left:6px; opacity:.65; font-size:12px }
  .chip.active { outline:1.5px solid var(--accent); }
  .ctl { display:flex; align-items:center; gap:8px; }
  .btn { background:#111827; color:#e5e7eb; border:1px solid var(--border); border-radius:10px; padding:8px 12px; cursor:pointer; }
  .btn:hover { background:#0f172a; }
  .btn.primary { border-color:#3b82f6; }
  .slider { appearance:none; height:6px; border-radius:999px; background:#1f2937; outline:none; width:150px; }
  .slider::-webkit-slider-thumb { appearance:none; width:16px; height:16px; border-radius:999px; background:#93c5fd; border:1px solid #1f2937; }
  .legend { position:absolute; top:66px; left:12px; background:rgba(16,20,24,.92); border:1px solid var(--border); border-radius:12px; padding:10px 12px; z-index:900; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }
  .legend h4 { margin:4px 0 8px; color:#cbd5e1; font-size:13px; font-weight:600; }
  .legend .item { display:flex; align-items:center; gap:8px; margin:6px 0; color:#d1d5db; }
  .legend .sw { width:14px; height:14px; border-radius:3px; border:1px solid rgba(255,255,255,.5); }
  .status { position:absolute; bottom:12px; left:12px; background:rgba(16,20,24,0.92); border:1px solid var(--border); color:#cbd5e1; padding:6px 10px; border-radius:10px; z-index:900; font-size:12px; min-width:260px; }
  .kbd { padding:2px 6px; border:1px solid var(--border); border-radius:6px; background:#0b0f14; color:#cbd5e1; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; }
  .leaflet-control-attribution { background:rgba(16,20,24,.7); color:#9ca3af; }
  .crosshair { cursor: crosshair; }

  /* Attribute Table Panel */
  .table-panel {
    position: absolute; right:12px; bottom:12px; width: 480px; height: 42%;
    background:rgba(16,20,24,0.92); border:1px solid var(--border); border-radius:12px; z-index:950;
    display:flex; flex-direction:column; box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }
  .table-head { display:flex; gap:8px; align-items:center; padding:8px 10px; border-bottom:1px solid var(--border); }
  .table-head .title { font-weight:600; color:#cbd5e1; }
  .table-head input[type="text"] { flex:1; padding:6px 8px; border-radius:8px; border:1px solid var(--border); background:#0b0f14; color:#e5e7eb; }
  .table-head .small { font-size:12px; color:#9ca3af; }
  .table-head .actions { display:flex; gap:8px; }
  .table-body { flex:1; overflow:auto; }
  table { width:100%; border-collapse:collapse; font-size:12px; }
  thead th { position: sticky; top:0; background:#0f1317; border-bottom:1px solid var(--border); padding:6px 8px; text-align:left; cursor:pointer; }
  tbody td { border-bottom:1px solid #11161c; padding:6px 8px; }
  tbody tr:hover { background:#0f1317; }
  .td-actions button { margin-right:6px; }
  .chk { width:16px; height:16px; }

  /* modal */
  .modal-bg { position:fixed; inset:0; background:rgba(0,0,0,.35); display:none; align-items:center; justify-content:center; z-index:1200; }
  .modal { background:#0f1317; border:1px solid var(--border); border-radius:12px; padding:16px; width:320px; color:#e5e7eb; box-shadow: 0 10px 40px rgba(0,0,0,.5); }
  .modal h3 { margin:0 0 10px; font-size:16px; }
  .row { display:flex; align-items:center; gap:8px; margin:8px 0; }
  .row label { width:90px; color:#cbd5e1; font-size:13px; }
  .row input[type="text"], .row input[type="number"] {
    width:100%; padding:8px; border-radius:8px; border:1px solid var(--border); background:#0b0f14; color:#e5e7eb;
  }
  .row input[type="color"] { width:44px; height:28px; padding:0; border:none; background:none; }
  .modal .actions { display:flex; gap:8px; justify-content:flex-end; margin-top:12px; }
</style>
</head>
<body>
<div id="map"></div>

<div class="topbar" id="topbar">
  <div class="brand">SATERYS Training Sample Manager</div>
  <div class="sep"></div>
  <div class="palette" id="palette"></div>
  <button id="addClass" class="btn">+ Class</button>
  <div class="sep"></div>
  <div class="ctl">
    <span>Brush</span>
    <input id="brush" class="slider" type="range" min="1" max="31" step="2" value="{BRUSH}"/>
    <span id="brushv" class="kbd">{BRUSH}px</span>
  </div>
  <div class="sep"></div>
  <div class="ctl">
    <button id="toggleLabel" class="btn">✎ Label: Off</button>
    <button id="undo" class="btn">↶ Undo <span class="kbd">Z</span></button>
    <button id="save" class="btn primary">💾 Save <span class="kbd">S</span></button>
  </div>
</div>

<div class="legend" id="legend"><h4>Classes</h4><div id="legendItems"></div></div>
<div class="status" id="status">Class: none • Brush: {BRUSH}px • Lat: — Lon: — • Keys: <span class="kbd">L</span> toggle, <span class="kbd">0–9</span> class, <span class="kbd">[ / ]</span> brush, <span class="kbd">Z</span> undo, <span class="kbd">S</span> save</div>

<!-- Attribute Table Panel -->
<div class="table-panel">
  <div class="table-head">
    <div class="title">Attribute Table</div>
    <input id="search" type="text" placeholder="Search id / class / name / lon / lat"/>
    <div class="small" id="rowcount">0 rows</div>
    <div class="actions">
      <label class="small"><input id="unpaintChk" type="checkbox" class="chk"/> Unpaint on delete</label>
      <button id="delSel" class="btn">🗑 Delete</button>
      <button id="csvBtn" class="btn">⬇ CSV</button>
    </div>
  </div>
  <div class="table-body">
    <table>
      <thead>
        <tr>
          <th style="width:30px"><input id="selAll" type="checkbox" class="chk"/></th>
          <th data-k="id">ID</th>
          <th data-k="class_id">Class</th>
          <th data-k="class_name">Label</th>
          <th data-k="lon">Lon</th>
          <th data-k="lat">Lat</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>

<!-- Add/Edit Class Modal -->
<div class="modal-bg" id="modalBg">
  <div class="modal">
    <h3 id="modalTitle">New Class</h3>
    <div class="row"><label for="clsName">Name</label><input id="clsName" type="text" placeholder="e.g., Water"/></div>
    <div class="row"><label for="clsId">ID</label><input id="clsId" type="number" min="1" max="255" placeholder="(auto)"/></div>
    <div class="row"><label for="clsColor">Color</label><input id="clsColor" type="color" value="#33cc77"/></div>
    <div class="actions">
      <button id="clsCancel" class="btn">Cancel</button>
      <button id="clsSave" class="btn primary">Save</button>
    </div>
  </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
let CLASSES = {CLASSES_JSON};
const CLASS_COLORS = () => Object.fromEntries(CLASSES.map(c => [String(c.id), c.color || '#ffffff']));
let labeling = false;
let currentClass = (CLASSES[0] && CLASSES[0].id) || null;
let brush = {BRUSH};

// Map + basemaps
const imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {maxZoom: 19, attribution:'&copy; Esri'});
const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution:'&copy; OpenStreetMap'});
const map = L.map('map', { zoomControl: true, layers: [imagery] }).setView([0,0], 2);
const TILE_TEMPLATE = {TILE_TEMPLATE_JS};
let rasterOverlay = null;
if (TILE_TEMPLATE && TILE_TEMPLATE.length > 0) {
  rasterOverlay = L.tileLayer(TILE_TEMPLATE, {maxZoom: 22, opacity: 0.85}).addTo(map);
}
L.control.layers({"🛰️ Imagery": imagery, "🗺️ OSM Streets": osm}, rasterOverlay ? {"Source Raster": rasterOverlay} : {}).addTo(map);
L.control.scale({imperial:false}).addTo(map);

// UI Elements
const palette = document.getElementById('palette');
const legendItems = document.getElementById('legendItems');
const statusEl = document.getElementById('status');
const brushEl = document.getElementById('brush');
const brushvEl = document.getElementById('brushv');
const toggleEl = document.getElementById('toggleLabel');
const undoEl = document.getElementById('undo');
const saveEl = document.getElementById('save');
const addClassEl = document.getElementById('addClass');
const modalBg = document.getElementById('modalBg');
const modalTitle = document.getElementById('modalTitle');
const clsName = document.getElementById('clsName');
const clsId = document.getElementById('clsId');
const clsColor = document.getElementById('clsColor');
const clsCancel = document.getElementById('clsCancel');
const clsSave = document.getElementById('clsSave');

// Attribute table elements
const searchEl = document.getElementById('search');
const tbody = document.getElementById('tbody');
const rowcount = document.getElementById('rowcount');
const selAll = document.getElementById('selAll');
const delSel = document.getElementById('delSel');
const csvBtn = document.getElementById('csvBtn');
const unpaintChk = document.getElementById('unpaintChk');

let ROWS = [];
let sortKey = 'id';
let sortAsc = true;

function renderPalette() {
  palette.innerHTML = '';
  legendItems.innerHTML = '';
  CLASSES.forEach(c => {
    const chip = document.createElement('div');
    chip.className = 'chip' + (currentClass === c.id ? ' active' : '');
    chip.dataset.id = c.id;
    chip.innerHTML = `<div class="sw" style="background:${c.color || '#fff'}"></div><div class="lbl">(${c.id}) ${c.name || c.id}</div><div class="edit">✎</div>`;
    chip.onclick = (ev) => {
      if (ev.target && ev.target.classList.contains('edit')) {
        openClassModal('edit', c);
      } else {
        currentClass = c.id; syncUI();
      }
    };
    palette.appendChild(chip);

    const li = document.createElement('div');
    li.className = 'item';
    li.innerHTML = `<div class="sw" style="background:${c.color || '#fff'}"></div><div>${c.id} — ${c.name || ''}</div>`;
    legendItems.appendChild(li);
  });
}

async function fetchClasses() {
  try {
    const list = await fetch('/labeler/classes').then(r=>r.json());
    if (Array.isArray(list) && list.length) {
      const keep = currentClass;
      CLASSES = list.sort((a,b)=>a.id-b.id);
      currentClass = CLASSES.find(c=>c.id===keep) ? keep : (CLASSES[0]?.id ?? null);
      renderPalette(); syncUI(); renderTable(); refreshPoints();
    }
  } catch (e) {}
}

function syncUI() {
  [...palette.children].forEach(ch => ch.classList.toggle('active', String(ch.dataset.id) === String(currentClass)));
  brushvEl.textContent = `${brush}px`;
  toggleEl.textContent = labeling ? '✎ Label: On' : '✎ Label: Off';
  document.getElementById('map').classList.toggle('crosshair', labeling);
  setStatus();
}

function setStatus(lat=null, lon=null) {
  const latlon = (lat!==null && lon!==null) ? `Lat: ${lat.toFixed(5)} Lon: ${lon.toFixed(5)}` : 'Lat: — Lon: —';
  statusEl.innerHTML = `Class: ${currentClass ?? 'none'} • Brush: ${brush}px • ${latlon} • Keys: <span class="kbd">L</span> toggle, <span class="kbd">0–9</span> class, <span class="kbd">[ / ]</span> brush, <span class="kbd">Z</span> undo, <span class="kbd">S</span> save`;
}

brushEl.addEventListener('input', e => { brush = parseInt(e.target.value,10) || 1; syncUI(); });
toggleEl.addEventListener('click', () => { labeling = !labeling; syncUI(); });
undoEl.addEventListener('click', async () => { await fetch('/labeler/undo', {method:'POST'}); refreshPoints(); refreshTable(); });
saveEl.addEventListener('click', async () => {
  const j = await fetch('/labeler/save', {method:'POST'}).then(r=>r.json());
  alert(`Saved ${j.written} points to ${j.path}`);
});

map.on('mousemove', (e) => setStatus(e.latlng.lat, e.latlng.lng));
map.on('click', async (e) => {
  if (!labeling) return;
  if (currentClass === null) { alert('Pick a class first'); return; }
  await fetch('/labeler/click', { method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ lon: e.latlng.lng, lat: e.latlng.lat, cls: currentClass })
  });
  refreshPoints(); refreshTable();
});

// Keyboard shortcuts
window.addEventListener('keydown', async (ev) => {
  if (ev.key === 'l' || ev.key === 'L') { labeling = !labeling; syncUI(); }
  else if (ev.key >= '0' && ev.key <= '9') { currentClass = parseInt(ev.key, 10); syncUI(); }
  else if (ev.key === '[') { brush = Math.max(1, brush - 2); brushEl.value = brush; syncUI(); }
  else if (ev.key === ']') { brush = Math.min(31, brush + 2); brushEl.value = brush; syncUI(); }
  else if (ev.key.toLowerCase() === 'z') { await fetch('/labeler/undo', {method:'POST'}); refreshPoints(); refreshTable(); }
  else if (ev.key.toLowerCase() === 's') { const j = await fetch('/labeler/save', {method:'POST'}).then(r=>r.json()); alert(`Saved ${j.written} points to ${j.path}`); }
});

// POINTS (map)
const pointsLayer = L.geoJSON(null, {
  pointToLayer: (feat, latlng) => {
    const colors = CLASS_COLORS();
    const cid = String(feat.properties.class_id);
    return L.circleMarker(latlng, { radius: 4, weight: 1, opacity: 1,
      color: colors[cid] || '#ffffff', fillColor: colors[cid] || '#ffffff', fillOpacity: 0.9 });
  }
}).addTo(map);

async function refreshPoints() {
  try {
    const gj = await fetch('/labeler/points').then(r => r.json());
    pointsLayer.clearLayers(); pointsLayer.addData(gj);
  } catch (e) {}
}
setInterval(refreshPoints, 1200);

// ATTRIBUTE TABLE
async function refreshTable() {
  try {
    const data = await fetch('/labeler/points_table').then(r=>r.json());
    ROWS = Array.isArray(data) ? data : [];
    renderTable();
  } catch (e) {}
}
function renderTable() {
  const q = searchEl.value.trim().toLowerCase();
  let rows = ROWS.slice();
  if (q) {
    rows = rows.filter(r => (''+r.id).includes(q) || (''+r.class_id).includes(q) ||
                             (r.class_name||'').toLowerCase().includes(q) ||
                             (''+r.lon).includes(q) || (''+r.lat).includes(q));
  }
  rows.sort((a,b) => {
    const A = a[sortKey], B = b[sortKey];
    if (A < B) return sortAsc ? -1 : 1;
    if (A > B) return sortAsc ? 1 : -1;
    return 0;
  });
  tbody.innerHTML = rows.map(r => `
    <tr data-id="${r.id}">
      <td><input type="checkbox" class="chk rowchk"/></td>
      <td>${r.id}</td>
      <td>${r.class_id}</td>
      <td>${(r.class_name||'')}</td>
      <td>${r.lon.toFixed(6)}</td>
      <td>${r.lat.toFixed(6)}</td>
      <td class="td-actions">
        <button class="btn btn-sm" data-act="goto">🔎</button>
        <button class="btn btn-sm" data-act="edit">✎</button>
        <button class="btn btn-sm" data-act="del">🗑</button>
      </td>
    </tr>
  `).join('');
  rowcount.textContent = `${rows.length} rows`;
}
searchEl.addEventListener('input', renderTable);
document.querySelectorAll('thead th[data-k]').forEach(th => {
  th.addEventListener('click', () => {
    const k = th.getAttribute('data-k');
    if (sortKey === k) sortAsc = !sortAsc;
    else { sortKey = k; sortAsc = true; }
    renderTable();
  });
});
selAll.addEventListener('change', () => {
  document.querySelectorAll('#tbody .rowchk').forEach(cb => cb.checked = selAll.checked);
});
delSel.addEventListener('click', async () => {
  const ids = [...document.querySelectorAll('#tbody tr')].filter(tr => tr.querySelector('.rowchk')?.checked).map(tr => parseInt(tr.dataset.id,10));
  if (!ids.length) { alert('Select rows first'); return; }
  const unpaint = !!unpaintChk.checked;
  await fetch('/labeler/points/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ids, unpaint})});
  selAll.checked = false;
  refreshPoints(); refreshTable();
});
csvBtn.addEventListener('click', () => { window.open('/labeler/points.csv', '_blank'); });
tbody.addEventListener('click', async (e) => {
  const tr = e.target.closest('tr'); if (!tr) return;
  const id = parseInt(tr.dataset.id,10);
  const act = e.target.getAttribute('data-act');
  const row = ROWS.find(r => r.id === id); if (!row) return;
  if (act === 'goto') {
    map.setView([row.lat, row.lon], Math.max(14, map.getZoom()));
    const m = L.circleMarker([row.lat,row.lon], {radius:8, weight:2}).addTo(map);
    setTimeout(()=>map.removeLayer(m), 900);
  } else if (act === 'edit') {
    const choice = prompt(`Set class ID for row ${id} (1..255)`, String(row.class_id));
    if (choice === null) return;
    const cid = parseInt(choice,10);
    if (isNaN(cid) || cid < 1 || cid > 255) { alert('Invalid class id'); return; }
    await fetch('/labeler/points/update', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({id, class_id: cid})
    });
    refreshPoints(); refreshTable(); fetchClasses();
  } else if (act === 'del') {
    const unpaint = !!unpaintChk.checked;
    await fetch('/labeler/points/delete', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ids:[id], unpaint})
    });
    refreshPoints(); refreshTable();
  }
});

// Class modal
function openClassModal(mode='add', cls=null) {
  modalTitle.textContent = mode === 'add' ? 'New Class' : 'Edit Class';
  clsName.value = cls?.name || '';
  clsId.value = (mode==='edit' ? (cls?.id ?? '') : '');
  clsColor.value = cls?.color || '#33cc77';
  modalBg.style.display = 'flex';
  clsSave.onclick = async () => {
    const nameVal  = clsName.value.trim();
    const colorVal = clsColor.value;
    const idVal    = parseInt(clsId.value, 10);
    if (!nameVal) { alert('Please enter a name'); return; }

    if (mode === 'add') {
      const payload = { name: nameVal, color: colorVal };
      if (!Number.isNaN(idVal)) payload.id = idVal; // explicit id if provided
      await fetch('/labeler/classes/add', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
    } else {
      // EDIT: allow changing the ID — send new_id if user changed it
      const payload = { id: cls.id, name: nameVal, color: colorVal };
      if (!Number.isNaN(idVal) && idVal !== cls.id) payload.new_id = idVal;
      await fetch('/labeler/classes/update', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
    }

    modalBg.style.display = 'none';
    await fetchClasses();       // refresh palette/legend & colors
    await refreshPoints();      // points styling may change
    await refreshTable();       // class_id/name may change in table
  };
}
addClassEl.onclick = () => openClassModal('add');
clsCancel.onclick = () => { modalBg.style.display = 'none'; };

// Boot
renderPalette(); syncUI(); refreshPoints(); refreshTable(); fetchClasses();
</script>
</body>
</html>
"""
        html = (html_template
                .replace("{CLASSES_JSON}", classes_json)
                .replace("{BRUSH}", str(BRUSH))
                .replace("{TILE_TEMPLATE_JS}", tile_template_js))
        return HTMLResponse(html)

    # ======= API =======
    @app.get("/labeler/points")
    async def points():
        feats = []
        for p in _STATE["points"]:
            feats.append({
                "type":"Feature",
                "geometry":{"type":"Point","coordinates":[p["lon"], p["lat"]]},
                "properties":{"id": p["id"], "class_id": p["class"]}
            })
        return JSONResponse({"type":"FeatureCollection","features":feats})

    @app.get("/labeler/points_table")
    async def points_table():
        return JSONResponse(_rows(_STATE["points"], _STATE["classes"]))

    @app.get("/labeler/points.csv")
    async def points_csv():
        csv = _csv_text(_STATE["points"], _STATE["classes"])
        return PlainTextResponse(csv, media_type="text/csv")

    @app.post("/labeler/click")
    async def click(req: Request):
        body = await req.json()
        lon = float(body.get("lon")); lat = float(body.get("lat")); cls = int(body.get("cls"))
        _paint_pixels(input_path, class_raster_path, lon, lat, cls, BRUSH)
        pid = _STATE["next_pid"]; _STATE["next_pid"] += 1
        _STATE["points"].append({"id": pid, "lon": lon, "lat": lat, "class": cls})
        return JSONResponse({"ok": True, "id": pid})

    @app.post("/labeler/save")
    async def save():
        written, driver = _write_points(args["points_path"], "EPSG:4326", _STATE["points"], _STATE["classes"])
        return JSONResponse({"ok": True, "written": written, "path": args["points_path"], "driver": driver})

    @app.post("/labeler/undo")
    async def undo(req: Request):
        try:
            body = await req.json(); n = int(body.get("n", 1))
        except Exception:
            n = 1
        undone = _undo(class_raster_path, n=n)
        for _ in range(min(n, len(_STATE["points"]))):
            _STATE["points"].pop()
        return JSONResponse({"ok": True, "undone": undone})

    @app.get("/labeler/classes")
    async def get_classes():
        return JSONResponse(_STATE["classes"])

    @app.post("/labeler/classes/add")
    async def add_class(req: Request):
        body = await req.json()
        name = str(body.get("name","")).strip()
        if not name: return JSONResponse({"ok": False, "error":"name required"}, status_code=400)
        try: cid = int(body["id"]) if "id" in body and body["id"] is not None else None
        except Exception: cid = None
        color = str(body.get("color","")).strip() or _next_color(len(_STATE["classes"]))
        used = {int(c["id"]) for c in _STATE["classes"]}
        if cid is None or cid < 1 or cid > 255 or cid in used:
            cid = 1
            while cid in used and cid <= 255: cid += 1
            if cid > 255: return JSONResponse({"ok": False, "error":"no free class IDs"}, status_code=400)
        _STATE["classes"].append({"id": cid, "name": name, "color": color})
        _STATE["classes"] = _validate_classes(_STATE["classes"])
        _save_classes(args, _STATE["classes"])
        return JSONResponse({"ok": True, "classes": _STATE["classes"]})

    @app.post("/labeler/classes/update")
    async def update_class(req: Request):
        body = await req.json()
        try:
            old_id = int(body["id"])  # existing class id
        except Exception:
            return JSONResponse({"ok": False, "error": "id required"}, status_code=400)

        name  = body.get("name", None)
        color = body.get("color", None)

        # Optional ID change
        new_id = body.get("new_id", None)
        if new_id is not None:
            try:
                new_id = int(new_id)
            except Exception:
                return JSONResponse({"ok": False, "error": "new_id must be integer"}, status_code=400)
            if not (1 <= new_id <= 255):
                return JSONResponse({"ok": False, "error": "new_id out of range (1..255)"}, status_code=400)
            if any(int(c["id"]) == new_id for c in _STATE["classes"] if int(c["id"]) != old_id):
                return JSONResponse({"ok": False, "error": f"new_id {new_id} already in use"}, status_code=400)

            # 1) recode pixels in class raster: old_id -> new_id
            _recode_raster_values(class_raster_path, old_id, new_id)

            # 2) update points already labeled with old_id
            for p in _STATE["points"]:
                if int(p["class"]) == old_id:
                    p["class"] = new_id

            # 3) update the class entry's id
            found = False
            for c in _STATE["classes"]:
                if int(c["id"]) == old_id:
                    c["id"] = new_id
                    found = True
                    break
            if not found:
                return JSONResponse({"ok": False, "error": "id not found"}, status_code=404)

            # subsequent edits should target the new_id
            old_id = new_id

        # Apply name/color edits
        found = False
        for c in _STATE["classes"]:
            if int(c["id"]) == old_id:
                if name  is not None: c["name"]  = str(name)
                if color is not None: c["color"] = str(color)
                found = True
                break
        if not found:
            return JSONResponse({"ok": False, "error": "id not found"}, status_code=404)

        _STATE["classes"] = _validate_classes(_STATE["classes"])
        _save_classes(args, _STATE["classes"])
        return JSONResponse({"ok": True, "classes": _STATE["classes"]})

    @app.post("/labeler/classes/remove")
    async def remove_class(req: Request):
        body = await req.json()
        try: cid = int(body["id"])
        except Exception: return JSONResponse({"ok": False, "error":"id required"}, status_code=400)
        _STATE["classes"] = [c for c in _STATE["classes"] if int(c["id"]) != cid]
        if not _STATE["classes"]:
            _STATE["classes"] = _validate_classes([{"id":1,"name":"Class 1","color":"#EF4444"}])
        _save_classes(args, _STATE["classes"])
        return JSONResponse({"ok": True, "classes": _STATE["classes"]})

    @app.post("/labeler/points/update")
    async def update_point(req: Request):
        body = await req.json()
        try:
            pid = int(body["id"]); new_c = int(body["class_id"])
        except Exception:
            return JSONResponse({"ok": False, "error":"id and class_id required"}, status_code=400)
        for p in _STATE["points"]:
            if int(p["id"]) == pid:
                p["class"] = new_c
                _paint_pixels(input_path, class_raster_path, p["lon"], p["lat"], new_c, BRUSH)
                return JSONResponse({"ok": True})
        return JSONResponse({"ok": False, "error":"id not found"}, status_code=404)

    @app.post("/labeler/points/delete")
    async def delete_points(req: Request):
        body = await req.json()
        ids = body.get("ids") or []
        unpaint = bool(body.get("unpaint", False))
        keep = []
        deleted = 0
        for p in list(_STATE["points"]):
            if int(p["id"]) in ids:
                deleted += 1
                if unpaint:
                    _unpaint_pixels(input_path, class_raster_path, p["lon"], p["lat"], BRUSH)
            else:
                keep.append(p)
        _STATE["points"] = keep
        return JSONResponse({"ok": True, "deleted": deleted, "unpaint": unpaint})

    # start uvicorn in a background thread
    def _serve():
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        server.run()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()

    # wait until the server is up; optionally open browser
    url = f"http://{host}:{port}/labeler"
    if _wait_ready(url, timeout=6.0) and bool(args.get("open_browser", True)):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    _STATE["server_running"] = True
    _STATE["labeler_url"] = url
    _STATE["host"] = host
    _STATE["port"] = port

# ---------- node entry ----------

def run(args, inputs, context):
    # Deps: fastapi uvicorn rasterio pyproj shapely fiona
    input_path = args.get("input_path") or ""
    if not input_path:
        if isinstance(inputs, dict):
            for v in inputs.values():
                if isinstance(v, dict) and v.get("type")=="raster" and "path" in v:
                    input_path = v["path"]; break
                if isinstance(v, list):
                    for it in v:
                        if isinstance(it, dict) and it.get("type")=="raster" and "path" in it:
                            input_path = it["path"]; break
    if not input_path:
        raise ValueError("manual_labeler: set 'input_path' or connect a raster upstream.")

    class_raster_path = args.get("class_raster_path") or "./results/labels.tif"
    _ensure_class_raster(input_path, class_raster_path)

    import rasterio
    with rasterio.open(input_path) as src:
        crs_wkt = src.crs.to_string() if src.crs else "EPSG:4326"

    if not _STATE["server_running"]:
        _start_server(args, input_path, class_raster_path, crs_wkt)

    url = _STATE.get("labeler_url", f"http://{args.get('host','127.0.0.1')}:{args.get('port',8090)}/labeler")
    return [
        {"type":"raster", "path": class_raster_path, "bands":1, "operation":"manual_labels"},
        {"type":"info",   "message": f"Labeler at {url}"}
    ]
