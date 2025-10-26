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
from .server.plugins import plugin_router
from .server.bootstrap import load_plugins, CoreBridge

# ------------------------------------------------------------------------------
# FastAPI app + CORS
# ------------------------------------------------------------------------------
app = FastAPI()

# Load plugins FIRST (before including the plugin_router)
def _init_plugins():
    """Initialize plugins on app creation"""
    try:
        from .auth import require_jwt
    except Exception:
        def require_jwt():
            """Stub authentication - returns no-op dependency"""
            def _noop(): 
                return None
            return _noop
    
    core = CoreBridge(plugin_router, require_jwt())
    load_plugins(core)

_init_plugins()

# NOW include routers after plugins have registered their sub-routers
app.include_router(pipeline_router)
app.include_router(plugin_router)

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
# Vector data endpoints (shapefile <-> GeoJSON conversion)
# ------------------------------------------------------------------------------
import json
import tempfile
import zipfile
from fastapi import UploadFile, File

try:
    import fiona
    from shapely.geometry import shape, mapping
    FIONA_AVAILABLE = True
except ImportError:
    FIONA_AVAILABLE = False

@app.post("/vector/upload")
async def upload_shapefile(file: UploadFile = File(...)):
    """
    Upload a shapefile (as a zip containing .shp, .shx, .dbf, .prj) and convert to GeoJSON.
    Returns GeoJSON FeatureCollection.
    """
    if not FIONA_AVAILABLE:
        raise HTTPException(500, "fiona not installed - cannot process shapefiles")
    
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(400, "Please upload a .zip file containing shapefile components")
    
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
        content = await file.read()
        tmp_zip.write(content)
        tmp_zip_path = tmp_zip.name
    
    try:
        # Extract zip to temp directory (with security check for zip slip)
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            # Validate all paths in the zip to prevent zip slip
            for member in zip_ref.namelist():
                member_path = os.path.join(extract_dir, member)
                if not member_path.startswith(extract_dir):
                    raise HTTPException(400, "Invalid zip file - contains unsafe paths")
            zip_ref.extractall(extract_dir)
        
        # Find the .shp file
        shp_file = None
        for fname in os.listdir(extract_dir):
            if fname.endswith('.shp'):
                shp_file = os.path.join(extract_dir, fname)
                break
        
        if not shp_file:
            raise HTTPException(400, "No .shp file found in the zip")
        
        # Read shapefile and convert to GeoJSON
        features = []
        with fiona.open(shp_file, 'r') as src:
            for feature in src:
                geojson_feature = {
                    "type": "Feature",
                    "geometry": feature['geometry'],
                    "properties": feature.get('properties', {})
                }
                features.append(geojson_feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Cleanup
        import shutil
        shutil.rmtree(extract_dir, ignore_errors=True)
        os.unlink(tmp_zip_path)
        
        return geojson
        
    except Exception as e:
        raise HTTPException(500, f"Failed to process shapefile: {str(e)}")

@app.post("/vector/save")
async def save_geojson_as_shapefile(payload: Dict[str, Any]):
    """
    Convert GeoJSON FeatureCollection to shapefile and return as downloadable zip.
    Body: { "geojson": {...}, "filename": "output" }
    """
    if not FIONA_AVAILABLE:
        raise HTTPException(500, "fiona not installed - cannot create shapefiles")
    
    geojson = payload.get('geojson')
    filename = payload.get('filename', 'vector_data')
    
    if not geojson or geojson.get('type') != 'FeatureCollection':
        raise HTTPException(400, "Invalid GeoJSON FeatureCollection")
    
    features = geojson.get('features', [])
    if not features:
        raise HTTPException(400, "No features to save")
    
    try:
        # Create temp directory for shapefile components
        temp_dir = tempfile.mkdtemp()
        shp_path = os.path.join(temp_dir, f"{filename}.shp")
        
        # Determine geometry type from first feature
        first_geom = features[0]['geometry']
        geom_type = first_geom['type']
        
        # Map GeoJSON geometry types to Fiona schema types
        fiona_geom_map = {
            'Point': 'Point',
            'LineString': 'LineString',
            'Polygon': 'Polygon',
            'MultiPoint': 'MultiPoint',
            'MultiLineString': 'MultiLineString',
            'MultiPolygon': 'MultiPolygon'
        }
        
        schema_geom = fiona_geom_map.get(geom_type, 'Polygon')
        
        # Build properties schema from first feature
        properties = features[0].get('properties', {})
        schema_props = {}
        for key, value in properties.items():
            if isinstance(value, str):
                schema_props[key] = 'str'
            elif isinstance(value, int):
                schema_props[key] = 'int'
            elif isinstance(value, float):
                schema_props[key] = 'float'
            else:
                schema_props[key] = 'str'
        
        schema = {
            'geometry': schema_geom,
            'properties': schema_props
        }
        
        # Write shapefile
        with fiona.open(shp_path, 'w', driver='ESRI Shapefile', 
                       crs='EPSG:4326', schema=schema) as dst:
            for feature in features:
                dst.write({
                    'geometry': feature['geometry'],
                    'properties': feature.get('properties', {})
                })
        
        # Create zip file with all shapefile components
        zip_path = os.path.join(temp_dir, f"{filename}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for fname in os.listdir(temp_dir):
                if fname != f"{filename}.zip":
                    file_path = os.path.join(temp_dir, fname)
                    zipf.write(file_path, arcname=fname)
        
        # Read zip file content
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return Response(
            content=zip_content,
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}.zip"'
            }
        )
        
    except Exception as e:
        raise HTTPException(500, f"Failed to create shapefile: {str(e)}")

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