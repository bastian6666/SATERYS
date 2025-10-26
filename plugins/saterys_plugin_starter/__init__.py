"""
SATERYS Starter Plugin

This plugin demonstrates how to create a SATERYS plugin that:
- Registers backend API endpoints
- Integrates with authentication (if available)

The plugin adds a simple echo endpoint at /plugins/starter/echo
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel


def register(core):
    """
    Plugin registration function called by SATERYS on startup.
    
    Args:
        core: CoreBridge instance providing access to:
            - core.plugin_router: FastAPI router for mounting plugin routes
            - core.require_jwt: Authentication dependency (if configured)
    """
    # Create a router for this plugin's endpoints
    router = APIRouter(prefix="/starter")
    
    # Define request/response models
    class EchoBody(BaseModel):
        msg: str
    
    class EchoResponse(BaseModel):
        ok: bool
        echo: str
    
    @router.post("/echo", response_model=EchoResponse)
    def echo(body: EchoBody, _user=Depends(core.require_jwt)):
        """
        Simple echo endpoint that returns the message back.
        
        This demonstrates:
        - Basic POST endpoint
        - Request/response with Pydantic models
        - Optional authentication with require_jwt dependency
        """
        return EchoResponse(ok=True, echo=body.msg)
    
    # Mount the plugin router
    core.plugin_router.include_router(router)
    print("✓ Starter plugin registered: /plugins/starter/echo")
