# nodes/raster_input.py
"""
Exposes a local GeoTIFF (or any raster readable by rasterio) as a pipeline input.
"""

NAME = "raster.input"
DEFAULT_ARGS = {
    "path": "/absolute/path/to/file.tif"  # user sets this in the UI
}

def run(args, inputs, context):
    import os
    import rasterio
    from rasterio.coords import BoundingBox

    path = str(args.get("path", "")).strip()
    if not path:
        raise ValueError("raster.input: 'path' is required")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raster file not found: {path}")

    with rasterio.open(path) as ds:
        bb: BoundingBox = ds.bounds
        return {
            "type": "raster",
            "driver": ds.driver,
            "path": os.path.abspath(path),
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "dtype": ds.dtypes[0] if ds.count else None,
            "crs": str(ds.crs) if ds.crs else None,
            "transform": [ds.transform.a, ds.transform.b, ds.transform.c,
                          ds.transform.d, ds.transform.e, ds.transform.f],
            "bounds": [bb.left, bb.bottom, bb.right, bb.top],
            "nodata": ds.nodata,
            "band_names": ds.descriptions if ds.descriptions else None,
            "meta": {"source": "local"},
        }
