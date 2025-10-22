# saterys/llm_service.py
"""
LLM service for generating workflow nodes based on user prompts.
Uses OpenAI's GPT-4o-mini for cost efficiency.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
import json
import re


def _get_openai_client():
    """Get OpenAI client, checking for API key."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI package not installed. Install with: pip install openai"
        )
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it to use LLM features."
        )
    
    return OpenAI(api_key=api_key)


def _get_existing_node_definitions(plugins: Dict[str, Any]) -> str:
    """Generate a description of existing node types for the LLM context."""
    descriptions = []
    
    for name, mod in plugins.items():
        default_args = getattr(mod, "DEFAULT_ARGS", {})
        doc = getattr(mod, "__doc__", "")
        
        # Clean up docstring
        doc_lines = [line.strip() for line in doc.split('\n') if line.strip()]
        doc_summary = ' '.join(doc_lines[:3]) if doc_lines else "No description"
        
        descriptions.append(f"- **{name}**: {doc_summary}")
        if default_args:
            descriptions.append(f"  Default args: {json.dumps(default_args, indent=2)}")
    
    return "\n".join(descriptions)


def _get_node_code_example() -> str:
    """Provide a template/example for node code generation."""
    return '''
# Example node structure:
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
        inputs: Data from connected upstream nodes (dict of {node_id: output})
        context: Runtime context (nodeId, etc.)
        
    Returns:
        Dictionary with output data
    """
    # Access parameters
    param1 = args.get("param1", "default_value")
    
    # Access upstream data
    upstream_data = list(inputs.values())[0] if inputs else None
    
    # For raster operations, check for raster input:
    # raster_input = next((inp for inp in inputs.values() 
    #                      if isinstance(inp, dict) and inp.get("type") == "raster"), None)
    
    # Return output (can be dict with "type" key for typed outputs)
    return {
        "type": "raster",  # or "vector", "text", etc.
        "path": "/path/to/output.tif",
        "metadata": {...}
    }
'''


async def generate_nodes_from_prompt(
    prompt: str, 
    existing_plugins: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate new node definitions based on a user prompt.
    
    Args:
        prompt: User's natural language description of what they want
        existing_plugins: Dict of existing plugin modules
        
    Returns:
        Dict with:
          - nodes: List of node definitions to create
          - explanation: Text explaining what was generated
          - error: Error message if generation failed
    """
    try:
        client = _get_openai_client()
    except (ImportError, ValueError) as e:
        return {
            "ok": False,
            "error": str(e),
            "nodes": [],
            "explanation": ""
        }
    
    # Build context about existing nodes
    existing_nodes_desc = _get_existing_node_definitions(existing_plugins)
    node_example = _get_node_code_example()
    
    system_prompt = f"""You are an expert at creating geospatial workflow nodes for the SATERYS platform.

EXISTING NODES:
{existing_nodes_desc}

NODE CODE TEMPLATE:
{node_example}

Your task is to:
1. Analyze the user's request
2. Identify which existing nodes can help
3. Create NEW node definitions ONLY if absolutely necessary (prefer using existing nodes)
4. Generate complete Python code for any new nodes
5. Return a workflow plan

IMPORTANT RULES:
- Prefer using existing nodes when possible
- Only create new nodes for missing functionality
- Follow the exact node structure shown in the template
- Use proper imports (numpy, rasterio, etc.)
- Include clear docstrings
- Return valid JSON with your response

Response format (JSON):
{{
  "workflow_plan": "Brief explanation of the workflow",
  "existing_nodes_to_use": [
    {{"type": "node.type", "purpose": "what it does in this workflow"}},
    ...
  ],
  "new_nodes": [
    {{
      "name": "node.type.name",
      "purpose": "what this node does",
      "code": "complete Python code for the node",
      "default_args": {{"param": "value"}},
      "position": {{"x": 100, "y": 100}}
    }},
    ...
  ],
  "connections": [
    {{"from": "source_node_type", "to": "target_node_type"}},
    ...
  ]
}}
"""
    
    user_message = f"Create a workflow for: {prompt}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        # Parse and structure the response
        nodes_to_create = []
        explanation_parts = [result.get("workflow_plan", "")]
        
        # Add info about existing nodes to use
        if result.get("existing_nodes_to_use"):
            explanation_parts.append("\n**Existing nodes to use:**")
            for node_info in result["existing_nodes_to_use"]:
                explanation_parts.append(f"- {node_info.get('type')}: {node_info.get('purpose')}")
        
        # Process new nodes to create
        if result.get("new_nodes"):
            explanation_parts.append("\n**New nodes to create:**")
            for i, node_def in enumerate(result["new_nodes"]):
                explanation_parts.append(f"- {node_def.get('name')}: {node_def.get('purpose')}")
                
                # Structure node for creation
                nodes_to_create.append({
                    "id": f"llm_gen_{i+1}",
                    "type": node_def.get("name", f"custom.node_{i+1}"),
                    "label": f"{node_def.get('name', 'custom')} (generated)",
                    "code": node_def.get("code", ""),
                    "args": node_def.get("default_args", {}),
                    "position": node_def.get("position", {"x": 300 + i * 260, "y": 200})
                })
        
        # Add connection suggestions
        if result.get("connections"):
            explanation_parts.append("\n**Suggested connections:**")
            for conn in result["connections"]:
                explanation_parts.append(f"- {conn.get('from')} → {conn.get('to')}")
        
        return {
            "ok": True,
            "nodes": nodes_to_create,
            "existing_nodes": result.get("existing_nodes_to_use", []),
            "connections": result.get("connections", []),
            "explanation": "\n".join(explanation_parts),
            "error": None
        }
        
    except json.JSONDecodeError as e:
        return {
            "ok": False,
            "error": f"Failed to parse LLM response as JSON: {e}",
            "nodes": [],
            "explanation": ""
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"LLM generation error: {str(e)}",
            "nodes": [],
            "explanation": ""
        }


def save_generated_node(node_code: str, node_name: str) -> tuple[bool, str]:
    """
    Save generated node code to a file in the user's nodes directory.
    
    Args:
        node_code: The Python code for the node
        node_name: Name of the node (will be cleaned for filename)
        
    Returns:
        Tuple of (success, message)
    """
    # Clean node name for filename
    safe_name = re.sub(r'[^a-zA-Z0-9_.]', '_', node_name)
    filename = f"{safe_name}.py"
    
    # Save to ./nodes directory (user workspace)
    nodes_dir = os.path.join(os.getcwd(), "nodes")
    os.makedirs(nodes_dir, exist_ok=True)
    
    filepath = os.path.join(nodes_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write(node_code)
        return True, f"Node saved to {filepath}"
    except Exception as e:
        return False, f"Failed to save node: {e}"
