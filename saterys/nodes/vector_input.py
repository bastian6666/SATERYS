# nodes/vector_input.py
"""
Read vector data (Shapefile, GeoJSON, GeoPackage) as a pipeline input.
Returns metadata about the vector layer for downstream processing.
"""

NAME = "vector.input"
DEFAULT_ARGS = {
    "path": "/absolute/path/to/file.shp"  # or .geojson, .gpkg
}

def run(args, inputs, context):
    import os
    import fiona
    from shapely.geometry import shape
    
    path = str(args.get("path", "")).strip()
    if not path:
        raise ValueError("vector.input: 'path' is required")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vector file not found: {path}")
    
    # Read vector file metadata
    with fiona.open(path, 'r') as src:
        # Get bounds
        bounds = src.bounds  # (minx, miny, maxx, maxy)
        
        # Count features
        feature_count = len(src)
        
        # Get CRS
        crs = str(src.crs) if src.crs else None
        
        # Get schema
        schema = src.schema
        
        # Get geometry type
        geom_type = schema.get('geometry', 'Unknown')
        
        # Sample first feature properties
        properties = {}
        if feature_count > 0:
            first_feature = next(iter(src))
            properties = list(first_feature.get('properties', {}).keys())
        
        return {
            "type": "vector",
            "path": os.path.abspath(path),
            "driver": src.driver,
            "crs": crs,
            "bounds": list(bounds),  # [minx, miny, maxx, maxy]
            "feature_count": feature_count,
            "geometry_type": geom_type,
            "properties": properties,
            "schema": schema,
            "meta": {
                "source": "local",
                "file_type": os.path.splitext(path)[1]
            }
        }
