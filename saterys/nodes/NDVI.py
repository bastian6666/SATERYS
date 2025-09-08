# nodes/ndvi.py
"""
NDVI node.
- If there are TWO upstream raster inputs: uses them as RED and NIR (you can hint which one via args.prefer_upstream_*).
- If there is ONE upstream raster input: reads specified band indices for red/nir.
- Saves NDVI as a GeoTIFF and returns a raster payload (path + metadata).

Requirements: rasterio, numpy
"""

from __future__ import annotations
import os, hashlib
from typing import Any, Dict, Tuple

NAME = "raster.ndvi"
DEFAULT_ARGS = {
    # When only one upstream raster is connected, read these band indices (1-based!)
    "red_band": 4,           # e.g. Landsat 8: B4 is red
    "nir_band": 5,           # Landsat 8: B5 is NIR
    # When TWO upstream rasters are connected, you can optionally hint which node id is which:
    "prefer_upstream_red_id": "",
    "prefer_upstream_nir_id": "",
    # Output
    "output_path": "",       # if empty, auto-cache to ./data/cache/ndvi-<hash>.tif
    "dtype": "float32",
    "nodata": -9999.0
}

def _cache_dir() -> str:
    return os.path.abspath(os.getenv("RASTER_CACHE", "./data/cache"))

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def _auto_name(paths: Tuple[str, ...], bands: Tuple[int, int]) -> str:
    h = hashlib.sha1(("|".join(paths) + f"|{bands}").encode("utf-8")).hexdigest()[:16]
    return f"ndvi-{h}.tif"

def _first_two_rasters(inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return a dict of {up_id: raster_payload} for the first two raster inputs found."""
    out = {}
    for up_id, v in inputs.items():
        if isinstance(v, dict) and v.get("type") == "raster" and v.get("path"):
            out[up_id] = v
            if len(out) == 2:
                break
    return out

def _assert_same_grid(r1, r2):
    if r1["crs"] != r2["crs"]:
        raise ValueError(f"NDVI: CRS mismatch: {r1['crs']} vs {r2['crs']}")
    if r1["transform"] != r2["transform"]:
        raise ValueError("NDVI: transform (georeferencing) mismatch between inputs")
    if r1["width"] != r2["width"] or r1["height"] != r2["height"]:
        raise ValueError("NDVI: raster shapes differ; please resample beforehand")

def run(args: Dict[str, Any], inputs: Dict[str, Any], context: Dict[str, Any]):
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling

    # 1) Gather upstream rasters
    rasters = _first_two_rasters(inputs)

    # 2) Resolve operating mode
    prefer_red = (args.get("prefer_upstream_red_id") or "").strip() or None
    prefer_nir = (args.get("prefer_upstream_nir_id") or "").strip() or None

    red_arr = None
    nir_arr = None
    meta_source = None  # template for writing output

    if len(rasters) >= 2:
        # --- Two-raster mode ---
        # Determine which is red and which is nir
        red_payload = None
        nir_payload = None

        # If preferences provided and present, honor them
        if prefer_red and prefer_red in rasters:
            red_payload = rasters[prefer_red]
        if prefer_nir and prefer_nir in rasters:
            nir_payload = rasters[prefer_nir]

        # If not both resolved, assign remaining by order
        remaining = [v for k, v in rasters.items() if v not in (red_payload, nir_payload)]
        if red_payload is None and remaining:
            red_payload = remaining.pop(0)
        if nir_payload is None and remaining:
            nir_payload = remaining.pop(0)

        if red_payload is None or nir_payload is None:
            raise ValueError("NDVI: need two upstream rasters or band indices")

        _assert_same_grid(red_payload, nir_payload)

        # Read first band from each file by default
        with rasterio.open(red_payload["path"]) as ds_red, rasterio.open(nir_payload["path"]) as ds_nir:
            red = ds_red.read(1, masked=True).astype("float32")
            nir = ds_nir.read(1, masked=True).astype("float32")
            meta_source = ds_red  # use RED for profile

            # Prefer nodata masks from both
            mask = red.mask | nir.mask
            red_arr = np.ma.array(red, mask=mask)
            nir_arr = np.ma.array(nir, mask=mask)

        out_name_paths = (red_payload["path"], nir_payload["path"])
        bands_used = (1, 1)

    else:
        # --- Single multiband mode ---
        # Find a single upstream raster
        raster = next((v for v in inputs.values() if isinstance(v, dict) and v.get("type") == "raster"), None)
        if raster is None:
            raise ValueError("NDVI: no upstream raster found")

        red_band = int(args.get("red_band", 4))
        nir_band = int(args.get("nir_band", 5))
        if red_band < 1 or nir_band < 1:
            raise ValueError("NDVI: band indices are 1-based and must be >= 1")

        with rasterio.open(raster["path"]) as ds:
            if red_band > ds.count or nir_band > ds.count:
                raise ValueError(f"NDVI: band index out of range (count={ds.count})")
            red = ds.read(red_band, masked=True).astype("float32")
            nir = ds.read(nir_band, masked=True).astype("float32")
            meta_source = ds
            mask = red.mask | nir.mask
            red_arr = np.ma.array(red, mask=mask)
            nir_arr = np.ma.array(nir, mask=mask)

        out_name_paths = (raster["path"],)
        bands_used = (red_band, nir_band)

    # 3) Compute NDVI = (NIR - RED) / (NIR + RED)
    #    Handle divide-by-zero and propagate masks.
    num = (nir_arr - red_arr)
    den = (nir_arr + red_arr)
    # Avoid runtime warnings; where den == 0, set masked
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = np.ma.divide(num, den)
        ndvi.mask = np.ma.getmaskarray(ndvi) | (den == 0)

    out_dtype = str(args.get("dtype", "float32")).lower()
    if out_dtype not in ("float32", "float64"):
        out_dtype = "float32"
    nodata_val = float(args.get("nodata", -9999.0))

    # 4) Prepare output path
    out_path = (args.get("output_path") or "").strip()
    if not out_path:
        cache_root = _cache_dir()
        _ensure_dir(cache_root)
        out_path = os.path.join(cache_root, _auto_name(out_name_paths, bands_used))
    else:
        _ensure_dir(os.path.dirname(os.path.abspath(out_path)))

    # 5) Write GeoTIFF
    with rasterio.open(out_path, "w",
                       driver="GTiff",
                       height=ndvi.shape[0],
                       width=ndvi.shape[1],
                       count=1,
                       dtype=out_dtype,
                       crs=meta_source.crs,
                       transform=meta_source.transform,
                       nodata=nodata_val) as dst:
        # Fill masked pixels with nodata
        out = ndvi.filled(nodata_val).astype(out_dtype)
        dst.write(out, 1)
        # Optional description
        dst.set_band_description(1, "NDVI")

    # 6) Return a raster payload for downstream nodes
    from rasterio.coords import BoundingBox
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
            "band_names": ["NDVI"],
            "meta": {
                "source": "ndvi",
                "mode": "two_rasters" if len(rasters) >= 2 else "multiband",
                "inputs": list(out_name_paths),
                "bands_used": {"red": bands_used[0], "nir": bands_used[1]},
            },
        }

    return payload
