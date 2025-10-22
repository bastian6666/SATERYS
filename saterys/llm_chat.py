# llm_chat.py
"""
SATERYS - LLM Chat Integration

Provides an AI assistant powered by OpenAI GPT models to help users:
- Create new nodes and add them to the canvas
- Add existing node types to workflows
- Modify existing nodes
- Generate complete workflows from natural language descriptions

Environment Variables:
- OPENAI_API_KEY: Required. Your OpenAI API key.
- SATERYS_LLM_MODEL: Optional. Default is "gpt-4o-mini" (cost-effective).
"""

from __future__ import annotations
import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

# Initialize OpenAI client
_client: Optional[AsyncOpenAI] = None

def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for LLM chat. "
                "Set it with: export OPENAI_API_KEY=sk-..."
            )
        _client = AsyncOpenAI(api_key=api_key)
    return _client

# Default model (cost-effective)
LLM_MODEL = os.environ.get("SATERYS_LLM_MODEL", "gpt-4o-mini")

# Chat history storage (in-memory for now)
_CHAT_HISTORY: List[Dict[str, Any]] = []
_MAX_HISTORY = 100

# System prompt
SYSTEM_PROMPT = """You are an AI assistant for SATERYS, a geospatial analysis platform with a node-based workflow builder.

Your capabilities:
1. **Create nodes**: Generate JSON to create new nodes with specific configurations
2. **Add nodes**: Add existing node types to the canvas
3. **Modify nodes**: Update node arguments and connections
4. **Build workflows**: Generate complete workflows from user descriptions

Available node types:
- hello: Simple greeting node (args: name)
- sum: Add numbers (args: nums - array of numbers)
- script: Execute custom Python code (args: code)
- raster.input: Load raster files (args: path)
- raster.ndvi: Calculate NDVI from raster (args: red_band, nir_band)
- raster.ndwi: Calculate NDWI from raster (args: green_band, nir_band)
- raster.pca: Principal Component Analysis (args: n_components)
- vector.input: Load vector data (args: path, layer)
- vector.create: Create vector features (args: type, coordinates, name, properties)
- training_sample: Training sample generation

When creating nodes, respond with JSON in this format:
{
  "action": "create_node" | "modify_node" | "create_workflow" | "chat",
  "nodes": [{"type": "node.type", "args": {...}, "label": "Node Label", "position": {"x": 100, "y": 100}}],
  "edges": [{"source": "nodeId1", "target": "nodeId2"}],
  "message": "Human-readable explanation"
}

For general questions or explanations, use action="chat" with just a message.

Keep responses concise and actionable. Always provide the "message" field to explain what you're doing."""

# Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None  # Current workflow state (nodes, edges)

class ChatResponse(BaseModel):
    id: str
    message: str
    action: str = "chat"  # chat, create_node, modify_node, create_workflow
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(BaseModel):
    messages: List[ChatMessage]

# Router
llm_router = APIRouter(prefix="/llm", tags=["llm"])

@llm_router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Send a message to the LLM and get a response with potential actions.
    """
    try:
        client = get_openai_client()
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    # Build context for the LLM
    context_str = ""
    if req.context:
        nodes = req.context.get("nodes", [])
        edges = req.context.get("edges", [])
        if nodes:
            context_str = f"\n\nCurrent workflow: {len(nodes)} nodes, {len(edges)} edges."
            context_str += f"\nNodes: {json.dumps([{'id': n['id'], 'type': n['type'], 'label': n.get('label', '')} for n in nodes], indent=2)}"
            if edges:
                context_str += f"\nEdges: {json.dumps(edges, indent=2)}"

    # Build messages for the API
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # Add recent chat history (last 10 messages)
    for msg in _CHAT_HISTORY[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current message with context
    user_message = req.message
    if context_str:
        user_message += context_str
    
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Call OpenAI
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        
        assistant_message = response.choices[0].message.content or ""
        
        # Try to parse as JSON first
        result = {
            "action": "chat",
            "message": assistant_message,
            "nodes": [],
            "edges": []
        }
        
        try:
            parsed = json.loads(assistant_message)
            if isinstance(parsed, dict):
                result.update(parsed)
                # Ensure message exists
                if "message" not in result:
                    result["message"] = "Action prepared."
        except json.JSONDecodeError:
            # Not JSON, treat as plain text response
            result["message"] = assistant_message
        
        # Store in history
        _CHAT_HISTORY.append({
            "role": "user",
            "content": req.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        _CHAT_HISTORY.append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Trim history if too long
        if len(_CHAT_HISTORY) > _MAX_HISTORY:
            _CHAT_HISTORY[:] = _CHAT_HISTORY[-_MAX_HISTORY:]
        
        return ChatResponse(
            id=uuid4().hex,
            **result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )

@llm_router.get("/history", response_model=ChatHistory)
async def get_history():
    """
    Get the chat history.
    """
    messages = [
        ChatMessage(
            role=msg["role"],
            content=msg["content"],
            timestamp=datetime.fromisoformat(msg["timestamp"]) if isinstance(msg.get("timestamp"), str) else datetime.utcnow()
        )
        for msg in _CHAT_HISTORY
    ]
    return ChatHistory(messages=messages)

@llm_router.delete("/history")
async def clear_history():
    """
    Clear the chat history.
    """
    _CHAT_HISTORY.clear()
    return {"ok": True, "message": "Chat history cleared"}

__all__ = ["llm_router"]
