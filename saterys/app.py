# saterys/app.py  (Python 3.7 compatible)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict  # IMPORTANT: Dict[...] for Py3.7
import importlib.util
import os
import sys
from .scheduling import pipeline_router, scheduler

# ------------------------------------------------------------------------------
# FastAPI app + CORS
# ------------------------------------------------------------------------------
app = FastAPI()

# Register the pipeline scheduling API
app.include_router(pipeline_router)

app.add_middleware(
    CORSMiddleware,
   allow_origins=["*"],            # or list specific origins if you prefer
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Plugin discovery — load BOTH package nodes AND ./nodes
# ------------------------------------------------------------------------------
PKG_NODE_DIR = os.path.join(os.path.dirname(__file__), "nodes")  # built-ins
CWD_NODE_DIR = os.path.join(os.getcwd(), "nodes")                # user workspace

PLUGINS: Dict[str, Any] = {}  # name -> module

def _load_dir(d: str):
    if not os.path.isdir(d):
        return
    for fn in os.listdir(d):
        if not fn.endswith(".py") or fn.startswith("__"):
            continue
        path = os.path.join(d, fn)
        spec = importlib.util.spec_from_file_location(fn[:-3], path)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[fn[:-3]] = mod
        spec.loader.exec_module(mod)
        name = getattr(mod, "NAME", fn[:-3])
        PLUGINS[name] = mod
        print(f"Loaded plugin: {name} from {path}")

def discover_plugins():
    PLUGINS.clear()
    _load_dir(PKG_NODE_DIR)  # package built-ins
    _load_dir(CWD_NODE_DIR)  # user ./nodes

discover_plugins()

# ------------------------------------------------------------------------------
# API models + endpoints
# ------------------------------------------------------------------------------
class RunPayload(BaseModel):
    nodeId: str
    type: str         # plugin name
    args: Dict[str, Any] = {}
    inputs: Dict[str, Any] = {}  # optional upstream data

@app.get("/node_types")
def node_types():
    out = []
    for name, mod in PLUGINS.items():
        out.append({
            "name": name,
            "default_args": getattr(mod, "DEFAULT_ARGS", {}),
        })
    return {"types": out}

@app.post("/run_node")
def run_node(p: RunPayload):
    mod = PLUGINS.get(p.type)
    if not mod:
        return {"ok": False, "error": "unknown node type '%s'" % p.type}
    try:
        res = mod.run(p.args or {}, p.inputs or {}, {"nodeId": p.nodeId})
        return {"ok": True, "output": res}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ------------------------------------------------------------------------------
# Raster preview endpoints (Leaflet tiles) — Py3.7 compatible
# Requires: pip install "rio-tiler<6" numpy
# ------------------------------------------------------------------------------
from typing import Dict as _Dict  # avoid confusion with above
import numpy as np

# rio-tiler compatibility: use Reader if available (v6+), else COGReader (v<6)
try:
    from rio_tiler.io import Reader as _RTReader   # rio-tiler >= 6 (needs Python >= 3.8)
except Exception:
    try:
        from rio_tiler.io import COGReader as _RTReader  # rio-tiler < 6 (Py3.7 OK)
    except Exception as _e:
        raise ImportError(
            "rio-tiler not available. Install a Py3.7-compatible version:\n"
            "  pip install 'rio-tiler<6' numpy"
        ) from _e

# Simple registry: preview id -> absolute path
PREVIEWS: _Dict[str, str] = {}

@app.post("/preview/register")
def preview_register(payload: Dict[str, str]):
    """
    Body: { "id": "myRaster1", "path": "/abs/path/to/file.tif" }
    """
    rid = str(payload.get("id", "")).strip()
    pth = str(payload.get("path", "")).strip()
    if not rid or not pth:
        raise HTTPException(400, "id and path are required")
    ap = os.path.abspath(pth)
    if not os.path.exists(ap):
        raise HTTPException(404, "file not found: %s" % ap)
    PREVIEWS[rid] = ap
    return {"ok": True, "id": rid, "path": ap}

@app.get("/preview/bounds/{rid}")
def preview_bounds(rid: str):
    path = PREVIEWS.get(rid)
    if not path:
        raise HTTPException(404, "unknown preview id")
    with _RTReader(path) as r:
        west, south, east, north = r.geographic_bounds  # lon/lat
    return {"bounds": [west, south, east, north], "crs": "EPSG:4326"}

@app.get("/preview/tile/{rid}/{z}/{x}/{y}.png")
def preview_tile(rid: str, z: int, x: int, y: int, indexes: str = ""):
    """
    Return a PNG tile for the registered raster.
    - ?indexes=4,3,2 chooses 1-based band indexes. If omitted: RGB if >=3 bands else band 1 grayscale.
    - Per-tile p2/p98 stretch to 0..255 for a decent look without dataset stats.
    """
    path = PREVIEWS.get(rid)
    if not path:
        raise HTTPException(404, "unknown preview id")

    # parse ?indexes
    idx = None
    if indexes:
        try:
            idx = tuple(int(i) for i in indexes.split(",") if i.strip())
        except Exception:
            raise HTTPException(400, "bad indexes param; expected comma-separated integers")

    with _RTReader(path) as r:
        # detect band count (compat across versions)
        band_count = getattr(getattr(r, "dataset", None), "count", None)
        if band_count is None:
            try:
                info = r.info()
                band_count = len(info.get("band_metadata", []))
            except Exception:
                band_count = 1
        if idx is None:
            idx = (1, 2, 3) if (band_count and band_count >= 3) else (1,)

        data, mask = r.tile(x, y, z, indexes=idx)  # data: (bands, H, W), mask: HxW

    # Per-band percentile stretch
    out_bands = []
    for b in range(data.shape[0]):
        arr = data[b].astype("float32")
        if mask is not None:
            valid = (mask != 0)  # treat 0 as nodata
            arr = np.where(valid, arr, np.nan)
        finite = np.isfinite(arr)
        if not np.any(finite):
            scaled = np.zeros_like(arr, dtype="uint8")
        else:
            vals = arr[finite]
            p2, p98 = np.percentile(vals, (2, 98))
            if not np.isfinite(p2) or not np.isfinite(p98) or (p98 <= p2):
                scaled = np.zeros_like(arr, dtype="uint8")
            else:
                scaledf = (arr - p2) / (p98 - p2) * 255.0
                scaled = np.clip(scaledf, 0, 255)
                scaled = np.where(finite, scaled, 0).astype("uint8")
        out_bands.append(scaled)

    data8 = np.stack(out_bands, axis=0)

    # Compose RGB
    if data8.shape[0] == 1:
        rgb = np.vstack([data8, data8, data8])
    elif data8.shape[0] >= 3:
        rgb = data8[:3]
    else:  # 2 bands -> duplicate last
        rgb = np.vstack([data8, data8[-1:]])

    # Encode PNG
    from rio_tiler.utils import render
    img = render(rgb, mask=mask, img_format="PNG")
    return Response(content=img, media_type="image/png")

# ------------------------------------------------------------------------------
# Vector data preview endpoints (GeoJSON, Shapefile, etc.)
# ------------------------------------------------------------------------------
import json

# Simple registry: vector id -> { "path": abs_path, "geojson": {...} }
VECTOR_PREVIEWS: _Dict[str, _Dict[str, Any]] = {}

@app.post("/preview/vector/register")
def vector_preview_register(payload: Dict[str, str]):
    """
    Register a vector file for preview.
    Body: { "id": "myVector1", "path": "/abs/path/to/file.shp|.geojson|.gpkg" }
    Converts to GeoJSON and stores for map preview.
    """
    vid = str(payload.get("id", "")).strip()
    pth = str(payload.get("path", "")).strip()
    if not vid or not pth:
        raise HTTPException(400, "id and path are required")
    ap = os.path.abspath(pth)
    if not os.path.exists(ap):
        raise HTTPException(404, f"file not found: {ap}")
    
    # Read vector file and convert to GeoJSON
    try:
        import fiona
        from shapely.geometry import shape, mapping
        import pyproj
        from pyproj import Transformer
        
        features = []
        source_crs = None
        
        with fiona.open(ap, 'r') as src:
            source_crs = src.crs
            for feature in src:
                geom = shape(feature['geometry'])
                props = feature.get('properties', {})
                
                # Transform to WGS84 if needed
                if source_crs and source_crs != 'EPSG:4326':
                    try:
                        # Create transformer from source CRS to WGS84
                        transformer = Transformer.from_crs(
                            source_crs,
                            'EPSG:4326',
                            always_xy=True
                        )
                        # Transform geometry
                        from shapely.ops import transform
                        geom = transform(transformer.transform, geom)
                    except Exception as e:
                        print(f"Warning: Could not transform geometry: {e}")
                
                features.append({
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": props
                })
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        VECTOR_PREVIEWS[vid] = {
            "path": ap,
            "geojson": geojson,
            "source_crs": str(source_crs) if source_crs else "EPSG:4326"
        }
        
        return {
            "ok": True,
            "id": vid,
            "path": ap,
            "feature_count": len(features),
            "source_crs": str(source_crs) if source_crs else "EPSG:4326"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error reading vector file: {str(e)}")

@app.get("/preview/vector/{vid}/geojson")
def vector_preview_geojson(vid: str):
    """
    Return the GeoJSON for a registered vector preview.
    """
    if vid not in VECTOR_PREVIEWS:
        raise HTTPException(404, "unknown vector preview id")
    
    return VECTOR_PREVIEWS[vid]["geojson"]

@app.get("/preview/vector/{vid}/bounds")
def vector_preview_bounds(vid: str):
    """
    Return the bounds [west, south, east, north] of a vector layer.
    """
    if vid not in VECTOR_PREVIEWS:
        raise HTTPException(404, "unknown vector preview id")
    
    geojson = VECTOR_PREVIEWS[vid]["geojson"]
    
    # Calculate bounds from all features
    from shapely.geometry import shape
    
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    
    for feature in geojson.get("features", []):
        try:
            geom = shape(feature["geometry"])
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            max_x = max(max_x, bounds[2])
            max_y = max(max_y, bounds[3])
        except:
            continue
    
    if min_x == float('inf'):
        # No valid geometries
        return {"bounds": [-180, -90, 180, 90], "crs": "EPSG:4326"}
    
    return {
        "bounds": [min_x, min_y, max_x, max_y],
        "crs": "EPSG:4326"
    }

# ------------------------------------------------------------------------------
# Serve built frontend (compiled Svelte) from saterys/static at "/"
# ------------------------------------------------------------------------------

_here = os.path.dirname(__file__)
static_dir = os.path.join(_here, "static")

if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # 👇 extra mount so /assets/* works when index.html uses absolute /assets URLs
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
def root():
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(404, "Frontend not built. Run: (cd saterys/web && npm install && npm run build)")
    return FileResponse(index_path)

# Start/stop the APScheduler with the app lifecycle
@app.on_event("startup")
async def _start_scheduler():
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
async def _stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)