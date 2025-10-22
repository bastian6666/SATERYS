# AI-Powered Workflow Generation

SATERYS now includes an AI-powered chat assistant that helps you create geospatial workflows using natural language prompts.

## Overview

The AI Workflow Assistant uses OpenAI's GPT-4o-mini model to:
- Analyze your workflow requirements
- Identify which existing nodes can help
- Generate new custom nodes when needed
- Automatically add nodes to your canvas
- Suggest connections between nodes

## Setup

### Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key to use this feature.
   - Get one at: https://platform.openai.com/api-keys

2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

3. **Install SATERYS** with OpenAI support (already included):
   ```bash
   pip install saterys
   # OpenAI package is now included as a dependency
   ```

## Usage

### 1. Launch SATERYS

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
saterys
```

### 2. Open AI Chat

Click the **"AI Chat"** button in the top toolbar (chat bubble icon).

### 3. Describe Your Workflow

Enter a natural language description of what you want to accomplish. Examples:

- "Create a workflow to detect buildings using satellite imagery"
- "Calculate NDVI and classify vegetation health"
- "Detect water bodies in Landsat imagery"
- "Create a land cover classification workflow"
- "Extract training samples for machine learning"

### 4. Review and Generate

The AI will:
1. Analyze existing nodes in SATERYS
2. Determine what can be accomplished with current nodes
3. Generate new nodes if necessary
4. Show you a workflow plan

Click **"✨ Generate Workflow"** to add the nodes to your canvas.

## How It Works

### Node Analysis

The AI assistant examines all available nodes in your SATERYS instance, including:
- Built-in nodes (raster.ndvi, raster.ndwi, raster.pca, etc.)
- Custom nodes from your `./nodes/` directory
- Plugin nodes from packages

### Intelligent Generation

The AI follows these principles:
1. **Prefer existing nodes**: Uses built-in nodes when possible
2. **Generate only when needed**: Creates new nodes only for missing functionality
3. **Follow patterns**: New nodes match the structure of existing ones
4. **Standard libraries**: Uses numpy, rasterio, and other geospatial standards

### Node Structure

Generated nodes follow this pattern:

```python
NAME = "node.type.name"
DEFAULT_ARGS = {
    "param1": "default_value",
    "param2": 42
}

def run(args, inputs, context):
    """
    Execute the node logic.
    
    Args:
        args: Node configuration parameters
        inputs: Data from connected upstream nodes
        context: Runtime context (nodeId, etc.)
        
    Returns:
        Dictionary with output data
    """
    # Processing logic here
    return {
        "type": "raster",
        "path": "/path/to/output.tif",
        "metadata": {...}
    }
```

## Cost Considerations

- **Model**: Uses GPT-4o-mini for cost efficiency
- **Typical Cost**: ~$0.01-0.03 per workflow generation
- **Token Usage**: Approximately 1,000-3,000 tokens per request

## Examples

### Example 1: Building Detection

**Prompt**: "Create a workflow to detect buildings using satellite imagery"

**Generated Plan**:
- Uses existing `raster.input` node for data loading
- Generates `raster.building_index` node for building detection
- Suggests connection from input to building detection

### Example 2: Water Body Analysis

**Prompt**: "Detect water bodies and calculate their area"

**Generated Plan**:
- Uses existing `raster.ndwi` node for water detection
- Generates `raster.vectorize` node to convert to polygons
- Generates `vector.area` node to calculate areas
- Suggests full workflow connection chain

## Troubleshooting

### Missing API Key

**Error**: `OPENAI_API_KEY environment variable not set`

**Solution**: Set your API key before starting SATERYS:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### API Rate Limits

If you hit rate limits, consider:
- Using a paid OpenAI account
- Waiting before retrying
- Reducing the complexity of prompts

### Node Generation Issues

If generated nodes don't work as expected:
1. Check the node code in the explanation
2. Manually edit the node in your `./nodes/` directory
3. Provide more specific requirements in your prompt

## Privacy & Security

- Prompts and node metadata are sent to OpenAI
- Source code of existing nodes is included in context
- No user data or actual geospatial data is sent
- API key is stored only in your environment variables

## Best Practices

1. **Be Specific**: Provide clear requirements
   - Good: "Detect buildings using NDVI threshold > 0.3"
   - Poor: "Do something with buildings"

2. **Leverage Existing Nodes**: Check available nodes first
   - Use `/node_types` endpoint to see what's available
   - Let the AI suggest which nodes to use

3. **Iterate**: Start simple, then refine
   - Generate basic workflow first
   - Add complexity in subsequent prompts

4. **Review Code**: Always review generated nodes
   - Check logic and parameters
   - Test with small datasets first
   - Modify as needed for your use case

## Limitations

- Requires internet connection to OpenAI API
- Cannot test generated code before adding to canvas
- May need manual adjustment for complex workflows
- Limited to patterns found in existing nodes

## Future Enhancements

Planned improvements:
- Local LLM support (Ollama, LLaMA)
- Code validation before adding nodes
- Workflow optimization suggestions
- Interactive refinement dialog
- Node testing framework integration

## Support

For issues or questions:
- GitHub Issues: https://github.com/bastian6666/SATERYS/issues
- Discussions: https://github.com/bastian6666/SATERYS/discussions
