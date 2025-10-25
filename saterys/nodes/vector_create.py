# nodes/vector_create.py
"""
Create vector features interactively or from coordinates.
Saves features to GeoJSON or Shapefile format.
"""

NAME = "vector.create"
DEFAULT_ARGS = {
    "output_path": "",  # if empty, auto-cache to ./data/cache/vector-<id>.geojson
    "geometry_type": "Polygon",  # Polygon, LineString, Point
    "output_format": "GeoJSON",  # GeoJSON or ESRI Shapefile
    "features": [],  # List of feature dicts with geometry and properties
    "crs": "EPSG:4326"
}

def run(args, inputs, context):
    import os
    import json
    import fiona
    from fiona.crs import from_epsg
    from shapely.geometry import shape, mapping
    
    # Get parameters
    output_path = (args.get("output_path") or "").strip()
    geom_type = str(args.get("geometry_type", "Polygon"))
    output_format = str(args.get("output_format", "GeoJSON"))
    features = args.get("features", [])
    crs_str = str(args.get("crs", "EPSG:4326"))
    
    # Generate output path if not provided
    if not output_path:
        cache_dir = os.path.abspath(os.getenv("RASTER_CACHE", "./data/cache"))
        os.makedirs(cache_dir, exist_ok=True)
        node_id = context.get("nodeId", "unknown")
        ext = ".geojson" if output_format == "GeoJSON" else ".shp"
        output_path = os.path.join(cache_dir, f"vector-{node_id}{ext}")
    else:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # If no features provided, check for upstream vector input
    if not features:
        vector_input = next(
            (inp for inp in inputs.values() if isinstance(inp, dict) and inp.get("type") == "vector"),
            None
        )
        if vector_input:
            # Copy features from upstream vector
            import fiona
            with fiona.open(vector_input["path"], 'r') as src:
                features = [dict(feat) for feat in src]
    
    if not features:
        # Create an empty feature collection
        features = []
    
    # Parse CRS
    if crs_str.startswith("EPSG:"):
        epsg_code = int(crs_str.split(":")[1])
        crs = from_epsg(epsg_code)
    else:
        crs = crs_str
    
    # Determine schema from first feature or use default
    if features and isinstance(features[0], dict):
        first_feature = features[0]
        if "properties" in first_feature:
            properties = first_feature["properties"]
            schema = {
                "geometry": geom_type,
                "properties": {k: type(v).__name__ for k, v in properties.items()}
            }
        else:
            schema = {"geometry": geom_type, "properties": {}}
    else:
        schema = {"geometry": geom_type, "properties": {}}
    
    # Write features to file
    driver = "GeoJSON" if output_format == "GeoJSON" else "ESRI Shapefile"
    
    with fiona.open(
        output_path,
        'w',
        driver=driver,
        crs=crs,
        schema=schema
    ) as dst:
        for feature in features:
            if isinstance(feature, dict):
                # Ensure feature has the right structure
                if "geometry" not in feature:
                    continue
                if "properties" not in feature:
                    feature["properties"] = {}
                dst.write(feature)
    
    # Return vector metadata
    with fiona.open(output_path, 'r') as src:
        try:
            bounds = src.bounds
        except:
            # If no features, use default bounds
            bounds = (0, 0, 0, 0)
        feature_count = len(src)
        
        return {
            "type": "vector",
            "path": os.path.abspath(output_path),
            "driver": driver,
            "crs": crs_str,
            "bounds": list(bounds),
            "feature_count": feature_count,
            "geometry_type": geom_type,
            "meta": {
                "source": "created",
                "node_id": context.get("nodeId", "unknown")
            }
        }
