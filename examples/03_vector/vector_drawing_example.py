"""
Vector Data and Drawing Example for SATERYS

This example demonstrates:
1. Loading vector data (shapefile/GeoJSON)
2. Displaying vector layers on the map
3. Creating new vector features programmatically
4. Using the interactive drawing tools

Prerequisites:
- SATERYS installed and running
- Sample vector data (shapefile or GeoJSON)
"""

# Example 1: Load and display a shapefile
# =========================================
# In the SATERYS UI:
# 1. Add a "vector.input" node
# 2. Configure with your shapefile path:

vector_input_config = {
    "path": "/path/to/your/shapefile.shp"
}

# 3. Run the node
# 4. Click the eye icon (👁) to preview on the map
# Result: Vector features appear on the map with interactive popups


# Example 2: Create vector data programmatically
# ==============================================
# Add a "vector.create" node with this configuration:

vector_create_config = {
    "geometry_type": "Polygon",
    "output_format": "GeoJSON",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.5, 37.7],
                    [-122.5, 37.8],
                    [-122.4, 37.8],
                    [-122.4, 37.7],
                    [-122.5, 37.7]
                ]]
            },
            "properties": {
                "name": "Study Area 1",
                "area_type": "urban",
                "priority": "high"
            }
        }
    ]
}

# Run the node and preview to see your created features


# Example 3: Interactive drawing workflow
# ========================================
"""
Step-by-step guide for interactive drawing:

1. Enable Drawing Mode - Click "Draw" button in header
2. Draw Polygons - Click polygon tool, click points, double-click to finish
3. Draw Lines - Click polyline tool, click points, double-click to finish
4. Add Markers - Click marker tool, click on map to place
5. Edit Features - Click edit tool, drag vertices
6. Delete Features - Click delete tool, select features, confirm
7. Export Your Work - Click "Export" button to save as GeoJSON
8. Disable Drawing - Click "Draw" button again to hide toolbar
"""

print("Interactive drawing enabled - see steps above")


# Example 4: Elevation profile extraction
# =======================================
elevation_workflow = """
1. Add "raster.input" node with DEM file
2. Add "raster.elevation_profile" node
3. Configure profile with coordinates
4. Connect: raster.input → raster.elevation_profile
5. Run to get 3D elevation data
"""

print(elevation_workflow)
