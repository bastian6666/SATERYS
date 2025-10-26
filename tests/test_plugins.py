# tests/test_plugins.py
"""
Unit tests for the plugin system.

Tests that plugins can register routes and that endpoints are accessible.
"""
import pytest
from fastapi import FastAPI, APIRouter, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

from saterys.server.plugins import plugin_router
from saterys.server.bootstrap import CoreBridge


def test_plugin_router_exists():
    """Test that plugin_router is properly initialized"""
    assert plugin_router is not None
    assert plugin_router.prefix == "/plugins"


def test_plugin_registration():
    """Test that a minimal plugin can register routes"""
    # Create a fresh test app
    test_app = FastAPI()
    test_plugin_router = APIRouter(prefix="/plugins")
    
    # Create a test plugin router
    plugin_sub_router = APIRouter(prefix="/starter")
    
    class TestBody(BaseModel):
        msg: str
    
    @plugin_sub_router.post("/echo")
    def test_echo(body: TestBody):
        return {"ok": True, "echo": body.msg}
    
    # Register the test router
    test_plugin_router.include_router(plugin_sub_router)
    test_app.include_router(test_plugin_router)
    
    # Test the endpoint through the app
    client = TestClient(test_app)
    response = client.post(
        "/plugins/starter/echo",
        json={"msg": "hello"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["echo"] == "hello"


def test_core_bridge_creation():
    """Test that CoreBridge can be instantiated with required attributes"""
    def mock_require_jwt():
        return None
    
    core = CoreBridge(plugin_router, mock_require_jwt)
    
    assert core.plugin_router is not None
    assert core.require_jwt is not None
    assert core.plugin_router.prefix == "/plugins"


def test_plugin_simulation():
    """Test simulating a full plugin registration flow"""
    # Create a test app
    test_app = FastAPI()
    test_plugin_router = APIRouter(prefix="/plugins")
    
    # Simulate a plugin registration function
    def register_test_plugin(core):
        r = APIRouter(prefix="/starter")
        
        class Body(BaseModel):
            msg: str
        
        @r.post("/echo")
        def echo(b: Body):
            return {"ok": True, "echo": b.msg}
        
        core.plugin_router.include_router(r)
    
    # Create CoreBridge and register plugin BEFORE including router in app
    def mock_jwt():
        return None
    
    core = CoreBridge(test_plugin_router, mock_jwt)
    register_test_plugin(core)
    
    # NOW include the router in the app
    test_app.include_router(test_plugin_router)
    
    # Test the endpoint
    client = TestClient(test_app)
    response = client.post(
        "/plugins/starter/echo",
        json={"msg": "test"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["echo"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
