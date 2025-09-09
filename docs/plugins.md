# 🧩 Plugin Development Guide

SATERYS is built around a powerful plugin system that allows you to extend the platform with custom processing nodes. This guide will teach you everything you need to know about creating, distributing, and maintaining SATERYS plugins.

## 🎯 Plugin Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SATERYS PLUGIN SYSTEM                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   🔍 Discovery  │  ⚙️ Execution   │     🔌 Integration      │
│                 │                 │                         │
│ • Auto-scan     │ • Args parsing  │ • FastAPI endpoints     │
│ • Hot reload    │ • Input validation • Web UI integration   │
│ • Type registry │ • Error handling │ • Map previews         │
│ • Metadata      │ • Result caching │ • Logging system       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Plugin Lifecycle

1. **📂 Discovery**: SATERYS scans `nodes/` directories
2. **📋 Registration**: Plugin metadata is extracted
3. **🎨 UI Integration**: Node appears in the interface
4. **⚡ Execution**: User triggers node execution
5. **📤 Output**: Results flow to downstream nodes

---

## 🚀 Quick Start

### Minimal Plugin

Create `nodes/hello_world.py`:

```python
NAME = "hello.world"

def run(args, inputs, context):
    return {"message": "Hello from my plugin!"}
```

That's it! Restart SATERYS and your plugin appears in the node dropdown.

---

## 📝 Plugin Structure

### Required Components

```python
# nodes/my_plugin.py

# 🏷️ REQUIRED: Unique plugin identifier
NAME = "category.my_plugin"

# ⚙️ OPTIONAL: Default parameters
DEFAULT_ARGS = {
    "param1": "default_value",
    "param2": 42,
    "enable_feature": True
}

# 🎯 REQUIRED: Main execution function
def run(args, inputs, context):
    """
    Execute the plugin logic.
    
    Args:
        args (dict): User-configured parameters
        inputs (dict): Data from upstream nodes
        context (dict): Runtime information
        
    Returns:
        dict: Output data for downstream nodes
    """
    # Your processing logic here
    return {"result": "success"}
```

### Optional Components

```python
# 📖 Plugin documentation
__doc__ = """
This plugin does amazing things with geospatial data.
Supports multiple input formats and provides rich outputs.
"""

# 🔢 Version information
__version__ = "1.0.0"

# 👤 Author information  
__author__ = "Your Name <your.email@example.com>"

# 🏷️ Plugin categories/tags
CATEGORIES = ["geospatial", "analysis", "remote_sensing"]

# 📋 Input/output schema (for validation)
INPUT_SCHEMA = {
    "raster": {"type": "raster", "required": True},
    "vector": {"type": "vector", "required": False}
}

OUTPUT_SCHEMA = {
    "result": {"type": "raster", "description": "Processed output"}
}
```

---

## 🛠️ Plugin Types and Patterns

### 1. Simple Data Processor

```python
# nodes/text_processor.py

NAME = "text.processor"
DEFAULT_ARGS = {
    "operation": "uppercase",
    "prefix": ""
}

def run(args, inputs, context):
    # Get text from inputs or args
    text = ""
    for inp in inputs.values():
        if isinstance(inp, dict) and "text" in inp:
            text = inp["text"]
            break
    
    if not text:
        text = args.get("text", "")
    
    # Process text
    operation = args.get("operation", "uppercase")
    prefix = args.get("prefix", "")
    
    if operation == "uppercase":
        result = text.upper()
    elif operation == "lowercase":
        result = text.lower()
    elif operation == "title":
        result = text.title()
    else:
        result = text
        
    return {
        "text": f"{prefix}{result}",
        "operation_applied": operation
    }
```

### 2. Geospatial Raster Processor

