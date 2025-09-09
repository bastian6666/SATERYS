# 🔌 SATERYS API Reference

SATERYS provides a comprehensive REST API built with FastAPI. This reference covers all available endpoints, request/response formats, and integration examples.

## 🌐 Base URL

```
http://localhost:8000
```

When running in production, replace with your actual host and port.

---

## 🔍 API Overview

### Endpoint Categories

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| 🧩 **Nodes** | `/node_types`, `/run_node` | Plugin management and execution |
| 🗺️ **Preview** | `/preview/*` | Raster visualization and mapping |
| 📄 **Static** | `/`, `/static/*` | Frontend and assets |

### Authentication

SATERYS currently runs without authentication. For production deployments, consider adding:
- API keys
- JWT tokens  
- OAuth integration
- Rate limiting

---

## 🧩 Node Management

### GET `/node_types`

Get all available plugin types and their configuration.

#### Request

```http
GET /node_types HTTP/1.1
Host: localhost:8000
```

#### Response

```json
{
  "types": [
    {
      "name": "hello",
      "default_args": {
        "name": "world"
      }
    },
    {
      "name": "raster.ndvi",
      "default_args": {
        "red_band": 4,
        "nir_band": 5,
        "output_path": "",
        "dtype": "float32",
        "nodata": -9999.0
      }
    },
    {
      "name": "raster.input",
      "default_args": {
        "path": "/absolute/path/to/file.tif"
      }
    }
  ]
}
```

#### Example Usage

```python
import requests

response = requests.get("http://localhost:8000/node_types")
node_types = response.json()

# Find NDVI node
ndvi_node = next(
    (nt for nt in node_types["types"] if nt["name"] == "raster.ndvi"),
    None
)

print(f"NDVI default args: {ndvi_node['default_args']}")
```

```javascript
// JavaScript/Node.js
const response = await fetch('http://localhost:8000/node_types');
const data = await response.json();

console.log('Available node types:', data.types.map(t => t.name));
```

```bash
# curl
curl -X GET "http://localhost:8000/node_types" \
     -H "accept: application/json"
```

---

### POST `/run_node`

Execute a specific node with parameters and inputs.

#### Request

