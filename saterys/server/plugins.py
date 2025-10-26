# saterys/server/plugins.py
"""
Plugin router for SATERYS backend extensions.

External plugins can register their own API endpoints under /plugins/<plugin-name>/...
"""
from fastapi import APIRouter

plugin_router = APIRouter(prefix="/plugins")
