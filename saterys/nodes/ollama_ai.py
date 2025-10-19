"""
OLLAMA AI LLM Node for intelligent workflow creation
Connects to OLLAMA to generate new nodes based on user prompts
"""

NAME = "ollama.ai"
DEFAULT_ARGS = {
    "prompt": "Create a raster processing node to calculate NDVI from satellite imagery",
    "model": "llama3.2:latest",
    "ollama_host": "http://localhost:11434",
    "max_tokens": 1000,
    "temperature": 0.7
}

def run(args, inputs, context):
    """
    Run OLLAMA AI to generate workflow suggestions
    """
    import json
    import requests
    from typing import Dict, Any
    
    prompt = args.get("prompt", "")
    model = args.get("model", "llama3.2:latest")
    ollama_host = args.get("ollama_host", "http://localhost:11434")
    max_tokens = args.get("max_tokens", 1000)
    temperature = args.get("temperature", 0.7)
    
    if not prompt:
        return {"ok": False, "error": "No prompt provided"}
    
    # System prompt for SATERYS workflow generation
    system_prompt = """You are an AI assistant specialized in geospatial analysis workflows using SATERYS.
    
SATERYS is a node-based geospatial pipeline builder. Available node types include:
- raster.input: Load GeoTIFF/COG files
- raster.ndvi: Calculate NDVI from raster bands
- raster.ndwi: Calculate NDWI for water detection 
- raster.pca: Principal Component Analysis
- sum: Sum numeric values
- hello: Hello world example
- script: Execute custom Python code

When creating nodes, you should respond with a JSON structure containing:
{
  "nodes": [
    {
      "type": "node_type_name",
      "label": "Human readable label",
      "args": {"param1": "value1", "param2": "value2"},
      "position": {"x": 100, "y": 200}
    }
  ],
  "edges": [
    {"source": "node_id_1", "target": "node_id_2"}
  ],
  "description": "Brief description of what this workflow does"
}

For positions, space nodes horizontally by ~260px and vertically by ~140px for good layout.
Keep your response focused and practical for geospatial analysis workflows."""

    try:
        # OLLAMA API request
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser request: {prompt}",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            f"{ollama_host}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return {
                "ok": False, 
                "error": f"OLLAMA API error: {response.status_code} - {response.text}"
            }
        
        result = response.json()
        ai_response = result.get("response", "")
        
        # Try to extract JSON from the response
        workflow_suggestion = None
        try:
            # Look for JSON in the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                workflow_suggestion = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, return the raw response
            pass
        
        return {
            "type": "ai_suggestion",
            "ai_response": ai_response,
            "workflow_suggestion": workflow_suggestion,
            "model_used": model,
            "prompt": prompt,
            "success": True
        }
        
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": "Cannot connect to OLLAMA. Make sure OLLAMA is running on " + ollama_host
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "error": "OLLAMA request timed out. Try reducing max_tokens or use a faster model."
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Unexpected error: {str(e)}"
        }