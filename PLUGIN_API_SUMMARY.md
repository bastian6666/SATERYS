# Plugin API - PR Summary

## Implementation Complete ✅

This PR implements a **plugin-first extension surface** for SATERYS, allowing developers to add new functionality without modifying core code.

## What Was Implemented

### 1. Backend Plugin Infrastructure

**Files Created:**
- `saterys/server/plugins.py` - Plugin router
- `saterys/server/bootstrap.py` - Entry-point loader with CoreBridge
- `tests/test_plugins.py` - Unit tests (4 passing)

**Changes:**
- `saterys/app.py` - Plugin loading and router integration
- Added development mode plugin discovery from `./plugins/` directory

**API:**
- Plugins register via Python entry points: `saterys.plugins`
- `CoreBridge` provides access to plugin_router and require_jwt
- Endpoints mount at `/plugins/<plugin-name>/...`

### 2. Frontend UI Registry

**Files Created:**
- `saterys/web/src/core/context.ts` - AppContext interface
- `saterys/web/src/core/registry.ts` - UI contribution registries
- `saterys/web/src/core/nodes.ts` - Node-graph plugin system
- `saterys/web/src/plugins.manifest.ts` - Plugin import manifest

**Changes:**
- `saterys/web/src/main.ts` - Import manifest before bootstrap
- `saterys/web/src/App.svelte` - Plugin toolbar integration, toast system
- `saterys/web/package.json` - Build scripts for plugins

**API:**
- `registerToolbar()` - Add toolbar buttons
- `registerMenu()` - Add menu items
- `registerShortcut()` - Add keyboard shortcuts
- `registerOverlay()` - Add canvas overlays
- `registerNodeType()` - Add custom processing nodes
- `getContext()` / `setContext()` - Access app services

### 3. Starter Plugins

**Python Plugin:**
- Location: `plugins/saterys_plugin_starter/`
- Implements: Echo endpoint at `/plugins/starter/echo`
- Demonstrates: FastAPI router integration, Pydantic models, auth

**UI Plugin:**
- Location: `saterys/web/plugins/@saterys/plugin-starter/`
- Implements: "Hello Plugin" toolbar button
- Demonstrates: API calls, toast notifications, job runner

### 4. Documentation

**Files Created:**
- `docs/plugin-api.md` - Comprehensive plugin API reference
- Updated `README.md` - Added Plugins section with quick start

## How to Use

### Run the Demo

```bash
# 1. Build frontend (includes plugins)
cd saterys/web
npm install
npm run build
cd ../..

# 2. Start server
python -m saterys

# 3. Open browser to http://localhost:8000

# 4. Click "Hello Plugin" button
#    → Toast: "Plugin button clicked!"
#    → Calls /plugins/starter/echo
#    → Toast: "Echo OK: Hello from UI plugin!"
```

### Create a Backend Plugin

```python
# plugins/my_plugin/__init__.py
from fastapi import APIRouter
from pydantic import BaseModel

def register(core):
    router = APIRouter(prefix="/myplugin")
    
    class Body(BaseModel):
        value: str
    
    @router.post("/action")
    def action(body: Body):
        return {"result": f"Processed: {body.value}"}
    
    core.plugin_router.include_router(router)
```

```toml
# plugins/my_plugin/pyproject.toml
[project]
name = "my_plugin"
version = "0.1.0"

[project.entry-points."saterys.plugins"]
myplugin = "my_plugin:register"
```

### Create a Frontend Plugin

```typescript
// saterys/web/plugins/@saterys/my-plugin/src/index.ts
import { registerToolbar } from '../../../../src/core/registry';
import { getContext } from '../../../../src/core/context';

registerToolbar({
  id: 'myplugin.action',
  label: 'My Action',
  async run() {
    const ctx = getContext();
    const res = await ctx.api.fetch('/plugins/myplugin/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: 'test' })
    });
    const data = await res.json();
    ctx.toast.success(data.result);
  }
});
```

Update `saterys/web/src/plugins.manifest.ts`:
```typescript
import '../plugins/@saterys/my-plugin/dist/index.js';
```

## Testing

### Backend Tests
```bash
python -m pytest tests/test_plugins.py -v
# ✅ 4 tests passing
```

### Manual Testing
```bash
# Test backend endpoint
curl -X POST http://localhost:8000/plugins/starter/echo \
  -H "Content-Type: application/json" \
  -d '{"msg":"test"}'
# Returns: {"ok":true,"echo":"test"}
```

## Architecture

### Backend Flow
1. App starts → `_init_plugins()` called
2. Entry points discovered (or ./plugins/ for dev)
3. Each plugin's `register(core)` called
4. Plugins mount sub-routers on `core.plugin_router`
5. Plugin router included in main app
6. Endpoints available at `/plugins/...`

### Frontend Flow
1. `main.ts` imports `plugins.manifest.ts`
2. Manifest imports all plugin modules
3. Plugins call registry functions
4. App.svelte renders registered UI elements
5. User interaction triggers plugin callbacks

## Benefits

✅ **Zero core modification** - Add features without touching core  
✅ **Clean separation** - Plugins are self-contained  
✅ **Type-safe** - Full TypeScript support  
✅ **Hot-reload ready** - Infrastructure supports future hot-reload  
✅ **Tested** - Unit tests verify plugin system  
✅ **Documented** - Complete API reference and examples  

## Future Enhancements

Possible additions to the plugin system:
- Hot-reload for development
- Plugin marketplace/discovery
- Permission system
- Inter-plugin communication
- UI theme hooks
- State management APIs

## Files Changed

**Backend:**
- `saterys/server/__init__.py` (new)
- `saterys/server/plugins.py` (new)
- `saterys/server/bootstrap.py` (new)
- `saterys/app.py` (modified)
- `tests/test_plugins.py` (new)

**Frontend:**
- `saterys/web/src/core/context.ts` (new)
- `saterys/web/src/core/registry.ts` (new)
- `saterys/web/src/core/nodes.ts` (new)
- `saterys/web/src/plugins.manifest.ts` (new)
- `saterys/web/src/main.ts` (modified)
- `saterys/web/src/App.svelte` (modified)
- `saterys/web/package.json` (modified)

**Plugins:**
- `plugins/saterys_plugin_starter/` (new)
- `saterys/web/plugins/@saterys/plugin-starter/` (new)

**Documentation:**
- `docs/plugin-api.md` (new)
- `README.md` (modified)

## Commits

1. `feat(backend): add plugin router and entry-point loader`
2. `feat(frontend): add UI contribution registry and context`
3. `chore(plugins): add starter UI & Python plugins`
4. `docs: add plugin API docs and README section`