```python
# nodes/raster_filter.py

import os
import numpy as np
import rasterio
from rasterio.enums import Resampling

NAME = "raster.filter"
DEFAULT_ARGS = {
    "filter_type": "gaussian",
    "kernel_size": 3,
    "sigma": 1.0,
    "output_path": ""
}

def run(args, inputs, context):
    # Find raster input
    raster_input = None
    for inp in inputs.values():
        if isinstance(inp, dict) and inp.get("type") == "raster":
            raster_input = inp
            break
    
    if not raster_input:
        raise ValueError("No raster input found")
    
    # Get parameters
    filter_type = args.get("filter_type", "gaussian")
    kernel_size = int(args.get("kernel_size", 3))
    sigma = float(args.get("sigma", 1.0))
    output_path = args.get("output_path", "")
    
    # Generate output path if not provided
    if not output_path:
        cache_dir = os.environ.get("RASTER_CACHE", "./data/cache")
        os.makedirs(cache_dir, exist_ok=True)
        output_path = os.path.join(
            cache_dir, 
            f"filtered_{context.get('nodeId', 'unknown')}.tif"
        )
    
    # Process raster
    with rasterio.open(raster_input["path"]) as src:
        # Read data
        data = src.read()
        
        # Apply filter
        if filter_type == "gaussian":
            from scipy import ndimage
            filtered_data = np.zeros_like(data)
            for i in range(data.shape[0]):
                filtered_data[i] = ndimage.gaussian_filter(
                    data[i], sigma=sigma
                )
        elif filter_type == "median":
            from scipy import ndimage
            filtered_data = np.zeros_like(data)
            for i in range(data.shape[0]):
                filtered_data[i] = ndimage.median_filter(
                    data[i], size=kernel_size
                )
        else:
            filtered_data = data  # No filtering
        
        # Write output
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=src.count,
            dtype=filtered_data.dtype,
            crs=src.crs,
            transform=src.transform,
            nodata=src.nodata
        ) as dst:
            dst.write(filtered_data)
    
    # Return raster payload
    with rasterio.open(output_path) as src:
        bounds = src.bounds
        return {
            "type": "raster",
            "path": os.path.abspath(output_path),
            "driver": src.driver,
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "dtype": str(src.dtypes[0]),
            "crs": str(src.crs) if src.crs else None,
            "transform": [src.transform[i] for i in range(6)],
            "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
            "nodata": src.nodata,
            "meta": {
                "filter_applied": filter_type,
                "parameters": {
                    "kernel_size": kernel_size,
                    "sigma": sigma
                }
            }
        }
```

### 3. Multi-Input Processor

```python
# nodes/raster_calculator.py

NAME = "raster.calculator"
DEFAULT_ARGS = {
    "expression": "A + B",  # Simple expression parser
    "output_dtype": "float32"
}

def run(args, inputs, context):
    import numpy as np
    import rasterio
    
    # Collect raster inputs
    rasters = {}
    for key, inp in inputs.items():
        if isinstance(inp, dict) and inp.get("type") == "raster":
            rasters[key] = inp
    
    if len(rasters) < 1:
        raise ValueError("At least one raster input required")
    
    expression = args.get("expression", "A + B")
    output_dtype = args.get("output_dtype", "float32")
    
    # Read all rasters (assuming same dimensions)
    arrays = {}
    reference_raster = None
    
    for name, raster in rasters.items():
        with rasterio.open(raster["path"]) as src:
            if reference_raster is None:
                reference_raster = src
                profile = src.profile
            arrays[name.upper()] = src.read(1).astype(np.float64)
    
    # Simple expression evaluation (expand as needed)
    # WARNING: This is a simplified example - use a proper parser for production
    result_array = None
    
    if expression == "A + B" and "A" in arrays and "B" in arrays:
        result_array = arrays["A"] + arrays["B"]
    elif expression == "A - B" and "A" in arrays and "B" in arrays:
        result_array = arrays["A"] - arrays["B"]
    elif expression == "A * B" and "A" in arrays and "B" in arrays:
        result_array = arrays["A"] * arrays["B"]
    elif expression == "A / B" and "A" in arrays and "B" in arrays:
        # Handle division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            result_array = np.divide(arrays["A"], arrays["B"])
            result_array[~np.isfinite(result_array)] = 0
    else:
        # Fallback: return first array
        result_array = next(iter(arrays.values()))
    
    # Save result
    output_path = f"./data/cache/calc_{context.get('nodeId', 'result')}.tif"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    profile.update(dtype=output_dtype, count=1)
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(result_array.astype(output_dtype), 1)
    
    # Return result
    with rasterio.open(output_path) as src:
        bounds = src.bounds
        return {
            "type": "raster",
            "path": os.path.abspath(output_path),
            "width": src.width,
            "height": src.height,
            "expression": expression,
            "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
        }
```

