# AI-Assisted SATERYS

SATERYS now includes AI-powered features that allow users to generate geospatial workflows using natural language descriptions. This documentation covers the setup, usage, and technical details of the AI integration.

## Features

- **Natural Language Node Generation**: Describe what you want to create and let AI generate the appropriate nodes
- **Auto-Pipeline Creation**: Generate complete workflows with connected nodes
- **Smart Positioning**: Automatically position nodes on the canvas to avoid overlaps
- **Multiple AI Providers**: Support for both local (OLLAMA) and cloud (OpenAI) AI services
- **Demo Mode**: Test functionality without AI service setup

## Quick Start

### 1. Using AI Features (Demo Mode)

If you don't have AI services configured, SATERYS will work in demo mode:

1. Click the **"AI Prompt"** button in the header or sidebar
2. Select generation type: **"Full Pipeline"** or **"Single Node"**  
3. Enter your request (e.g., "Create a workflow to calculate NDVI from satellite imagery")
4. Click **"Generate Pipeline (Demo)"**

Demo mode will generate mock nodes based on your request for testing purposes.

### 2. Setting Up OLLAMA (Local AI)

For local AI processing using OLLAMA:

```bash
# Install OLLAMA
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (e.g., llama3.2)
ollama pull llama3.2

# Start OLLAMA service
ollama serve
```

SATERYS will automatically detect and use OLLAMA if available.

### 3. Setting Up OpenAI (Cloud AI)

For cloud-based AI using OpenAI:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start SATERYS
saterys
```

## Usage Examples

### Basic Node Generation

**Prompt**: "Add an NDVI calculation node"
**Result**: Single NDVI node with appropriate default parameters

### Pipeline Generation

**Prompt**: "Create a workflow to calculate NDVI from satellite imagery"
**Result**: Complete pipeline with:
- Raster input node
- NDVI calculation node  
- Automatic connection between nodes

### Advanced Workflows

**Prompt**: "Build a pipeline for water body detection using NDWI"
**Result**: Multi-node pipeline for water analysis

**Prompt**: "Create a forest cover analysis workflow with PCA"
**Result**: Complex workflow with multiple processing steps

## Supported Node Types

The AI system understands these SATERYS node types:

- **raster.input**: Load raster files (GeoTIFF, COG)
- **raster.ndvi**: Calculate NDVI vegetation index
- **raster.ndwi**: Calculate NDWI water index  
- **raster.pca**: Principal Component Analysis
- **script**: Custom Python script execution
- **sum**: Sum numeric values
- **hello**: Hello world example

## API Reference

### Check AI Status

```bash
GET /ai/status
```

**Response**:
```json
{
  "available": true,
  "provider": "ollama",
  "model": "llama3.2",
  "models": ["llama3.2", "codellama"]
}
```

### Generate Content

```bash
POST /ai/generate
```

**Request**:
```json
{
  "prompt": "Create a workflow to calculate NDVI",
  "type": "pipeline",
  "position": {"x": 200, "y": 200}
}
```

**Response**:
```json
{
  "success": true,
  "nodes": [
    {
      "id": "input_demo",
      "type": "raster.input",
      "label": "raster.input (input_demo)",
      "args": {"path": "/path/to/demo.tif"},
      "position": {"x": 100, "y": 200}
    }
  ],
  "edges": [
    {"source": "input_demo", "target": "ndvi_demo"}
  ],
  "description": "NDVI calculation workflow"
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for cloud AI
- `SATERYS_AI_PROVIDER`: Force specific provider ("ollama" or "openai")
- `SATERYS_AI_MODEL`: Override default model name

### Model Configuration

**OLLAMA Models** (recommended):
- `llama3.2`: General purpose, good performance
- `codellama`: Code-focused, better for technical tasks
- `mistral`: Alternative general purpose model

**OpenAI Models**:
- `gpt-4o`: Most capable, higher cost
- `gpt-4o-mini`: Good balance of capability and cost
- `gpt-3.5-turbo`: Fastest, lower cost

## Troubleshooting

### AI Service Not Available

If you see "Demo Mode" status:

1. **OLLAMA**: Ensure OLLAMA is installed and running (`ollama serve`)
2. **OpenAI**: Check that `OPENAI_API_KEY` environment variable is set
3. **Network**: Verify internet connection for OpenAI or local OLLAMA access

### Generated Nodes Not Appearing

1. Check the logs panel for error messages
2. Verify the prompt is descriptive enough
3. Try using example prompts first
4. Check browser console for JavaScript errors

### Poor Generation Quality

1. Be more specific in your prompts
2. Use geospatial terminology the AI understands
3. Try different prompt phrasing
4. Consider switching AI providers/models

## Development

### Adding New Node Types

To make new node types available to the AI:

1. Add the node to SATERYS plugin system
2. Update `_get_available_node_types()` in `ai_service.py`
3. Add example usage to the AI training prompts

### Customizing AI Prompts

The AI prompts can be customized in `ai_service.py`:

```python
def _build_context_prompt(self, user_request: str) -> str:
    # Customize the system prompt here
    return f"Your custom instructions... {user_request}"
```

### Extending AI Providers

To add new AI providers:

1. Add provider to `AIProvider` enum
2. Implement client initialization in `_initialize_client()`
3. Add generation logic in `_generate_response()`

## Best Practices

### Writing Effective Prompts

**Good**: "Create a workflow to calculate NDVI from Landsat imagery"
**Better**: "Build a pipeline that loads a raster file and calculates NDVI using red band 4 and NIR band 5"

**Good**: "Add a water detection node"  
**Better**: "Add an NDWI calculation node for water body detection"

### Performance Tips

1. Use OLLAMA for privacy and no API costs
2. Start with smaller models for testing
3. Use specific node type requests for faster responses
4. Cache AI status checks in production

### Security Considerations

1. Never commit API keys to version control
2. Use environment variables for configuration
3. Consider network restrictions for OLLAMA access
4. Monitor API usage costs for OpenAI

## Support

For issues with AI features:

1. Check the [GitHub Issues](https://github.com/bastian6666/SATERYS/issues)
2. Review logs in the SATERYS interface
3. Test with demo mode first
4. Verify AI service configuration

The AI features are designed to enhance SATERYS workflows while maintaining the flexibility and power of the underlying geospatial processing capabilities.