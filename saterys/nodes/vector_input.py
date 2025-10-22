# nodes/vector_input.py
"""
Load vector data (points, lines, polygons) from GeoJSON, Shapefile, or GPKG.
Exposes the geometry and properties for visualization and analysis.
"""

NAME = "vector.input"
DEFAULT_ARGS = {
    "path": "/absolute/path/to/file.geojson",  # or .shp, .gpkg
    "layer": None,  # optional layer name for multi-layer formats (GPKG)
}

def run(args, inputs, context):
    import os
    import json
    import fiona
    from shapely.geometry import shape, mapping
    from pyproj import Transformer, CRS

    path = str(args.get("path", "")).strip()
    layer_name = args.get("layer")
    
    if not path:
        raise ValueError("vector.input: 'path' is required")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vector file not found: {path}")

    # Open with Fiona
    open_kwargs = {}
    if layer_name:
        open_kwargs["layer"] = layer_name

    features = []
    src_crs = None
    bounds = None
    
    with fiona.open(path, **open_kwargs) as src:
        src_crs = src.crs
        bounds = src.bounds  # (minx, miny, maxx, maxy)
        
        # Convert to WGS84 (EPSG:4326) for Leaflet
        transformer = None
        if src_crs and CRS(src_crs) != CRS.from_epsg(4326):
            transformer = Transformer.from_crs(
                CRS(src_crs), 
                CRS.from_epsg(4326), 
                always_xy=True
            )
        
        for feature in src:
            geom = shape(feature["geometry"])
            props = feature.get("properties", {})
            
            # Transform geometry to WGS84 if needed
            if transformer:
                geom = _transform_geometry(geom, transformer)
            
            features.append({
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": props
            })
    
    # Transform bounds to WGS84 if needed
    if bounds and transformer:
        minx, miny = transformer.transform(bounds[0], bounds[1])
        maxx, maxy = transformer.transform(bounds[2], bounds[3])
        bounds = [minx, miny, maxx, maxy]
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {
        "type": "vector",
        "path": os.path.abspath(path),
        "geojson": geojson,
        "feature_count": len(features),
        "crs": "EPSG:4326",  # always output as WGS84
        "original_crs": str(src_crs) if src_crs else None,
        "bounds": bounds,
    }


def _transform_geometry(geom, transformer):
    """Transform a Shapely geometry using a pyproj Transformer."""
    from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
    from shapely.ops import transform as shapely_transform
    
    def transform_coords(x, y, z=None):
        return transformer.transform(x, y)
    
    return shapely_transform(transform_coords, geom)