```http
POST /run_node HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "nodeId": "unique-node-identifier",
  "type": "plugin-name", 
  "args": {
    "parameter1": "value1",
    "parameter2": 42
  },
  "inputs": {
    "upstream_node_id": {
      "type": "data_type",
      "data": "..."
    }
  }
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `nodeId` | string | ✅ | Unique identifier for this execution |
| `type` | string | ✅ | Plugin name (from `/node_types`) |
| `args` | object | ❌ | Plugin parameters (defaults to `{}`) |
| `inputs` | object | ❌ | Data from upstream nodes (defaults to `{}`) |

#### Response - Success

```json
{
  "ok": true,
  "output": {
    "type": "result_type",
    "data": "...",
    "metadata": {
      "processing_time": 1.23,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Response - Error

```json
{
  "ok": false,
  "error": "Detailed error message explaining what went wrong"
}
```

#### Example Usage

**Hello World Example:**

```python
import requests

payload = {
    "nodeId": "hello-1",
    "type": "hello",
    "args": {"name": "SATERYS"},
    "inputs": {}
}

response = requests.post(
    "http://localhost:8000/run_node", 
    json=payload
)

result = response.json()
print(result["output"])  # {"text": "hello SATERYS"}
```

**NDVI Calculation Example:**

```python
import requests

# First, run a raster input node
raster_payload = {
    "nodeId": "input-1",
    "type": "raster.input", 
    "args": {"path": "/path/to/landsat8.tif"},
    "inputs": {}
}

raster_response = requests.post(
    "http://localhost:8000/run_node",
    json=raster_payload
)
raster_output = raster_response.json()["output"]

# Then, run NDVI calculation
ndvi_payload = {
    "nodeId": "ndvi-1",
    "type": "raster.ndvi",
    "args": {
        "red_band": 4,
        "nir_band": 5,
        "output_path": "./results/ndvi.tif"
    },
    "inputs": {
        "input-1": raster_output  # Pass raster data from previous node
    }
}

ndvi_response = requests.post(
    "http://localhost:8000/run_node",
    json=ndvi_payload  
)

print(ndvi_response.json())
```

**Pipeline Execution Example:**

```python
import requests

class SATERYSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def run_node(self, node_id, node_type, args=None, inputs=None):
        payload = {
            "nodeId": node_id,
            "type": node_type,
            "args": args or {},
            "inputs": inputs or {}
        }
        
        response = requests.post(
            f"{self.base_url}/run_node",
            json=payload
        )
        
        result = response.json()
        if not result["ok"]:
            raise Exception(f"Node execution failed: {result['error']}")
            
        return result["output"]

# Usage
client = SATERYSClient()

# Build a pipeline programmatically
raster = client.run_node(
    "load-raster", "raster.input",
    args={"path": "/data/satellite.tif"}
)

ndvi = client.run_node(
    "calc-ndvi", "raster.ndvi", 
    args={"red_band": 3, "nir_band": 4},
    inputs={"load-raster": raster}
)

print(f"NDVI calculated: {ndvi['path']}")
```

---

## 🗺️ Raster Preview API

The preview system allows you to visualize raster data on interactive maps.

### POST `/preview/register`

Register a raster file for map preview.

#### Request

```http
POST /preview/register HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "id": "unique-preview-id",
  "path": "/absolute/path/to/raster.tif"
}
```

#### Response

```json
{
  "ok": true,
  "id": "unique-preview-id",
  "path": "/absolute/path/to/raster.tif"
}
```

#### Example Usage

```python
import requests

payload = {
    "id": "landsat-scene-1",
    "path": "/data/landsat8_rgb.tif"
}

response = requests.post(
    "http://localhost:8000/preview/register",
    json=payload
)

print(response.json())
```

---

### GET `/preview/bounds/{preview_id}`

Get geographic bounds of a registered raster.

#### Request

```http
GET /preview/bounds/landsat-scene-1 HTTP/1.1
Host: localhost:8000
```

#### Response

```json
{
  "bounds": [-122.5, 37.5, -122.0, 38.0],
  "crs": "EPSG:4326"
}
```

The bounds format is `[west, south, east, north]` in the specified coordinate system.

---

### GET `/preview/tile/{preview_id}/{z}/{x}/{y}.png`

Get a map tile for the registered raster.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `preview_id` | string | Registered preview ID |
| `z` | integer | Zoom level (0-18) |
| `x` | integer | Tile X coordinate |
| `y` | integer | Tile Y coordinate |
| `indexes` | string (query) | Band indices (e.g., `?indexes=4,3,2`) |

#### Request

```http
GET /preview/tile/landsat-scene-1/10/163/395.png?indexes=4,3,2 HTTP/1.1
Host: localhost:8000
```

#### Response

Returns a PNG image (binary data) with appropriate caching headers.

#### Example Usage

**Leaflet Integration:**

```javascript
// Add SATERYS raster as Leaflet tile layer
const rasterLayer = L.tileLayer(
  'http://localhost:8000/preview/tile/landsat-scene-1/{z}/{x}/{y}.png?indexes=4,3,2',
  {
    attribution: 'SATERYS',
    maxZoom: 18
  }
);

// Get bounds and fit map
fetch('http://localhost:8000/preview/bounds/landsat-scene-1')
  .then(response => response.json())
  .then(data => {
    const bounds = L.latLngBounds(
      [data.bounds[1], data.bounds[0]],  // SW
      [data.bounds[3], data.bounds[2]]   // NE
    );
    
    map.fitBounds(bounds);
    rasterLayer.addTo(map);
  });
```

**OpenLayers Integration:**

```javascript
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';

const rasterLayer = new TileLayer({
  source: new XYZ({
    url: 'http://localhost:8000/preview/tile/landsat-scene-1/{z}/{x}/{y}.png?indexes=4,3,2',
    crossOrigin: 'anonymous'
  })
});

map.addLayer(rasterLayer);
```

---

## 📄 Frontend Endpoints

### GET `/`

Serves the main SATERYS web application.

#### Request

```http
GET / HTTP/1.1
Host: localhost:8000
```

#### Response

Returns the main HTML interface for SATERYS.

---

### GET `/static/{path}`

Serves static assets (CSS, JS, images).

#### Request

```http
GET /static/assets/index.js HTTP/1.1
Host: localhost:8000
```

---

## 🔧 Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid parameters or missing required fields |
| 404 | Not Found | Endpoint or resource doesn't exist |  
| 422 | Unprocessable Entity | Request validation failed |
| 500 | Internal Server Error | Plugin execution error or server issue |

### Error Response Format

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🧪 Testing the API

### Using curl

```bash
# Get node types
curl -X GET "http://localhost:8000/node_types"

# Run a simple node
curl -X POST "http://localhost:8000/run_node" \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "test-1", 
    "type": "hello",
    "args": {"name": "API Test"}
  }'

# Register preview
curl -X POST "http://localhost:8000/preview/register" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-raster",
    "path": "/path/to/test.tif" 
  }'
```

### Using Python requests

```python
import requests

class SATERYSTestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def test_connection(self):
        """Test basic connectivity"""
        response = requests.get(f"{self.base_url}/node_types")
        return response.status_code == 200
        
    def test_hello_node(self):
        """Test basic node execution"""
        payload = {
            "nodeId": "test-hello",
            "type": "hello", 
            "args": {"name": "Test"}
        }
        
        response = requests.post(f"{self.base_url}/run_node", json=payload)
        result = response.json()
        
        assert result["ok"] == True
        assert "hello Test" in result["output"]["text"]
        
    def test_error_handling(self):
        """Test error responses"""
        payload = {
            "nodeId": "test-error",
            "type": "nonexistent.node"
        }
        
        response = requests.post(f"{self.base_url}/run_node", json=payload)
        result = response.json()
        
        assert result["ok"] == False
        assert "unknown node type" in result["error"]

# Run tests
client = SATERYSTestClient()
assert client.test_connection(), "Connection failed"
client.test_hello_node()
client.test_error_handling()
print("✅ All API tests passed!")
```

---

## 📚 Integration Examples

### Workflow Automation Script

```python
#!/usr/bin/env python3
"""
Automated NDVI processing workflow using SATERYS API
"""

import requests
import time
import os
from pathlib import Path

class SATERYSWorkflow:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        
    def run_node(self, node_id, node_type, args=None, inputs=None):
        """Execute a node and return output"""
        payload = {
            "nodeId": node_id,
            "type": node_type, 
            "args": args or {},
            "inputs": inputs or {}
        }
        
        response = requests.post(f"{self.api_url}/run_node", json=payload)
        result = response.json()
        
        if not result["ok"]:
            raise Exception(f"Node {node_id} failed: {result['error']}")
            
        return result["output"]
        
    def process_landsat_scene(self, scene_path, output_dir):
        """Process a Landsat scene to generate NDVI"""
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"🛰️ Processing scene: {scene_path}")
        
        # 1. Load raster
        print("📂 Loading raster...")
        raster = self.run_node(
            "load-scene",
            "raster.input",
            args={"path": str(scene_path)}
        )
        
        # 2. Calculate NDVI
        print("🌿 Calculating NDVI...")
        ndvi_output = os.path.join(output_dir, "ndvi.tif")
        ndvi = self.run_node(
            "calc-ndvi",
            "raster.ndvi",
            args={
                "red_band": 4,    # Landsat 8 Red
                "nir_band": 5,    # Landsat 8 NIR
                "output_path": ndvi_output
            },
            inputs={"load-scene": raster}
        )
        
        # 3. Register for preview
        print("🗺️ Registering preview...")
        requests.post(
            f"{self.api_url}/preview/register",
            json={
                "id": f"ndvi-{int(time.time())}",
                "path": ndvi["path"]
            }
        )
        
        print(f"✅ NDVI saved to: {ndvi['path']}")
        return ndvi

# Usage
if __name__ == "__main__":
    workflow = SATERYSWorkflow()
    
    # Process multiple scenes
    scenes = [
        "/data/landsat/scene1.tif",
        "/data/landsat/scene2.tif" 
    ]
    
    for scene in scenes:
        if os.path.exists(scene):
            try:
                result = workflow.process_landsat_scene(scene, "./results")
                print(f"Processed: {scene}")
            except Exception as e:
                print(f"Failed to process {scene}: {e}")
```

### Jupyter Notebook Integration

```python
# Jupyter notebook cell
import requests
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show

def saterys_ndvi(raster_path):
    """Calculate NDVI using SATERYS API and display result"""
    
    # Execute NDVI calculation
    payload = {
        "nodeId": f"notebook-ndvi-{id(raster_path)}",
        "type": "raster.ndvi", 
        "args": {"red_band": 4, "nir_band": 5},
        "inputs": {
            "raster_input": {
                "type": "raster",
                "path": raster_path
            }
        }
    }
    
    response = requests.post("http://localhost:8000/run_node", json=payload)
    result = response.json()
    
    if not result["ok"]:
        raise Exception(result["error"])
        
    # Display result
    ndvi_path = result["output"]["path"]
    
    with rasterio.open(ndvi_path) as src:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        show(src, ax=ax, cmap='RdYlGn', title='NDVI Result')
        plt.tight_layout()
        plt.show()
        
    return ndvi_path

# Usage in notebook
ndvi_result = saterys_ndvi("/path/to/landsat.tif")
print(f"NDVI saved to: {ndvi_result}")
```

---

## 🔐 Security Considerations

### Production Deployment

For production use, implement these security measures:

1. **Authentication**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   def verify_token(token: str = Depends(security)):
       # Verify JWT or API key
       if not is_valid_token(token.credentials):
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token"
           )
   
   @app.post("/run_node", dependencies=[Depends(verify_token)])
   def run_node_secure(payload: RunPayload):
       # Protected endpoint
       pass
   ```

2. **Input Validation**
   ```python
   from pydantic import BaseModel, validator
   
   class RunPayload(BaseModel):
       nodeId: str
       type: str
       args: dict = {}
       inputs: dict = {}
       
       @validator('nodeId')
       def validate_node_id(cls, v):
           if not re.match(r'^[a-zA-Z0-9\-_]+$', v):
               raise ValueError('Invalid node ID format')
           return v
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/run_node")
   @limiter.limit("10/minute")
   def run_node_limited(request: Request, payload: RunPayload):
       # Rate-limited endpoint
       pass
   ```

---

<div align="center">

**Build amazing integrations with SATERYS! 🚀**

[⬅️ Plugin Development](plugins.md) | [Examples ➡️](../examples/)

</div>