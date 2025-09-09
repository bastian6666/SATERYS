# 🎯 SATERYS Examples

This directory contains practical examples showcasing SATERYS capabilities across different use cases and domains.

## 📂 Directory Structure

```
examples/
├── 01_basic/                    # Getting started examples
│   ├── hello_world.py          # Simple node execution
│   ├── numeric_operations.py   # Basic arithmetic pipelines
│   └── README.md
├── 02_geospatial/              # Earth observation workflows
│   ├── ndvi_calculation.py     # Vegetation index analysis
│   ├── water_detection.py      # Water body mapping
│   ├── change_detection.py     # Multi-temporal analysis
│   └── README.md
├── 03_automation/              # Batch processing scripts
│   ├── batch_processing.py     # Process multiple files
│   ├── scheduled_analysis.py   # Automated workflows
│   └── README.md
├── 04_integration/             # External tool integration
│   ├── jupyter_integration.py  # Notebook workflows
│   ├── qgis_plugin.py         # QGIS integration
│   ├── web_api_client.py       # REST API usage
│   └── README.md
├── 05_custom_plugins/          # Plugin development examples
│   ├── simple_plugin.py        # Basic plugin template
│   ├── raster_plugin.py        # Geospatial processing
│   ├── ml_plugin.py            # Machine learning integration
│   └── README.md
└── data/                       # Sample datasets
    ├── landsat_sample.tif      # Sample satellite imagery
    ├── sentinel_rgb.tif        # RGB composite
    └── README.md
```

## 🚀 Quick Start Examples

### Hello World

```python
import requests

# Simple node execution
response = requests.post("http://localhost:8000/run_node", json={
    "nodeId": "hello-1",
    "type": "hello",
    "args": {"name": "SATERYS"}
})

print(response.json()["output"])  # {"text": "hello SATERYS"}
```

### NDVI Calculation

```python
import requests

# Load satellite imagery
raster_response = requests.post("http://localhost:8000/run_node", json={
    "nodeId": "load-landsat",
    "type": "raster.input",
    "args": {"path": "/path/to/landsat8.tif"}
})

raster_output = raster_response.json()["output"]

# Calculate NDVI
ndvi_response = requests.post("http://localhost:8000/run_node", json={
    "nodeId": "calc-ndvi", 
    "type": "raster.ndvi",
    "args": {"red_band": 4, "nir_band": 5},
    "inputs": {"load-landsat": raster_output}
})

print(f"NDVI saved to: {ndvi_response.json()['output']['path']}")
```

## 🌟 Featured Examples

### 1. 🛰️ Multi-Temporal NDVI Analysis

**Use Case**: Monitor vegetation changes over time using satellite time series.

**Location**: `02_geospatial/change_detection.py`

**Key Features**:
- Load multiple satellite scenes
- Calculate NDVI for each time period  
- Generate change maps
- Export results for analysis

### 2. 🌊 Automated Water Body Detection

**Use Case**: Detect and map water bodies using spectral indices.

**Location**: `02_geospatial/water_detection.py`

**Key Features**:
- NDWI calculation
- Thresholding and classification
- Accuracy assessment
- Vector export

### 3. ⚙️ Batch Processing Pipeline

**Use Case**: Process hundreds of satellite scenes automatically.

**Location**: `03_automation/batch_processing.py`

**Key Features**:
- Directory scanning
- Parallel processing
- Progress tracking
- Error handling and logging

### 4. 📊 Jupyter Notebook Integration

**Use Case**: Interactive analysis and visualization in Jupyter.

**Location**: `04_integration/jupyter_integration.py`

**Key Features**:
- SATERYS API client
- Matplotlib visualization
- Interactive widgets
- Export capabilities

### 5. 🧠 Machine Learning Plugin

**Use Case**: Land cover classification using scikit-learn.

**Location**: `05_custom_plugins/ml_plugin.py`

**Key Features**:
- Feature extraction
- Model training
- Prediction mapping
- Validation metrics

## 🎓 Learning Path

### Beginner (Start Here!)

1. **[Basic Operations](01_basic/)** - Learn SATERYS fundamentals
2. **[Simple NDVI](02_geospatial/ndvi_calculation.py)** - First geospatial analysis
3. **[Web Interface Tutorial](../docs/getting-started.md)** - GUI workflow

### Intermediate

4. **[Batch Processing](03_automation/batch_processing.py)** - Automate workflows
5. **[API Integration](04_integration/web_api_client.py)** - Programmatic access
6. **[Custom Plugins](05_custom_plugins/)** - Extend functionality

### Advanced

7. **[Machine Learning](05_custom_plugins/ml_plugin.py)** - AI-powered analysis
8. **[QGIS Integration](04_integration/qgis_plugin.py)** - Desktop GIS workflows
9. **[Production Deployment](../docs/deployment.md)** - Scale your applications

## 🛠️ Prerequisites

### Software Requirements

```bash
# Core dependencies
pip install saterys numpy matplotlib

# Geospatial analysis  
pip install rasterio geopandas folium

# Machine learning
pip install scikit-learn pandas

# Visualization
pip install plotly seaborn ipywidgets
```

### Sample Data

