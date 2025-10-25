"""
Vector Data Drawing and Export Demo for SATERYS

This example demonstrates the vector data capabilities:
1. Drawing vector features (points, lines, polygons) on the map
2. Saving vector data to the backend
3. Exporting vector data to shapefile format
4. Loading and visualizing vector layers

Usage:
1. Start SATERYS: saterys
2. Open the web interface at http://localhost:8000
3. Use the drawing tools in the map to create features
4. Click "Load Vectors" to display the drawn features
5. Click "Export Shapefile" to download as a ZIP file
"""

# Note: This demo uses FastAPI TestClient for programmatic API access.
# In production, you would use requests library or similar HTTP client.
from fastapi.testclient import TestClient
from saterys.app import app

def create_sample_vectors():
    """Create sample vector data programmatically"""
    
    client = TestClient(app)
    
    # Example 1: Points of Interest
    poi_geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-122.4194, 37.7749]
                },
                'properties': {
                    'name': 'San Francisco City Hall',
                    'type': 'Government',
                    'year_built': 1915
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-122.4183, 37.8199]
                },
                'properties': {
                    'name': 'Golden Gate Bridge',
                    'type': 'Landmark',
                    'year_built': 1937
                }
            }
        ]
    }
    
    response = client.post('/vector/register', 
                          json={'id': 'sf_poi', 'geojson': poi_geojson})
    print('POI registered:', response.json())
    
    # Example 2: Polygon (Study Area)
    study_area = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    [-122.5, 37.7],
                    [-122.3, 37.7],
                    [-122.3, 37.9],
                    [-122.5, 37.9],
                    [-122.5, 37.7]
                ]]
            },
            'properties': {
                'name': 'Study Area 1',
                'area_km2': 125.5,
                'status': 'active'
            }
        }]
    }
    
    response = client.post('/vector/register',
                          json={'id': 'study_areas', 'geojson': study_area})
    print('Study area registered:', response.json())
    
    # Example 3: LineString (Route)
    route = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [-122.4194, 37.7749],
                    [-122.4183, 37.8199],
                    [-122.4783, 37.8199]
                ]
            },
            'properties': {
                'name': 'Scenic Route',
                'length_km': 12.5,
                'surface': 'paved'
            }
        }]
    }
    
    response = client.post('/vector/register',
                          json={'id': 'routes', 'geojson': route})
    print('Route registered:', response.json())
    
    # List all registered vectors
    response = client.get('/vector/list')
    print('\nAll registered vectors:', response.json())
    
    # Export one to shapefile
    response = client.post('/vector/export_shapefile/sf_poi')
    if response.status_code == 200:
        # Save to file
        with open('sf_poi.zip', 'wb') as f:
            f.write(response.content)
        print('\nShapefile exported to sf_poi.zip')
    
if __name__ == '__main__':
    print('Creating sample vector data...\n')
    create_sample_vectors()
    print('\n✅ Sample vectors created!')
    print('\nTo visualize:')
    print('1. Start SATERYS: saterys')
    print('2. Open http://localhost:8000')
    print('3. Click "Load Vectors" button to see the data')
    print('4. Use drawing tools to create more features')
    print('5. Click "Export Shapefile" to download')