---

## 🔧 Advanced Features

### Error Handling

```python
def run(args, inputs, context):
    try:
        # Your processing logic
        result = process_data(args, inputs)
        
        return {
            "status": "success",
            "data": result
        }
        
    except FileNotFoundError as e:
        raise ValueError(f"Input file not found: {e}")
        
    except Exception as e:
        # Log the error but provide user-friendly message
        import traceback
        print(f"Plugin error: {traceback.format_exc()}")
        
        raise RuntimeError(f"Processing failed: {str(e)}")
```

### Caching and Performance

```python
import hashlib
import os
import pickle

def run(args, inputs, context):
    # Generate cache key
    cache_key = hashlib.sha256(
        str(sorted(args.items()) + sorted(inputs.items())).encode()
    ).hexdigest()
    
    cache_file = f"./data/cache/{NAME}_{cache_key}.pkl"
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Process data
    result = expensive_computation(args, inputs)
    
    # Save to cache
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)
    
    return result
```

### Progress Reporting

```python
def run(args, inputs, context):
    steps = ["loading", "processing", "saving"]
    
    for i, step in enumerate(steps):
        print(f"Progress: {step} ({i+1}/{len(steps)})")
        
        if step == "loading":
            data = load_data(inputs)
        elif step == "processing":
            result = process_data(data, args)
        elif step == "saving":
            save_result(result)
    
    return {"status": "completed", "steps": len(steps)}
```

---

## 🧪 Testing Plugins

### Basic Unit Testing

```python
# test_my_plugin.py

import sys
import os
sys.path.append('nodes')

from my_plugin import run, NAME, DEFAULT_ARGS

def test_basic_functionality():
    """Test basic plugin execution"""
    args = DEFAULT_ARGS.copy()
    inputs = {}
    context = {"nodeId": "test-node"}
    
    result = run(args, inputs, context)
    
    assert isinstance(result, dict)
    assert "result" in result

def test_with_inputs():
    """Test plugin with input data"""
    args = {"param1": "test_value"}
    inputs = {
        "upstream_node": {
            "type": "text",
            "data": "test input"
        }
    }
    context = {"nodeId": "test-node-2"}
    
    result = run(args, inputs, context)
    
    # Add your specific assertions here
    assert result is not None

if __name__ == "__main__":
    test_basic_functionality()
    test_with_inputs()
    print("✅ All tests passed!")
```

### Integration Testing

```python
# test_integration.py

import requests
import json

def test_plugin_via_api():
    """Test plugin through SATERYS API"""
    
    # Start SATERYS server first: `saterys --port 8001`
    base_url = "http://localhost:8001"
    
    # Check if plugin is registered
    response = requests.get(f"{base_url}/node_types")
    node_types = response.json()["types"]
    
    plugin_found = any(nt["name"] == "my.plugin" for nt in node_types)
    assert plugin_found, "Plugin not found in node types"
    
    # Execute plugin
    payload = {
        "nodeId": "test-integration", 
        "type": "my.plugin",
        "args": {"param1": "integration_test"},
        "inputs": {}
    }
    
    response = requests.post(f"{base_url}/run_node", json=payload)
    result = response.json()
    
    assert result["ok"] == True
    assert "output" in result

if __name__ == "__main__":
    test_plugin_via_api()
    print("✅ Integration test passed!")
```

---

## 📦 Plugin Distribution

### Directory Structure

```
my-saterys-plugins/
├── README.md
├── requirements.txt
├── setup.py           # Optional: for pip installation
├── nodes/
│   ├── __init__.py    # Optional
│   ├── my_plugin.py
│   ├── another_plugin.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── test_my_plugin.py
│   └── test_integration.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_workflow.py
└── docs/
    └── plugin_guide.md
```

### Requirements File

```txt
# requirements.txt
numpy>=1.20.0
scipy>=1.7.0
scikit-image>=0.18.0
matplotlib>=3.3.0
```