Download sample datasets:

```bash
# Create data directory
mkdir -p examples/data

# Download Landsat sample (placeholder - replace with actual data)
wget -O examples/data/landsat_sample.tif \
  "https://example.com/sample_data/landsat8_rgb.tif"

# Or use your own GeoTIFF files
cp /path/to/your/satellite/data.tif examples/data/
```

## 🔧 Running Examples

### Method 1: Direct Execution

```bash
# Start SATERYS server
saterys &

# Run example script
cd examples/02_geospatial
python ndvi_calculation.py
```

### Method 2: Jupyter Notebooks

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter server
jupyter notebook

# Open example notebooks in browser
# Navigate to examples/ directory
```

### Method 3: Docker Container

```dockerfile
# Dockerfile
FROM python:3.10-slim

RUN pip install saterys jupyter

COPY examples/ /app/examples/
WORKDIR /app

EXPOSE 8000 8888

CMD ["sh", "-c", "saterys & jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"]
```

```bash
# Build and run
docker build -t saterys-examples .
docker run -p 8000:8000 -p 8888:8888 saterys-examples
```

## 📚 Documentation

Each example directory contains:

- 📄 **README.md** - Overview and setup instructions
- 🐍 **Python scripts** - Executable examples
- 📓 **Jupyter notebooks** - Interactive tutorials  
- 📊 **Sample outputs** - Expected results
- 🔧 **Requirements.txt** - Dependencies

## 🤝 Contributing Examples

We welcome community contributions! Here's how to add your examples:

### 1. Create Example Structure

```bash
# Create new example category
mkdir examples/06_my_category

# Add files
touch examples/06_my_category/README.md
touch examples/06_my_category/my_example.py
touch examples/06_my_category/requirements.txt
```

### 2. Follow Template

```python
#!/usr/bin/env python3
"""
Example: [Brief Description]

This example demonstrates [key functionality].

Requirements:
- SATERYS running on localhost:8000
- Sample data in examples/data/
- Additional dependencies: pip install [packages]

Usage:
    python my_example.py

Expected Output:
    [Describe what users should see]
"""

import requests
import os

# Configuration
API_BASE = "http://localhost:8000"
DATA_DIR = "../data"

def main():
    """Main example function"""
    
    print("🚀 Starting SATERYS example...")
    
    # Your example code here
    
    print("✅ Example completed successfully!")

if __name__ == "__main__":
    main()
```

### 3. Add Documentation

```markdown
# My Example Category

Brief description of what this category covers.

## Examples

### my_example.py

**Purpose**: Describe what this example does

**Key Learning Points**:
- Point 1
- Point 2  
- Point 3

**Usage**:
```bash
python my_example.py
```

**Expected Output**: Describe the results
```

### 4. Test Your Example

```bash
# Verify it works
cd examples/06_my_category
python my_example.py

# Check documentation
cat README.md
```

### 5. Submit Pull Request

1. Fork the SATERYS repository
2. Add your examples
3. Test thoroughly
4. Submit pull request with description

## 🎯 Example Categories Explained

### 01_basic/ - Foundation Examples
- **Purpose**: Learn SATERYS core concepts
- **Audience**: Complete beginners
- **Focus**: API basics, simple workflows

### 02_geospatial/ - Earth Observation
- **Purpose**: Real-world geospatial analysis
- **Audience**: GIS professionals, researchers
- **Focus**: Satellite data processing, indices calculation

### 03_automation/ - Production Workflows
- **Purpose**: Scalable, automated processing
- **Audience**: DevOps, data engineers
- **Focus**: Batch processing, monitoring, error handling

### 04_integration/ - Tool Connectivity
- **Purpose**: Connect SATERYS with other tools
- **Audience**: Developers, analysts
- **Focus**: APIs, notebooks, desktop applications

### 05_custom_plugins/ - Extensibility
- **Purpose**: Create custom processing nodes
- **Audience**: Python developers
- **Focus**: Plugin architecture, advanced processing

## 💡 Tips for Success

### 1. Start Simple
Begin with basic examples and gradually increase complexity.

### 2. Use Real Data  
Examples work best with actual satellite imagery or GIS data.

### 3. Include Error Handling
```python
try:
    result = requests.post(API_URL, json=payload)
    result.raise_for_status()
except requests.RequestException as e:
    print(f"❌ API request failed: {e}")
    return
```

### 4. Add Progress Indicators
```python
from tqdm import tqdm

for i, file in enumerate(tqdm(files, desc="Processing")):
    # Process file
    pass
```

### 5. Document Expected Results
Always explain what users should see when running examples.

---

## 🔗 Additional Resources

- 📖 [Getting Started Guide](../docs/getting-started.md)
- 🧩 [Plugin Development](../docs/plugins.md)
- 🔌 [API Reference](../docs/api.md)
- 💬 [Community Discussions](https://github.com/bastian6666/SATERYS/discussions)
- 🐛 [Issue Tracker](https://github.com/bastian6666/SATERYS/issues)

---

<div align="center">

**Ready to explore SATERYS capabilities? Start with [01_basic](01_basic/)! 🚀**

[⬅️ Back to Main README](../README.md)

</div>