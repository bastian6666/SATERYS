# 🚀 Getting Started with SATERYS

Welcome to SATERYS! This guide will help you get up and running with the geospatial pipeline builder in just a few minutes.

## 🎯 What You'll Learn

By the end of this guide, you'll know how to:
- ✅ Install and launch SATERYS
- ✅ Create your first pipeline
- ✅ Work with geospatial data
- ✅ Execute and view results

---

## ⚡ Quick Installation

### Prerequisites

- **Python 3.9+** (check with `python --version`)
- **pip** package manager

### Install SATERYS

```bash
# Install from PyPI
pip install saterys

# Verify installation
saterys --help
```

<details>
<summary>💡 Having installation issues?</summary>

**Common solutions:**

```bash
# Update pip first
pip install --upgrade pip

# Install in user directory if permission issues
pip install --user saterys

# Use virtual environment (recommended)
python -m venv saterys-env
source saterys-env/bin/activate  # Linux/Mac
# or
saterys-env\Scripts\activate     # Windows
pip install saterys
```

</details>

---

## 🎨 First Launch

Start SATERYS with a single command:

```bash
saterys
```

You'll see output like this:

```console
Starting Saterys API → http://127.0.0.1:8000
Loaded plugin: script from /path/to/saterys/nodes/script.py
Loaded plugin: raster.ndwi from /path/to/saterys/nodes/NDWI.py
Loaded plugin: raster.input from /path/to/saterys/nodes/input.py
Loaded plugin: hello from /path/to/saterys/nodes/hello.py
Loaded plugin: raster.pca from /path/to/saterys/nodes/PCA.py
Loaded plugin: sum from /path/to/saterys/nodes/sum.py
Loaded plugin: raster.ndvi from /path/to/saterys/nodes/NDVI.py
INFO:     Uvicorn running on http://127.0.0.1:8000
```

🌐 **Open your browser** and navigate to `http://localhost:8000`

---

## 🖱️ Interface Overview

The SATERYS interface consists of several key areas:

```
┌─────────────────────────────────────────────────────────────┐
│  🛰️ SATERYS              [Run] [Logs] [Layers] [Theme]  │
├─────────────────────────────────────────────────────────────┤
│ TOOLS        │                                     │ 🗺️     │
│ + Add Node   │         NODE CANVAS                │ MAP     │
│ ▷ Run        │                                     │         │
│ 🧹 Clear      │    [Hello] ──► [Sum] ──► [Script]  │ 🗺️     │
│ 🌙 Theme      │                                     │         │
│              │                                     │         │
│ EDGES        │                                     │         │
│ (none)       │                                     │ 🗺️     │
│              │                                     │         │
└──────────────┴─────────────────────────────────────┴─────────┘
│                    PIPELINE LOGS                              │
│ No logs yet. Run the pipeline to see Python prints/stdout.   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components:

- 🧰 **Tools Panel**: Add nodes, run pipelines, manage layers
- 🎯 **Node Canvas**: Visual workflow builder
- 🗺️ **Map Panel**: Geospatial data preview
- 📋 **Logs Panel**: Execution output and debugging

---

## 👋 Tutorial 1: Hello World

Let's create your first SATERYS pipeline!

### Step 1: Add a Hello Node

1. Click **"Add Node"** in the tools panel
2. A new node appears on the canvas
3. By default, it's set to "hello" type

### Step 2: Configure the Node

1. Click the **📝 (edit)** button on the hello node
2. A parameter dialog opens
3. Change the `name` parameter from "world" to "SATERYS"
4. Close the dialog

### Step 3: Execute

1. Click **"Run"** in the top toolbar (or tools panel)
2. Watch the logs panel at the bottom
3. You should see: `{'text': 'hello SATERYS'}`

🎉 **Congratulations!** You've run your first SATERYS pipeline.

---

## 🧮 Tutorial 2: Numeric Processing

Let's create a simple numeric pipeline.

### Step 1: Create Sum Pipeline

1. Add a new node and change its type to **"sum"**
2. Add another **"hello"** node
3. Connect them:
   - Click the **output** port of the hello node
   - Click the **input** port of the sum node

### Step 2: Configure Parameters

**Hello Node:**
- Set `name` to `"42"` (the node will output: `{"text": "hello 42"}`)

**Sum Node:**  
- Set `a` to `10`
- Set `b` to `5` 
- This node adds values from arguments and connected inputs

### Step 3: Run and Observe

Click **Run** and check the logs. You'll see:
- Hello node output: `{"text": "hello 42"}`
- Sum node output: `{"result": 15}` (10 + 5)

---

## 🛰️ Tutorial 3: Geospatial Data

Now let's work with real geospatial data!

### Prerequisites

You'll need a GeoTIFF file. You can:
- Download sample data from [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- Use [Sentinel Hub EO Browser](https://apps.sentinel-hub.com/eo-browser/)
- Or use any GeoTIFF file you have

### Step 1: Load Raster Data

1. Add a node and change type to **"raster.input"**
2. Click the **📝** button to edit parameters
3. Set the `path` parameter to your GeoTIFF file path:
   ```
   /path/to/your/satellite_image.tif
   ```

### Step 2: Preview on Map

1. Click the **👁️ (preview)** button on the raster.input node
2. The map panel on the right should show your raster data
3. Use the zoom controls to navigate

### Step 3: Calculate NDVI

If your raster has multispectral bands:

1. Add a **"raster.ndvi"** node
2. Connect the raster.input output to the NDVI input  
3. Configure NDVI parameters:
   - `red_band`: Band index for red (e.g., 4 for Landsat 8)
   - `nir_band`: Band index for NIR (e.g., 5 for Landsat 8)
4. Click **Run**
5. Preview the NDVI result on the map

---

## 🔧 Development Mode

For active development and customization:

```bash
# Start with auto-reload
saterys --dev
```

This enables:
- 🔄 **Hot reload** when you modify plugins
- 🎨 **Frontend development** server (if available)
- 📝 **Detailed logging** for debugging

---

## 📁 Custom Plugins

Create a `nodes/` directory in your working folder:

```bash
mkdir nodes
```

Add a custom plugin:

```python
# nodes/my_plugin.py

