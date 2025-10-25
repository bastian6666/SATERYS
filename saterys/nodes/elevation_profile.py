# nodes/elevation_profile.py
"""
Generate elevation profile from a DEM (Digital Elevation Model) raster.
Creates a 3D-ready dataset with elevation values along a line or within a polygon.
"""

NAME = "raster.elevation_profile"
DEFAULT_ARGS = {
    "dem_path": "",  # Path to DEM raster file
    "profile_type": "line",  # "line" or "polygon"
    "coordinates": [],  # List of [lon, lat] coordinates for line/polygon
    "output_path": "",  # Output path for profile data (GeoJSON with z-values)
    "sample_distance": 100  # Distance between samples in meters (for line profiles)
}

def run(args, inputs, context):
    import os
    import json
    import rasterio
    from rasterio.transform import rowcol
    import numpy as np
    from shapely.geometry import LineString, Point, mapping
    import pyproj
    from pyproj import Transformer
    
    # Get parameters
    dem_path = str(args.get("dem_path", "")).strip()
    profile_type = str(args.get("profile_type", "line"))
    coordinates = args.get("coordinates", [])
    output_path = (args.get("output_path") or "").strip()
    sample_distance = float(args.get("sample_distance", 100))
    
    # Try to get DEM from upstream raster input if not provided
    if not dem_path:
        raster_input = next(
            (inp for inp in inputs.values() if isinstance(inp, dict) and inp.get("type") == "raster"),
            None
        )
        if raster_input:
            dem_path = raster_input["path"]
    
    if not dem_path or not os.path.exists(dem_path):
        raise ValueError("elevation_profile: DEM path is required and must exist")
    
    if not coordinates or len(coordinates) < 2:
        raise ValueError("elevation_profile: At least 2 coordinates are required")
    
    # Generate output path if not provided
    if not output_path:
        cache_dir = os.path.abspath(os.getenv("RASTER_CACHE", "./data/cache"))
        os.makedirs(cache_dir, exist_ok=True)
        node_id = context.get("nodeId", "unknown")
        output_path = os.path.join(cache_dir, f"elevation_profile-{node_id}.geojson")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Read DEM
    with rasterio.open(dem_path) as src:
        dem_crs = src.crs
        dem_transform = src.transform
        dem_data = src.read(1)
        
        # Create transformer from WGS84 to DEM CRS if needed
        transformer = None
        if dem_crs and str(dem_crs) != "EPSG:4326":
            transformer = Transformer.from_crs(
                "EPSG:4326",
                dem_crs,
                always_xy=True
            )
        
        # Extract elevation values along the profile
        profile_points = []
        
        if profile_type == "line":
            # Create line and sample at regular intervals
            line_coords = coordinates
            
            # Transform coordinates to DEM CRS if needed
            if transformer:
                line_coords = [transformer.transform(lon, lat) for lon, lat in coordinates]
            
            # Create line geometry
            line = LineString(line_coords)
            
            # Sample along the line
            distance = 0
            while distance <= line.length:
                point = line.interpolate(distance)
                x, y = point.x, point.y
                
                # Get elevation value
                try:
                    row, col = rowcol(dem_transform, x, y)
                    if 0 <= row < dem_data.shape[0] and 0 <= col < dem_data.shape[1]:
                        elevation = float(dem_data[row, col])
                        
                        # Transform back to WGS84 if needed
                        if transformer:
                            rev_transformer = Transformer.from_crs(
                                dem_crs,
                                "EPSG:4326",
                                always_xy=True
                            )
                            lon, lat = rev_transformer.transform(x, y)
                        else:
                            lon, lat = x, y
                        
                        profile_points.append({
                            "lon": lon,
                            "lat": lat,
                            "elevation": elevation,
                            "distance": distance
                        })
                except:
                    pass
                
                distance += sample_distance
        
        elif profile_type == "polygon":
            # Sample all points within the polygon
            # For now, just sample the boundary
            for lon, lat in coordinates:
                x, y = lon, lat
                if transformer:
                    x, y = transformer.transform(lon, lat)
                
                try:
                    row, col = rowcol(dem_transform, x, y)
                    if 0 <= row < dem_data.shape[0] and 0 <= col < dem_data.shape[1]:
                        elevation = float(dem_data[row, col])
                        profile_points.append({
                            "lon": lon,
                            "lat": lat,
                            "elevation": elevation,
                            "distance": 0
                        })
                except:
                    pass
    
    # Create GeoJSON with elevation data
    features = []
    for i, pt in enumerate(profile_points):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [pt["lon"], pt["lat"], pt["elevation"]]
            },
            "properties": {
                "elevation": pt["elevation"],
                "distance": pt["distance"],
                "index": i
            }
        })
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    # Calculate statistics
    elevations = [pt["elevation"] for pt in profile_points]
    min_elev = min(elevations) if elevations else 0
    max_elev = max(elevations) if elevations else 0
    avg_elev = sum(elevations) / len(elevations) if elevations else 0
    
    return {
        "type": "elevation_profile",
        "path": os.path.abspath(output_path),
        "profile_type": profile_type,
        "point_count": len(profile_points),
        "elevation_stats": {
            "min": min_elev,
            "max": max_elev,
            "average": avg_elev,
            "range": max_elev - min_elev
        },
        "meta": {
            "source": "dem",
            "dem_path": dem_path,
            "sample_distance": sample_distance
        }
    }
