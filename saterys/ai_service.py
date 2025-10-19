# saterys/ai_service.py
"""
AI service for generating node plugins and auto-adding nodes to the canvas.
Supports both OLLAMA (local) and OpenAI (cloud) models.
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import re

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass
class NodeConfig:
    """Configuration for a generated node"""
    name: str
    type: str
    args: Dict[str, Any]
    position: Dict[str, float]
    description: str
    
    
@dataclass
class PipelineConfig:
    """Configuration for a generated mini-pipeline"""
    nodes: List[NodeConfig]
    edges: List[Dict[str, str]]  # [{source: str, target: str}, ...]
    description: str


class AIService:
    """AI service for SATERYS node generation and pipeline automation"""
    
    def __init__(self, provider: AIProvider = AIProvider.OLLAMA, model: str = None):
        self.provider = provider
        self.model = model or self._get_default_model()
        self.client = self._initialize_client()
        
    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        if self.provider == AIProvider.OLLAMA:
            return "llama3.2"  # or "codellama", "mistral"
        elif self.provider == AIProvider.OPENAI:
            return "gpt-4o-mini"  # or "gpt-4"
        return "llama3.2"
    
    def _initialize_client(self):
        """Initialize the AI client based on provider"""
        if self.provider == AIProvider.OLLAMA:
            if not OLLAMA_AVAILABLE:
                raise ImportError("ollama package not available. Install with: pip install ollama")
            # OLLAMA client is module-level, no initialization needed
            return None
        elif self.provider == AIProvider.OPENAI:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not available. Install with: pip install openai")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response from AI model"""
        try:
            if self.provider == AIProvider.OLLAMA:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response['message']['content']
            elif self.provider == AIProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"AI generation failed: {str(e)}")
    
    def _get_available_node_types(self) -> List[Dict[str, Any]]:
        """Get list of available node types from the SATERYS system"""
        # This would typically be passed in or fetched from the main app
        # For now, we'll define common geospatial node types
        return [
            {"name": "raster.input", "description": "Load raster files (GeoTIFF, COG)", "default_args": {"path": ""}},
            {"name": "raster.ndvi", "description": "Calculate NDVI vegetation index", "default_args": {"red_band": 4, "nir_band": 5}},
            {"name": "raster.ndwi", "description": "Calculate NDWI water index", "default_args": {"green_band": 3, "nir_band": 5}},
            {"name": "raster.pca", "description": "Principal Component Analysis on raster", "default_args": {"n_components": 3}},
            {"name": "script", "description": "Custom Python script execution", "default_args": {"code": "print('hello')"}},
            {"name": "sum", "description": "Sum numeric values", "default_args": {"nums": [1, 2, 3]}},
            {"name": "hello", "description": "Hello world example", "default_args": {"name": "world"}},
        ]
    
    def _build_context_prompt(self, user_request: str) -> str:
        """Build context-aware prompt for node generation"""
        available_nodes = self._get_available_node_types()
        
        node_descriptions = "\n".join([
            f"- {node['name']}: {node['description']}"
            for node in available_nodes
        ])
        
        prompt = f"""You are an AI assistant for SATERYS, a geospatial pipeline builder. Your task is to help users create node-based workflows for Earth observation and remote sensing analysis.

Available Node Types:
{node_descriptions}

User Request: "{user_request}"

Please analyze the user's request and generate appropriate nodes and connections. Respond with a JSON object in this exact format:

{{
  "nodes": [
    {{
      "id": "unique_node_id",
      "type": "node_type_from_available_list",
      "label": "descriptive_label",
      "args": {{"arg_name": "arg_value"}},
      "position": {{"x": number, "y": number}},
      "description": "what this node does"
    }}
  ],
  "edges": [
    {{
      "source": "source_node_id",
      "target": "target_node_id"
    }}
  ],
  "description": "overall description of the generated pipeline"
}}

Guidelines:
1. Use only node types from the available list
2. Position nodes in a logical flow (left to right, with spacing)
3. Create sensible connections between nodes
4. Set appropriate default arguments based on the use case
5. Generate 1-5 nodes typically, unless the request specifically asks for more
6. Consider typical geospatial workflows (data input → processing → analysis → output)

Return only the JSON object, no additional text."""

        return prompt
    
    def generate_pipeline(self, user_request: str) -> PipelineConfig:
        """Generate a pipeline configuration based on user request"""
        prompt = self._build_context_prompt(user_request)
        
        try:
            response = self._generate_response(prompt)
            
            # Clean response and extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON response
            pipeline_data = json.loads(response)
            
            # Convert to NodeConfig objects
            nodes = []
            for node_data in pipeline_data.get("nodes", []):
                node_config = NodeConfig(
                    name=node_data["id"],
                    type=node_data["type"],
                    args=node_data.get("args", {}),
                    position=node_data.get("position", {"x": 100, "y": 100}),
                    description=node_data.get("description", "")
                )
                nodes.append(node_config)
            
            edges = pipeline_data.get("edges", [])
            description = pipeline_data.get("description", "AI-generated pipeline")
            
            return PipelineConfig(
                nodes=nodes,
                edges=edges,
                description=description
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Pipeline generation failed: {str(e)}")
    
    def generate_single_node(self, user_request: str, position: Optional[Dict[str, float]] = None) -> NodeConfig:
        """Generate a single node based on user request"""
        if position is None:
            position = {"x": 200, "y": 200}
            
        available_nodes = self._get_available_node_types()
        node_descriptions = "\n".join([
            f"- {node['name']}: {node['description']}"
            for node in available_nodes
        ])
        
        prompt = f"""You are an AI assistant for SATERYS. Generate a single node based on this request: "{user_request}"

Available Node Types:
{node_descriptions}

Respond with a JSON object for a single node:

{{
  "id": "unique_node_id",
  "type": "node_type_from_available_list",
  "label": "descriptive_label",
  "args": {{"arg_name": "arg_value"}},
  "description": "what this node does"
}}

Choose the most appropriate node type and set reasonable default arguments.
Return only the JSON object, no additional text."""

        try:
            response = self._generate_response(prompt)
            
            # Clean and parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            node_data = json.loads(response)
            
            return NodeConfig(
                name=node_data["id"],
                type=node_data["type"],
                args=node_data.get("args", {}),
                position=position,
                description=node_data.get("description", "")
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Node generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the AI service is available and properly configured"""
        try:
            if self.provider == AIProvider.OLLAMA:
                # Try to list available models to test connection
                ollama.list()
                return True
            elif self.provider == AIProvider.OPENAI:
                # Check if API key is available
                return bool(os.getenv("OPENAI_API_KEY"))
            return False
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for the current provider"""
        try:
            if self.provider == AIProvider.OLLAMA:
                models = ollama.list()
                return [model['name'] for model in models.get('models', [])]
            elif self.provider == AIProvider.OPENAI:
                # OpenAI models are fixed, return common ones
                return ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
            return []
        except Exception:
            return []


def create_ai_service(provider: str = "ollama", model: str = None) -> AIService:
    """Factory function to create AI service instance"""
    try:
        ai_provider = AIProvider(provider.lower())
        return AIService(provider=ai_provider, model=model)
    except ValueError:
        # Default to OLLAMA if invalid provider
        return AIService(provider=AIProvider.OLLAMA, model=model)


# Example usage and testing
if __name__ == "__main__":
    # Test the AI service
    service = create_ai_service("ollama")
    
    if service.is_available():
        print("AI service is available")
        print(f"Available models: {service.get_available_models()}")
        
        # Test single node generation
        try:
            node = service.generate_single_node("create an NDVI calculation node")
            print(f"Generated node: {node}")
        except Exception as e:
            print(f"Node generation failed: {e}")
        
        # Test pipeline generation
        try:
            pipeline = service.generate_pipeline("create a workflow to calculate vegetation index from satellite imagery")
            print(f"Generated pipeline with {len(pipeline.nodes)} nodes")
        except Exception as e:
            print(f"Pipeline generation failed: {e}")
    else:
        print("AI service is not available")