NAME = "my.awesome.plugin"
DEFAULT_ARGS = {
    "multiplier": 2
}

def run(args, inputs, context):
    multiplier = args.get("multiplier", 2)
    result = 42 * multiplier
    
    return {
        "type": "number",
        "value": result,
        "message": f"42 × {multiplier} = {result}"
    }
```

Restart SATERYS and your plugin will appear in the node type dropdown!

---

## 🚨 Troubleshooting

### Common Issues

<details>
<summary><strong>❌ "Frontend not built" error</strong></summary>

This usually means the static files are missing. Try:

```bash
pip install --upgrade --force-reinstall saterys
```

</details>

<details>
<summary><strong>❌ Port already in use</strong></summary>

Use a different port:

```bash
saterys --port 8080
```

Or find and stop the process using port 8000.

</details>

<details>
<summary><strong>❌ Plugin not loading</strong></summary>

Check that your plugin file:
- Is in a `nodes/` directory
- Has a `.py` extension
- Contains a `NAME` variable
- Contains a `run()` function
- Has no syntax errors

</details>

<details>
<summary><strong>❌ Raster file not found</strong></summary>

Ensure:
- File path is absolute (not relative)
- File exists and is readable
- File format is supported by rasterio (GeoTIFF, COG, etc.)

</details>

### Getting Help

- 📖 Check the full [documentation](../README.md)
- 🐛 Report bugs on [GitHub Issues](https://github.com/bastian6666/SATERYS/issues)
- 💬 Ask questions in [Discussions](https://github.com/bastian6666/SATERYS/discussions)

---

## 🎯 Next Steps

Now that you're familiar with SATERYS basics, explore:

- 🧩 [Plugin Development Guide](plugins.md) - Create custom processing nodes
- 📊 [Advanced Examples](../examples/) - Complex geospatial workflows  
- 🔌 [API Reference](api.md) - REST endpoint documentation
- 🎨 [UI Customization](customization.md) - Theming and branding

---

<div align="center">

**Happy analyzing! 🛰️✨**

[⬅️ Back to Main README](../README.md) | [Plugin Development ➡️](plugins.md)

</div>