# Vector Data and AI Chat Examples

This directory contains examples demonstrating SATERYS's new features for working with vector data (points, lines, polygons) and the AI chat assistant.

## Vector Data Features

SATERYS now supports working with geospatial vector data alongside raster data. You can:

- Load vector data from various formats (GeoJSON, Shapefile, GPKG)
- Create vector features programmatically (points, lines, polygons)
- Visualize vector layers on the Leaflet map
- Combine vector and raster data in workflows

### Example 1: Creating a Point Feature

Create a simple point on the map:

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "vector.create",
      "label": "Create Point",
      "args": {
        "type": "point",
        "coordinates": [-122.4194, 37.7749],
        "name": "San Francisco",
        "properties": {
          "city": "San Francisco",
          "state": "California"
        }
      },
      "position": {"x": 100, "y": 100}
    }
  ],
  "edges": []
}
```

### Example 2: Creating a Polygon

Define an area of interest:

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "vector.create",
      "label": "Study Area",
      "args": {
        "type": "polygon",
        "coordinates": [
          [-122.5, 37.7],
          [-122.4, 37.7],
          [-122.4, 37.8],
          [-122.5, 37.8],
          [-122.5, 37.7]
        ],
        "name": "Study Area",
        "properties": {
          "area_type": "urban"
        }
      },
      "position": {"x": 100, "y": 100}
    }
  ],
  "edges": []
}
```

### Example 3: Loading Vector Data from File

Load existing vector data:

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "vector.input",
      "label": "Load Boundaries",
      "args": {
        "path": "/path/to/boundaries.geojson",
        "layer": null
      },
      "position": {"x": 100, "y": 100}
    }
  ],
  "edges": []
}
```

## AI Chat Assistant

The AI chat assistant can help you build workflows using natural language. Access it by clicking the "AI Chat" button at the top of the screen.

### Example Prompts

**Create a simple workflow:**
```
Create a workflow to calculate NDVI from a raster at /data/landsat.tif
```

**Add nodes to canvas:**
```
Add a vector.create node to mark a study area
```

**Build a complex workflow:**
```
Build a workflow that:
1. Loads a raster from /data/image.tif
2. Calculates NDVI (red band 4, NIR band 5)
3. Creates a vector polygon for the study area
```

**Modify existing nodes:**
```
Change the coordinates of node n1 to San Francisco's location
```

**Get help:**
```
How do I create a polygon with multiple holes?
```

```
What bands should I use for NDWI calculation?
```

### AI Capabilities

The AI assistant can:

1. **Create Nodes**: Generate new nodes with proper configuration
2. **Connect Nodes**: Establish data flow between nodes
3. **Modify Arguments**: Update node parameters
4. **Explain Concepts**: Answer questions about geospatial analysis
5. **Generate Workflows**: Build complete multi-node pipelines

### Important Notes

- The AI requires an OpenAI API key set in the `OPENAI_API_KEY` environment variable
- Chat history is preserved during your session
- The AI has context about your current workflow and can modify it
- All node types and their arguments are available to the AI

## Combining Vector and Raster Data

You can create workflows that work with both vector and raster data:

```
Create a workflow that:
1. Loads a raster image
2. Loads a vector polygon boundary
3. Calculates NDVI within the polygon area
```

The AI will help you build the complete workflow with proper node connections.

## Tips for Working with the AI

1. **Be Specific**: Provide clear descriptions of what you want
2. **Use Context**: The AI knows about your current workflow
3. **Iterate**: You can ask follow-up questions to refine results
4. **Ask for Help**: The AI can explain concepts and provide guidance

## Environment Setup

To use the AI chat feature, set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Then start SATERYS:

```bash
saterys
```

The chat panel will appear at the bottom of the screen when you click "AI Chat".