### Setup Script

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-saterys-plugins",
    version="1.0.0",
    description="Custom SATERYS plugins for specialized processing",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0", 
        "scikit-image>=0.18.0"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

---

## 🔍 Debugging Tips

### Add Debug Logging

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run(args, inputs, context):
    logger.debug(f"Plugin {NAME} started")
    logger.debug(f"Args: {args}")
    logger.debug(f"Inputs: {list(inputs.keys())}")
    
    # Your processing logic
    
    logger.debug(f"Plugin {NAME} completed")
    return result
```

### Print Debugging

```python
def run(args, inputs, context):
    print(f"🐛 DEBUG: {NAME} execution started")
    print(f"🔧 Args: {json.dumps(args, indent=2)}")
    print(f"📥 Input types: {[inp.get('type', 'unknown') for inp in inputs.values()]}")
    
    # Your processing logic
    
    print(f"✅ {NAME} completed successfully")
    return result
```

### Validate Inputs

```python
def validate_inputs(inputs):
    """Validate that required inputs are present and valid"""
    required_types = ["raster", "vector"]  # Adjust as needed
    
    for req_type in required_types:
        found = False
        for inp in inputs.values():
            if isinstance(inp, dict) and inp.get("type") == req_type:
                found = True
                break
        
        if not found:
            raise ValueError(f"Required input type '{req_type}' not found")

def run(args, inputs, context):
    validate_inputs(inputs)
    
    # Continue with processing...
```

---

## 🌟 Best Practices

### 1. **Naming Conventions**

```python
# ✅ Good: Descriptive, hierarchical names
NAME = "raster.ndvi"
NAME = "vector.buffer" 
NAME = "ml.classification.random_forest"

# ❌ Avoid: Generic or unclear names  
NAME = "process"
NAME = "node1"
NAME = "stuff"
```

### 2. **Parameter Design**

```python
# ✅ Good: Clear, well-documented parameters
DEFAULT_ARGS = {
    "output_path": "",           # Clear purpose
    "buffer_distance": 100.0,    # Descriptive name  
    "spatial_reference": "EPSG:4326",  # Standard format
    "overwrite_existing": False  # Boolean flag
}

# ❌ Avoid: Unclear or poorly typed parameters
DEFAULT_ARGS = {
    "path": "",      # Too generic
    "val": 100,      # Unclear name
    "flag": 1        # Use boolean instead of int
}
```

### 3. **Error Messages**

```python
# ✅ Good: Specific, actionable error messages
if not os.path.exists(raster_path):
    raise FileNotFoundError(
        f"Raster file not found: {raster_path}. "
        f"Please check the file path and ensure the file exists."
    )

# ❌ Avoid: Generic or unhelpful errors
if not os.path.exists(raster_path):
    raise Exception("Error")
```

### 4. **Output Consistency**

```python
# ✅ Good: Consistent output structure
def run(args, inputs, context):
    return {
        "type": "raster",           # Always include type
        "path": output_path,        # Core data
        "metadata": {               # Additional info
            "processing_time": elapsed,
            "parameters_used": args,
            "source_files": input_paths
        },
        "statistics": {             # Optional stats
            "min_value": data.min(),
            "max_value": data.max(),
            "mean_value": data.mean()
        }
    }
```

---

## 🤝 Contributing Plugins

### Submission Guidelines

1. **Code Quality**
   - Follow PEP 8 style guide
   - Include docstrings
   - Add type hints where possible
   - Handle errors gracefully

2. **Documentation**  
   - README with usage examples
   - Parameter descriptions
   - Input/output specifications
   - Installation instructions

3. **Testing**
   - Unit tests for core functionality
   - Integration tests with SATERYS
   - Example usage scripts

4. **Licensing**
   - Use compatible license (MIT recommended)
   - Include copyright notices
   - Respect third-party licenses

### Community Plugins

Share your plugins with the community:

- 📢 [SATERYS Discussions](https://github.com/bastian6666/SATERYS/discussions)
- 🐙 GitHub repositories with `saterys-plugin` topic
- 📦 PyPI packages with `saterys` classifier

---

<div align="center">

**Ready to build amazing plugins? 🚀**

[⬅️ Back to Getting Started](getting-started.md) | [Examples ➡️](../examples/)

</div>