#!/usr/bin/env python3
"""
Integration test for SATERYS vector visualization features

Tests:
1. Vector data registration (points, lines, polygons)
2. Vector data retrieval
3. Shapefile export
4. Drawing feature save
5. Vector list
"""

from fastapi.testclient import TestClient
from saterys.app import app
import json
import zipfile
import io

def test_vector_features():
    """Run comprehensive tests for vector features"""
    
    print("🧪 Running SATERYS Vector Feature Integration Tests\n")
    client = TestClient(app)
    
    # Test 1: Register Point Vector
    print("Test 1: Register Point Vector...")
    point_geojson = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [-122.4, 37.8]
            },
            'properties': {
                'name': 'Test Point',
                'category': 'test'
            }
        }]
    }
    
    response = client.post('/vector/register', json={'id': 'test_points', 'geojson': point_geojson})
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    assert data['ok'] == True
    assert data['featureCount'] == 1
    print("✅ Point registration successful\n")
    
    # Test 2: Register Polygon Vector
    print("Test 2: Register Polygon Vector...")
    polygon_geojson = {
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
                'name': 'Study Area',
                'area': 100.5
            }
        }]
    }
    
    response = client.post('/vector/register', json={'id': 'test_polygons', 'geojson': polygon_geojson})
    assert response.status_code == 200
    print("✅ Polygon registration successful\n")
    
    # Test 3: Register LineString Vector
    print("Test 3: Register LineString Vector...")
    line_geojson = {
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [-122.4, 37.8],
                    [-122.3, 37.7]
                ]
            },
            'properties': {
                'name': 'Test Route',
                'length': 5.5
            }
        }]
    }
    
    response = client.post('/vector/register', json={'id': 'test_lines', 'geojson': line_geojson})
    assert response.status_code == 200
    print("✅ LineString registration successful\n")
    
    # Test 4: Retrieve Vector
    print("Test 4: Retrieve Vector Data...")
    response = client.get('/vector/get/test_points')
    assert response.status_code == 200
    data = response.json()
    assert data['type'] == 'FeatureCollection'
    assert len(data['features']) == 1
    print("✅ Vector retrieval successful\n")
    
    # Test 5: List All Vectors
    print("Test 5: List All Vectors...")
    response = client.get('/vector/list')
    assert response.status_code == 200
    data = response.json()
    assert 'vectors' in data
    assert len(data['vectors']) >= 3  # At least our 3 test vectors
    print(f"✅ Vector listing successful ({len(data['vectors'])} vectors found)\n")
    
    # Test 6: Export Point to Shapefile
    print("Test 6: Export Point to Shapefile...")
    response = client.post('/vector/export_shapefile/test_points')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    
    # Verify ZIP contents
    zip_data = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_data, 'r') as z:
        files = z.namelist()
        assert any(f.endswith('.shp') for f in files), "Missing .shp file"
        assert any(f.endswith('.shx') for f in files), "Missing .shx file"
        assert any(f.endswith('.dbf') for f in files), "Missing .dbf file"
        assert any(f.endswith('.prj') for f in files), "Missing .prj file"
    print("✅ Point shapefile export successful\n")
    
    # Test 7: Export Polygon to Shapefile
    print("Test 7: Export Polygon to Shapefile...")
    response = client.post('/vector/export_shapefile/test_polygons')
    assert response.status_code == 200
    print("✅ Polygon shapefile export successful\n")
    
    # Test 8: Export LineString to Shapefile
    print("Test 8: Export LineString to Shapefile...")
    response = client.post('/vector/export_shapefile/test_lines')
    assert response.status_code == 200
    print("✅ LineString shapefile export successful\n")
    
    # Test 9: Draw Feature Save
    print("Test 9: Draw Feature Save...")
    drawn_features = [{
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [-122.4, 37.8]
        },
        'properties': {'drawn': True}
    }]
    
    response = client.post('/vector/draw', json={'id': 'test_drawings', 'features': drawn_features})
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] == True
    print("✅ Draw feature save successful\n")
    
    # Test 10: Verify Single Feature Normalization
    print("Test 10: Single Feature Normalization...")
    single_feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [-122.4, 37.8]
        },
        'properties': {'test': 'single'}
    }
    
    response = client.post('/vector/register', json={'id': 'single_feature', 'geojson': single_feature})
    assert response.status_code == 200
    data = response.json()
    assert data['featureCount'] == 1
    print("✅ Single feature normalization successful\n")
    
    print("=" * 60)
    print("🎉 All tests passed! Vector features are working correctly.")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        test_vector_features()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
