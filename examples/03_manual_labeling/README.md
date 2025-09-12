# Manual Labeling Example

This example demonstrates how to use the SATERYS Manual Labeler for creating training samples from satellite imagery.

## Overview

The Manual Labeler provides an interactive web interface for:
- Manually labeling pixels on satellite imagery
- Managing classification classes with custom colors and names
- Exporting training data in multiple formats (GPKG, Shapefile, CSV)
- Real-time visualization and editing of labeled samples

## Files in this Example

- `basic_labeling.py` - Simple example using the manual labeler
- `create_sample_data.py` - Script to generate synthetic test data
- `advanced_labeling.py` - Advanced configuration example
- `README.md` - This file

## Quick Start

1. **Create sample data** (optional, if you don't have your own raster):
   ```bash
   python create_sample_data.py
   ```

2. **Run the basic example**:
   ```bash
   python basic_labeling.py
   ```

3. **Open the web interface** in your browser:
   - The script will output a URL like: `http://127.0.0.1:8090/labeler`
   - Click the URL or navigate to it manually

4. **Start labeling**:
   - Click "✎ Label: Off" to enable labeling mode
   - Select a class from the color-coded palette
   - Click on the map to label pixels
   - Use the attribute table to manage your labels

## Usage Guide

### Labeling Workflow

1. **Select a class** by clicking on the colored class chips
2. **Enable labeling mode** with the "✎ Label" button or press 'L'
3. **Click on the map** to paint pixels with the selected class
4. **Adjust brush size** using the slider or bracket keys [ ]
5. **Save your work** with the "💾 Save" button or press 'S'

### Keyboard Shortcuts

- `L` - Toggle labeling mode on/off
- `1-9` - Select class by ID number
- `[` / `]` - Decrease/increase brush size
- `Z` - Undo last labeling operation
- `S` - Save current labels to files

### Class Management

- **Add classes**: Click the "+ Class" button
- **Edit classes**: Click the ✎ icon on any class chip
- **Change colors**: Use the color picker in the class editor
- **Rename classes**: Edit the name field in the class editor

### Attribute Table Features

- **Search**: Filter points by ID, class, coordinates, or name
- **Sort**: Click column headers to sort data
- **Edit**: Change class assignments for individual points
- **Delete**: Remove selected points (with optional unpaint)
- **Export**: Download labels as CSV

## Output Files

The manual labeler creates several output files:

### Vector Points (GPKG/Shapefile)
- **File**: `results/training_points.gpkg`
- **Content**: Point geometries with class_id and class_name attributes
- **Use**: Training data for machine learning algorithms

### Raster Labels (GeoTIFF)
- **File**: `results/labels.tif`
- **Content**: Single-band uint8 raster with class pixel values
- **Use**: Pixel-level ground truth for analysis

### Class Definitions (JSON)
- **File**: `results/classes.json`
- **Content**: Class metadata (ID, name, color)
- **Use**: Maintaining consistent class definitions across sessions

## Integration with SATERYS

The Manual Labeler can be integrated into larger SATERYS workflows:

```python
# Example pipeline
raster_input → manual_labeler → ml_classifier → accuracy_assessment
```

### Upstream Connections
- Connect raster outputs from other nodes
- Accepts any GDAL-readable raster format
- Preserves spatial reference and metadata

### Downstream Usage
- Training data for machine learning nodes
- Ground truth for accuracy assessment
- Input for statistical analysis workflows

## Advanced Configuration

See `advanced_labeling.py` for examples of:
- Custom class definitions
- Different output formats
- Performance tuning options
- Integration with existing workflows

## Troubleshooting

### Common Issues

**Map not loading**:
- Check internet connection (required for basemap tiles)
- Verify raster file path and format
- Ensure GDAL can read your raster file

**Labels not saving**:
- Check write permissions for output directory
- Verify disk space availability
- Ensure output paths are valid

**Port conflicts**:
- Use `port_autoselect: True` to find available ports
- Manually specify a different port number

### Getting Help

- Check the [main documentation](../../docs/manual-labeler.md)
- Report issues on [GitHub](https://github.com/bastian6666/SATERYS/issues)
- Join discussions on [GitHub Discussions](https://github.com/bastian6666/SATERYS/discussions)

## Next Steps

- Explore the [comprehensive manual labeler documentation](../../docs/manual-labeler.md)
- Try the [plugin development guide](../../docs/plugins.md) to create custom nodes
- Check out other [SATERYS examples](../) for more workflows