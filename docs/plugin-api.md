# Plugin API Documentation

SATERYS provides a plugin-first extension surface that allows you to add new functionality without modifying the core codebase.

## Overview

The plugin system consists of two parts:
- **Backend plugins** (Python): Add new REST API endpoints
- **Frontend plugins** (TypeScript/JavaScript): Add UI elements, canvas overlays, and custom interactions

## Backend Plugins (Python)

Backend plugins use Python's entry points system to register themselves with SATERYS.

### Creating a Backend Plugin

1. **Create a Python package** with a `pyproject.toml`:

```toml
[project]
name = "saterys_plugin_myfeature"
version = "0.1.0"
dependencies = ["fastapi", "pydantic"]

[project.entry-points."saterys.plugins"]
myfeature = "saterys_plugin_myfeature:register"
```

2. **Implement the registration function** in `__init__.py`:

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

def register(core):
    """
    Plugin registration function called by SATERYS on startup.
    
    Args:
        core: CoreBridge with:
            - core.plugin_router: FastAPI router for mounting routes
            - core.require_jwt: Authentication dependency
    """
    router = APIRouter(prefix="/myfeature")
    
    class RequestModel(BaseModel):
        param: str
    
    @router.post("/endpoint")
    def my_endpoint(body: RequestModel, _user=Depends(core.require_jwt)):
        return {"result": f"Processed: {body.param}"}
    
    core.plugin_router.include_router(router)
```

3. **Install the plugin**:

```bash
pip install -e /path/to/your/plugin
```

Your endpoint will be available at `/plugins/myfeature/endpoint`.

### Development Mode

For local development, SATERYS will automatically discover plugins in the `./plugins/` directory:

```bash
# Structure
plugins/
  saterys_plugin_myfeature/
    __init__.py
    pyproject.toml
```

### CoreBridge API

The `core` object passed to your `register()` function provides:

- **`core.plugin_router`**: FastAPI `APIRouter` where you should mount your sub-router
- **`core.require_jwt`**: Authentication dependency (returns user info or None if not authenticated)

## Frontend Plugins (TypeScript/JavaScript)

Frontend plugins register UI contributions through a centralized registry system.

### Creating a Frontend Plugin

1. **Create a TypeScript/JavaScript module**:

```typescript
// plugins/@saterys/my-plugin/src/index.ts
import { registerToolbar, registerOverlay } from 'path/to/core/registry';
import { getContext } from 'path/to/core/context';

// Register a toolbar button
registerToolbar({
  id: 'myplugin.action',
  group: 'analysis',
  label: 'My Action',
  order: 100,
  async run() {
    const ctx = getContext();
    ctx.toast.info('Button clicked!');
    
    // Call backend API
    const res = await ctx.api.fetch('/plugins/myfeature/endpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ param: 'value' })
    });
    
    const data = await res.json();
    ctx.toast.success(`Result: ${data.result}`);
  }
});

// Register a canvas overlay
registerOverlay({
  id: 'myplugin.overlay',
  zIndex: 500,
  draw(g: CanvasRenderingContext2D, view: any, ctx: any) {
    // Draw on the canvas
    g.strokeStyle = '#00ff00';
    g.strokeRect(10, 10, 100, 100);
  }
});
```

2. **Build your plugin**:

```bash
cd plugins/@saterys/my-plugin
npm install
npm run build  # Outputs to dist/index.js
```

3. **Import in the manifest**:

Edit `web/src/plugins.manifest.ts`:

```typescript
import '../plugins/@saterys/my-plugin/dist/index.js';
export {};
```

### Frontend API Reference

#### AppContext

Access the application context in your plugin:

```typescript
import { getContext } from './core/context';

const ctx = getContext();
```

The context provides:

- **`ctx.api.fetch(path, init?)`**: Make HTTP requests (auto-prefixes base URL if needed)
- **`ctx.toast.info(msg)`**: Show info toast
- **`ctx.toast.success(msg)`**: Show success toast
- **`ctx.toast.error(msg)`**: Show error toast
- **`ctx.jobs.run(label, task)`**: Run a background job with progress reporting
- **`ctx.commands.execute(cmd)`**: Execute a command with undo support
- **`ctx.layers`**: Layer management (addFromId, remove, getSelected)
- **`ctx.selection.firstRaster()`**: Get first selected raster
- **`ctx.entitlements.has(flag)`**: Check feature flags
- **`ctx.theme`**: Current theme ('dark' | 'light')

#### Registry Functions

**Toolbar Buttons:**

```typescript
registerToolbar({
  id: string;           // Unique identifier
  group: string;        // Grouping category
  label?: string;       // Button label
  icon?: any;           // SVG or icon component
  order?: number;       // Sort order (default: 0)
  when?: string;        // Conditional expression (future)
  run: Command;         // Function to execute
});
```

**Menu Items:**

```typescript
registerMenu({
  id: string;
  menu: 'layer/context' | 'app/main' | 'canvas/context';
  order?: number;
  when?: string;
  run: Command;
});
```

**Keyboard Shortcuts:**

```typescript
registerShortcut('Ctrl+K', async (ctx) => {
  // Handle shortcut
});
```

**Canvas Overlays:**

```typescript
registerOverlay({
  id: string;
  zIndex?: number;      // Stack order (default: 0)
  draw: (g: CanvasRenderingContext2D, view: any, ctx: AppContext) => void;
});
```

**Custom Nodes:**

```typescript
registerNodeType({
  type: string;         // Unique node type identifier
  label: string;        // Display name
  inputs: NodeIO[];     // Input sockets
  outputs: NodeIO[];    // Output sockets
  run: async (ctx, inputs) => { /* processing */ },
  serialize?: (node) => any;
  deserialize?: (node, data) => void;
});
```

## Example: Full Plugin

See the starter plugins for complete examples:
- **Backend**: `plugins/saterys_plugin_starter/`
- **Frontend**: `saterys/web/plugins/@saterys/plugin-starter/`

## Best Practices

1. **Namespace your IDs**: Use `plugin-name.feature` format (e.g., `myplugin.analyze`)
2. **Error handling**: Always handle errors and show user-friendly messages via toasts
3. **Progress reporting**: Use `ctx.jobs.run()` for long-running operations
4. **Authentication**: Use `core.require_jwt` dependency for protected endpoints
5. **Testing**: Test both backend endpoints and UI integration

## Troubleshooting

**Backend plugin not loading:**
- Check the plugin is installed or in `./plugins/` directory
- Verify the entry point name matches in `pyproject.toml`
- Look for error messages in console output

**Frontend plugin not appearing:**
- Ensure the plugin is built (`npm run build`)
- Check it's imported in `plugins.manifest.ts`
- Verify the registration calls are executed (check console logs)
- Rebuild the main app (`npm run build` in web/)

## Future Enhancements

Planned features for the plugin system:
- Plugin marketplace and discovery
- Hot-reload for development
- Plugin permissions and sandboxing
- UI theme customization hooks
- State management APIs
- Inter-plugin communication
