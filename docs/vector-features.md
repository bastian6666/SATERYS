# Vector Data and Drawing Features

SATERYS now supports comprehensive vector data capabilities, allowing you to work with shapefiles, GeoJSON, and GeoPackage files, as well as create and edit vector features directly on the map.

## Features

### 1. Vector Data Input

The `vector.input` node allows you to load vector data from various formats:

- **Supported Formats:** Shapefile (.shp), GeoJSON (.geojson), GeoPackage (.gpkg)
- **Automatic CRS transformation** to WGS84 for web display
- **Feature properties** preserved and displayed in popups

#### Usage Example

```python
# In a SATERYS workflow:
# 1. Add a vector.input node
# 2. Configure the path to your vector file
{
  "path": "/path/to/your/shapefile.shp"
}
```

The node returns metadata including:
- Feature count
- Geometry type (Polygon, LineString, Point, etc.)
- Bounds (spatial extent)
- CRS information
- Property field names

### 2. Vector Data Creation

The `vector.create` node enables you to create new vector datasets programmatically:

#### Configuration Options

```json
{
  "geometry_type": "Polygon",        // Polygon, LineString, or Point
  "output_format": "GeoJSON",        // GeoJSON or ESRI Shapefile
  "output_path": "",                 // Optional: auto-generates if empty
  "features": [],                    // List of feature objects
  "crs": "EPSG:4326"                // Output coordinate system
}
```

#### Example: Creating Features

```python
# Create a polygon feature
{
  "geometry_type": "Polygon",
  "output_format": "GeoJSON",
  "features": [
    {
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
        "name": "Study Area",
        "type": "urban"
      }
    }
  ]
}
```

### 3. Interactive Drawing Tools

SATERYS now includes interactive drawing tools powered by Leaflet.draw:

#### Available Tools

- **Polygon:** Draw custom polygons by clicking points
- **Rectangle:** Draw rectangular areas
- **Circle:** Draw circular areas
- **Polyline:** Draw lines and paths
- **Marker:** Place point markers
- **Edit:** Modify existing drawn features
- **Delete:** Remove drawn features

#### How to Use

1. **Enable Drawing Mode:** Click the "Draw" button in the header (pencil icon)
2. **Select Tool:** Choose from the drawing toolbar that appears on the map
3. **Draw Features:** Click on the map to create your features
4. **Edit/Delete:** Use the edit tools to modify or remove features
5. **Export:** Click the "Export" button to save drawn features as GeoJSON

#### Export Drawn Features

Drawn features can be exported as GeoJSON files:
- Click the "Export" button (download icon) in the header
- Features are saved with complete geometry and any properties
- File name format: `drawn-features-YYYY-MM-DDTHH-MM-SS.geojson`

### 4. Vector Layer Display

Vector layers are automatically styled when previewed on the map:

#### Styling

- **Polygons:** Blue fill with semi-transparent interior
- **Lines:** Blue solid lines
- **Points:** Blue circle markers with white borders

#### Interactive Features

- **Click on features** to see a popup with properties
- **Layer control** allows toggling vector layers on/off
- **Auto-zoom** to layer bounds when previewed
- **Layer naming** includes node ID for easy identification

### 5. Elevation Profile (3D Support)

The `raster.elevation_profile` node extracts elevation data from Digital Elevation Models (DEMs):

#### Configuration

```json
{
  "dem_path": "/path/to/dem.tif",
  "profile_type": "line",            // "line" or "polygon"
  "coordinates": [                   // [lon, lat] pairs in WGS84
    [-122.5, 37.7],
    [-122.4, 37.8]
  ],
  "sample_distance": 100,            // Meters between samples (for lines)
  "output_path": ""                  // Optional: auto-generates if empty
}
```

#### Output

The node generates a GeoJSON file with 3D coordinates (lon, lat, elevation):

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.5, 37.7, 245.3]
      },
      "properties": {
        "elevation": 245.3,
        "distance": 0,
        "index": 0
      }
    }
  ]
}
```

#### Statistics

Returns elevation statistics:
- Minimum elevation
- Maximum elevation
- Average elevation
- Elevation range

#### Use Cases

- Terrain analysis along transects
- Viewshed analysis preparation
- 3D visualization data generation
- Topographic profile extraction

## Workflow Examples

### Example 1: Load and Display Vector Data

1. Add a `vector.input` node
2. Set the path to your shapefile/GeoJSON
3. Run the node
4. Click the "👁" (preview) button on the node
5. The vector layer appears on the map with popups

### Example 2: Draw and Export Study Areas

1. Click "Draw" in the header to enable drawing
2. Select the Polygon tool
3. Draw your study area on the map
4. Click "Export" to save as GeoJSON
5. Use the exported file in other GIS software

### Example 3: Elevation Profile Along a Path

1. Add a `raster.input` node with a DEM file
2. Add a `raster.elevation_profile` node
3. Configure coordinates for your transect line
4. Connect nodes: DEM → elevation_profile
5. Run to generate 3D profile data

### Example 4: Create Vector Data Programmatically

1. Add a `vector.create` node
2. Define features in the `features` parameter
3. Run the node to generate output file
4. Preview on the map to verify

## API Endpoints

### Vector Preview Registration

```bash
POST /preview/vector/register
Content-Type: application/json

{
  "id": "my-vector",
  "path": "/path/to/vector.shp"
}
```

### Get GeoJSON

```bash
GET /preview/vector/{id}/geojson
```

### Get Bounds

```bash
GET /preview/vector/{id}/bounds
```

## Tips and Best Practices

1. **Large Files:** For large vector datasets, consider simplifying geometries before loading
2. **CRS Handling:** SATERYS automatically transforms to WGS84 for web display
3. **Drawing Precision:** Zoom in for more precise drawing
4. **Export Regularly:** Export drawn features frequently to avoid data loss
5. **Combine with Raster:** Use vector layers as masks or ROIs for raster analysis
6. **Elevation Profiles:** Ensure DEM and profile coordinates overlap spatially

## Limitations and Future Enhancements

### Current Limitations

- Drawing tools work in 2D only (z-values must be added separately)
- No direct shapefile editing (export as GeoJSON, edit externally, re-import)
- Large vector files (>1MB) may take time to render

### Planned Enhancements

- 3D visualization with CesiumJS or deck.gl
- Advanced styling options (color by attribute, size by value)
- Vector analysis operations (buffer, intersection, union)
- Direct attribute editing in popups
- Vector tile support for large datasets

## Troubleshooting

### Vector Not Displaying

- Check that the file path is correct and absolute
- Verify the file format is supported (SHP, GeoJSON, GPKG)
- Ensure the CRS is defined in the source file
- Check browser console for errors

### Drawing Tools Not Appearing

- Ensure drawing mode is enabled (click "Draw" button)
- Verify Leaflet.draw loaded successfully
- Check that the map is fully initialized

### Elevation Profile Empty

- Verify DEM path is correct
- Ensure coordinates overlap with DEM extent
- Check that coordinates are in lon/lat (EPSG:4326)
- Verify DEM has valid elevation data (not all NoData)

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/bastian6666/SATERYS/issues)
- Review existing workflows in the examples directory
- Consult the main [documentation](../README.md)
