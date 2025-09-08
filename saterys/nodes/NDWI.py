# nodes/ndwi.py
"""
NDWI node (McFeeters 1996): NDWI = (Green - NIR) / (Green + NIR)

- Modes:
  1) Two upstream single-band rasters (same grid): use them as GREEN and NIR
     (you can hint which is which via args.prefer_upstream_*).
  2) One upstream multiband raster: read GREEN/NIR band indices.

- Output: writes NDWI GeoTIFF and returns a raster payload (path + metadata)
  compatible with your NDVI node’s structure.

Requirements: rasterio, numpy
"""

from __future__ import annotations
import os, hashlib
from typing import Any, Dict, Tuple

NAME = "raster.ndwi"
DEFAULT_ARGS = {
    # When only one upstream raster is connected, read these band indices (1-based!)
    "green_band": 3,         # Landsat 8/9: B3 is green
    "nir_band": 5,           # Landsat 8/9: B5 is NIR

    # When TWO upstream rasters are connected, you can hint which node id is which:
    "prefer_upstream_green_id": "",
    "prefer_upstream_nir_id": "",

    # Output
    "output_path": "",       # if empty, auto-cache to ./data/cache/ndwi-<hash>.tif
    "dtype": "float32",
    "nodata": -9999.0
}

def _cache_dir() -> str:
    return os.path.abspath(os.getenv("RASTER_CACHE", "./data/cache"))

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def _auto_name(paths: Tuple[str, ...], bands: Tuple[int, int]) -> str:
    h = hashlib.sha1(("|".join(paths) + f"|{bands}").encode("utf-8")).hexdigest()[:16]
    return f"ndwi-{h}.tif"

def _first_two_rasters(inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return {up_id: raster_payload} for the first two raster inputs found."""
    out = {}
    for up_id, v in inputs.items():
        if isinstance(v, dict) and v.get("type") == "raster" and v.get("path"):
            out[up_id] = v
            if len(out) == 2:
                break
    return out

def _assert_same_grid(r1, r2):
    if r1["crs"] != r2["crs"]:
        raise ValueError(f"NDWI: CRS mismatch: {r1['crs']} vs {r2['crs']}")
    if r1["transform"] != r2["transform"]:
        raise ValueError("NDWI: transform (georeferencing) mismatch between inputs")
    if r1["width"] != r2["width"] or r1["height"] != r2["height"]:
        raise ValueError("NDWI: raster shapes differ; please resample beforehand")

def run(args: Dict[str, Any], inputs: Dict[str, Any], context: Dict[str, Any]):
    import numpy as np
    import rasterio

    # 1) Gather upstream rasters
    rasters = _first_two_rasters(inputs)

    # 2) Resolve operating mode
    prefer_g = (args.get("prefer_upstream_green_id") or "").strip() or None
    prefer_n = (args.get("prefer_upstream_nir_id") or "").strip() or None

    green_arr = None
    nir_arr = None
    meta_source = None  # template for writing output

    if len(rasters) >= 2:
        # --- Two-raster mode ---
        # Determine which is green and which is nir
        green_payload = None
        nir_payload = None

        if prefer_g and prefer_g in rasters:
            green_payload = rasters[prefer_g]
        if prefer_n and prefer_n in rasters:
            nir_payload = rasters[prefer_n]

        remaining = [v for k, v in rasters.items() if v not in (green_payload, nir_payload)]
        if green_payload is None and remaining:
            green_payload = remaining.pop(0)
        if nir_payload is None and remaining:
            nir_payload = remaining.pop(0)

        if green_payload is None or nir_payload is None:
            raise ValueError("NDWI: need two upstream rasters or band indices")

        _assert_same_grid(green_payload, nir_payload)

        with rasterio.open(green_payload["path"]) as dsg, rasterio.open(nir_payload["path"]) as dsn:
            g = dsg.read(1, masked=True).astype("float32")
            n = dsn.read(1, masked=True).astype("float32")
            meta_source = dsg
            mask = g.mask | n.mask
            green_arr = np.ma.array(g, mask=mask)
            nir_arr   = np.ma.array(n, mask=mask)

        bands_used = (1, 1)
        name_inputs = (green_payload["path"], nir_payload["path"])

    else:
        # --- Single multiband mode ---
        raster = next((v for v in inputs.values() if isinstance(v, dict) and v.get("type") == "raster"), None)
        if raster is None:
            raise ValueError("NDWI: no upstream raster found")

        g_idx = int(args.get("green_band", 3))
        n_idx = int(args.get("nir_band", 5))
        if g_idx < 1 or n_idx < 1:
            raise ValueError("NDWI: band indices are 1-based and must be >= 1")

        with rasterio.open(raster["path"]) as ds:
            if g_idx > ds.count or n_idx > ds.count:
                raise ValueError(f"NDWI: band index out of range (count={ds.count})")
            g = ds.read(g_idx, masked=True).astype("float32")
            n = ds.read(n_idx, masked=True).astype("float32")
            meta_source = ds
            mask = g.mask | n.mask
            green_arr = np.ma.array(g, mask=mask)
            nir_arr   = np.ma.array(n, mask=mask)

        bands_used = (g_idx, n_idx)
        name_inputs = (raster["path"],)

    # 3) Compute NDWI = (G - NIR) / (G + NIR), mask div-by-zero
    with np.errstate(divide="ignore", invalid="ignore"):
        num = (green_arr - nir_arr)
        den = (green_arr + nir_arr)
        ndwi = np.ma.divide(num, den)
        ndwi.mask = np.ma.getmaskarray(ndwi) | (den == 0)

    out_dtype = str(args.get("dtype", "float32")).lower()
    if out_dtype not in ("float32", "float64"):
        out_dtype = "float32"
    nodata_val = float(args.get("nodata", -9999.0))

    # 4) Prepare output path
    out_path = (args.get("output_path") or "").strip()
    if not out_path:
        cache_root = _cache_dir()
        _ensure_dir(cache_root)
        out_path = os.path.join(cache_root, _auto_name(name_inputs, bands_used))
    else:
        _ensure_dir(os.path.dirname(os.path.abspath(out_path)))

    # 5) Write GeoTIFF
    with rasterio.open(out_path, "w",
                       driver="GTiff",
                       height=ndwi.shape[0],
                       width=ndwi.shape[1],
                       count=1,
                       dtype=out_dtype,
                       crs=meta_source.crs,
                       transform=meta_source.transform,
                       nodata=nodata_val) as dst:
        dst.write(ndwi.filled(nodata_val).astype(out_dtype), 1)
        dst.set_band_description(1, "NDWI")

    # 6) Return a raster payload (mirrors NDVI node)
    with rasterio.open(out_path) as ds:
        bb = ds.bounds
        payload = {
            "type": "raster",
            "driver": ds.driver,
            "path": os.path.abspath(out_path),
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "dtype": ds.dtypes[0],
            "crs": str(ds.crs) if ds.crs else None,
            "transform": [ds.transform.a, ds.transform.b, ds.transform.c,
                          ds.transform.d, ds.transform.e, ds.transform.f],
            "bounds": [bb.left, bb.bottom, bb.right, bb.top],
            "nodata": ds.nodata,
            "band_names": ["NDWI"],
            "meta": {
                "source": "ndwi",
                "mode": "two_rasters" if len(rasters) >= 2 else "multiband",
                "inputs": list(name_inputs),
                "bands_used": {"green": bands_used[0], "nir": bands_used[1]},
            },
        }

    return payload
