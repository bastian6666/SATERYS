# Vector Data Examples

This directory contains examples demonstrating SATERYS vector data capabilities.

## Features

### 1. Interactive Vector Drawing
- Draw points, lines, polygons, rectangles, and circles directly on the map
- Edit and delete drawn features
- Automatic saving to the backend

### 2. Vector Data Visualization
- Load and display GeoJSON data on the map
- Custom styling for different geometry types
- Interactive popups showing feature properties

### 3. Shapefile Export
- Export vector data to ESRI Shapefile format
- Downloaded as ZIP containing .shp, .shx, .dbf, .prj, and .cpg files
- Supports points, lines, and polygons

### 4. 3D Visualization
- Toggle 3D view for elevation profiles
- Enhanced visualization for terrain analysis

## Quick Start

### Using the Web Interface

1. Start SATERYS:
   ```bash
   saterys
   ```

2. Open your browser to http://localhost:8000

3. Drawing features:
   - Use the drawing toolbar on the left side of the map
   - Select a tool (marker, polyline, polygon, rectangle, circle)
   - Draw on the map
   - Features are automatically saved

4. Loading vectors:
   - Click the "Load Vectors" button in the sidebar
   - Your drawn features will be displayed with styling

5. Exporting to shapefile:
   - Click "Export Shapefile" to download your drawings
   - A ZIP file will be downloaded containing all shapefile components

### Programmatic Usage

See `vector_drawing_demo.py` for examples of:
- Creating vector data programmatically
- Registering GeoJSON data via API
- Exporting to shapefile format

Run the demo:
```bash
python examples/03_vector/vector_drawing_demo.py
```

## API Endpoints

### Register Vector Data
```bash
POST /vector/register
Content-Type: application/json

{
  "id": "my_vector",
  "geojson": {
    "type": "FeatureCollection",
    "features": [...]
  }
}
```

### Retrieve Vector Data
```bash
GET /vector/get/{vector_id}
```

### List All Vectors
```bash
GET /vector/list
```

### Export to Shapefile
```bash
POST /vector/export_shapefile/{vector_id}
```
Returns a ZIP file containing shapefile components.

### Save Drawn Features
```bash
POST /vector/draw
Content-Type: application/json

{
  "id": "user_drawings",
  "features": [...]
}
```

## Supported Geometry Types

- **Point** / **MultiPoint**: Individual locations
- **LineString** / **MultiLineString**: Routes, paths, networks
- **Polygon** / **MultiPolygon**: Areas, boundaries, study regions
- **Circle**: Circular regions (automatically converted to polygons with 64 vertices on export)
- **Rectangle**: Rectangular areas (automatically converted to polygons on export)

**Note**: Leaflet Draw creates Circle and Rectangle geometries as special types, but these are automatically converted to standard Polygon geometries when saving or exporting to maintain compatibility with GeoJSON and shapefile standards.

## Feature Properties

All features can have custom properties that will be:
- Displayed in popups when clicking features on the map
- Included in shapefile exports as attribute fields
- Accessible via the API

Example feature with properties:
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-122.4, 37.8]
  },
  "properties": {
    "name": "Sample Location",
    "category": "research",
    "value": 42.5,
    "active": true
  }
}
```

## Use Cases

1. **Field Data Collection**: Mark sample locations and survey areas
2. **Study Area Definition**: Outline regions of interest for analysis
3. **Route Planning**: Draw paths for drone flights or ground surveys
4. **Feature Annotation**: Mark and describe features in satellite imagery
5. **Data Export**: Share results as standard shapefiles for GIS software

## Integration with Existing Nodes

Vector data can be combined with raster analysis workflows:
- Use vector polygons to define areas for raster statistics
- Overlay vector data on raster visualizations
- Export both raster and vector results together

## Tips

- Drawn features are saved with ID "user_drawings"
- Multiple vector layers can be registered with different IDs
- The map uses WGS84 (EPSG:4326) coordinate system
- Shapefiles maintain the original coordinate system
- Use the layer control to toggle vector layers on/off
- 3D view adds elevation profile visualization for enhanced terrain analysis
