# nodes/vector_create.py
"""
Create vector features (points, lines, polygons) programmatically.
Useful for testing and creating simple geometries.
"""

NAME = "vector.create"
DEFAULT_ARGS = {
    "type": "point",  # point, line, polygon
    "coordinates": [[0, 0]],  # format depends on type
    "properties": {},  # custom properties
    "name": "Feature 1"
}

def run(args, inputs, context):
    import json
    from shapely.geometry import Point, LineString, Polygon, mapping
    
    geom_type = str(args.get("type", "point")).lower()
    coords = args.get("coordinates", [[0, 0]])
    properties = args.get("properties", {})
    name = args.get("name", "Feature 1")
    
    # Add name to properties if not present
    if "name" not in properties:
        properties["name"] = name
    
    # Create geometry based on type
    try:
        if geom_type == "point":
            # coords should be [lon, lat] or [[lon, lat]]
            if isinstance(coords[0], list):
                coords = coords[0]
            geom = Point(coords)
        
        elif geom_type == "line" or geom_type == "linestring":
            # coords should be [[lon1, lat1], [lon2, lat2], ...]
            geom = LineString(coords)
        
        elif geom_type == "polygon":
            # coords should be [[lon1, lat1], [lon2, lat2], ..., [lon1, lat1]]
            # Must be closed (first point == last point)
            if coords[0] != coords[-1]:
                coords.append(coords[0])  # close the polygon
            geom = Polygon(coords)
        
        else:
            raise ValueError(f"Unsupported geometry type: {geom_type}")
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": properties
        }
        
        geojson = {
            "type": "FeatureCollection",
            "features": [feature]
        }
        
        # Calculate bounds
        bounds = geom.bounds  # (minx, miny, maxx, maxy)
        
        return {
            "type": "vector",
            "geojson": geojson,
            "feature_count": 1,
            "crs": "EPSG:4326",
            "bounds": list(bounds),
        }
    
    except Exception as e:
        raise ValueError(f"Failed to create {geom_type} geometry: {e}")
