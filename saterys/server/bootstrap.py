# saterys/server/bootstrap.py
"""
Plugin loader using importlib.metadata entry points.

External Python packages can register themselves under the 'saterys.plugins' group
and provide a register(core: CoreBridge) function to add routes and access core services.
"""
from importlib.metadata import entry_points
from typing import Callable
import sys
import os


class CoreBridge:
    """
    Bridge object passed to plugins, providing access to core services.
    
    Attributes:
        plugin_router: FastAPI router where plugins can mount sub-routers
        require_jwt: Authentication dependency (if available)
    """
    def __init__(self, plugin_router, require_jwt):
        self.plugin_router = plugin_router
        self.require_jwt = require_jwt


def load_plugins(core: CoreBridge):
    """
    Discover and load all plugins registered under 'saterys.plugins' entry point group.
    
    Each plugin's register function is called with the CoreBridge instance.
    """
    # Python 3.9+ compatible entry_points access
    try:
        # Python 3.10+
        eps = entry_points(group="saterys.plugins")
    except TypeError:
        # Python 3.9
        eps = entry_points().get("saterys.plugins", [])
    
    for ep in eps:
        try:
            register = ep.load()
            register(core)
            print(f"✓ Loaded plugin: {ep.name} ({ep.value})")
        except Exception as e:
            print(f"✗ Failed to load plugin {ep.name}: {e}")
    
    # Also try to load plugins from ./plugins directory (development mode)
    plugins_dir = os.path.join(os.getcwd(), "plugins")
    if os.path.isdir(plugins_dir) and plugins_dir not in sys.path:
        sys.path.insert(0, plugins_dir)
        
    # Try loading common plugin names
    dev_plugins = ["saterys_plugin_starter"]
    for plugin_name in dev_plugins:
        try:
            module = __import__(plugin_name)
            if hasattr(module, 'register'):
                module.register(core)
                print(f"✓ Loaded dev plugin: {plugin_name}")
        except ImportError:
            pass  # Plugin not available in dev mode
        except Exception as e:
            print(f"✗ Failed to load dev plugin {plugin_name}: {e}")

