# Vector Data Examples

This directory contains examples for working with vector data in SATERYS.

## Examples

### vector_drawing_example.py

Demonstrates the new vector capabilities:
- Loading shapefiles, GeoJSON, and GeoPackage files
- Creating vector features programmatically
- Using interactive drawing tools
- Extracting elevation profiles from DEMs
- Exporting drawn features

## Quick Start

1. **Start SATERYS:**
   ```bash
   saterys
   ```

2. **Access the web interface:**
   ```
   http://localhost:8000
   ```

3. **Try Vector Input:**
   - Add a `vector.input` node
   - Set path to a shapefile or GeoJSON file
   - Run and preview on the map

4. **Try Interactive Drawing:**
   - Click "Draw" button in header
   - Use drawing tools to create features
   - Click "Export" to save as GeoJSON

## Sample Data

For testing, you can:
- Create a simple GeoJSON file
- Use the drawing tools to create features
- Download sample data from natural earth: https://www.naturalearthdata.com/

## Documentation

See [Vector Features Documentation](../../docs/vector-features.md) for detailed information.
