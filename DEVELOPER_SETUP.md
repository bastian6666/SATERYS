# 🚀 SATERYS Developer Setup Guide

This guide will walk you through setting up SATERYS for development with OLLAMA AI integration.

## 📋 Prerequisites

- **Python 3.9+** (Python 3.10+ recommended)
- **Node.js 16+** and **npm**
- **Git**
- **OLLAMA** (for AI features)

## 🛠️ Development Environment Setup

### 1. Clone and Install SATERYS

```bash
# Clone the repository
git clone https://github.com/bastian6666/SATERYS.git
cd SATERYS

# Install in development mode
pip install -e .

# Verify installation
saterys --help
```

### 2. Frontend Development Setup

```bash
# Navigate to frontend directory
cd saterys/web

# Install dependencies
npm install

# Build frontend assets (production)
npm run build

# OR run in development mode with hot reload
npm run dev
```

### 3. OLLAMA AI Integration Setup

#### Install OLLAMA

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

#### Download AI Models

```bash
# Download the default model (recommended)
ollama pull llama3.2:latest

# Optional: Download other models
ollama pull llama3.2:1b     # Smaller, faster model
ollama pull codellama:latest # Code-specialized model
ollama pull mistral:latest   # Alternative model
```

#### Start OLLAMA Server

```bash
# Start OLLAMA server (runs on http://localhost:11434 by default)
ollama serve
```

**Note:** Keep this terminal open while developing - the AI features require OLLAMA to be running.

#### Verify OLLAMA Installation

```bash
# Test OLLAMA is working
ollama list

# Test API access
curl http://localhost:11434/api/tags
```

## 🏃‍♂️ Running SATERYS

### Development Mode (Recommended)

This starts both the backend (FastAPI) and frontend (Vite) with hot reload:

```bash
# From the SATERYS root directory
saterys --dev
```

This will:
- Start the FastAPI backend on `http://localhost:8000`
- Start the Vite frontend dev server on `http://localhost:5173`
- Automatically open your browser to the frontend
- Enable hot reload for both frontend and backend changes

### Production Mode

To run with built static assets:

```bash
# Make sure frontend is built
cd saterys/web && npm run build && cd ../..

# Start production server
saterys

# Access at http://localhost:8000
```

### Custom Configuration

```bash
# Custom host and port
saterys --host 0.0.0.0 --port 8080

# Or use environment variables
export SATERYS_HOST=0.0.0.0
export SATERYS_PORT=8080
export SATERYS_DEV_ORIGIN=http://localhost:5173  # For CORS in dev mode
saterys
```

## 🔧 Development Workflow

### Backend Development (FastAPI)

1. **Adding New Nodes:**
   ```bash
   # Create new node file in saterys/nodes/
   touch saterys/nodes/my_new_node.py
   ```

   Example node structure:
   ```python
   NAME = "my.custom.node"
   DEFAULT_ARGS = {"param1": "default_value"}

   def run(args, inputs, context):
       # Your processing logic
       return {"result": "output"}
   ```

2. **API Development:**
   - Edit `saterys/app.py` to add new endpoints
   - FastAPI auto-reloads when files change (in `--dev` mode)
   - API docs available at `http://localhost:8000/docs`

3. **Testing Backend:**
   ```bash
   # Test node loading
   curl http://localhost:8000/node_types

   # Test workflow save/load
   curl http://localhost:8000/workflows

   # Test OLLAMA integration
   curl http://localhost:8000/ollama/status
   ```

### Frontend Development (Svelte)

1. **File Structure:**
   ```
   saterys/web/
   ├── src/
   │   ├── App.svelte          # Main application
   │   ├── main.ts             # Entry point
   │   └── app.css             # Global styles
   ├── package.json
   └── vite.config.ts
   ```

2. **Making Changes:**
   - Edit `src/App.svelte` for UI changes
   - Vite automatically reloads on file changes
   - Check browser console for errors

3. **Building for Production:**
   ```bash
   cd saterys/web
   npm run build
   ```

### Adding Custom Nodes

1. **Create Node File:**
   ```python
   # saterys/nodes/my_analysis.py
   NAME = "analysis.custom"
   DEFAULT_ARGS = {
       "input_path": "",
       "output_path": "",
       "threshold": 0.5
   }

   def run(args, inputs, context):
       import rasterio
       import numpy as np
       
       # Your processing logic here
       input_path = args.get("input_path")
       threshold = args.get("threshold", 0.5)
       
       # Process data...
       
       return {
           "type": "raster",
           "path": output_path,
           "metadata": {"threshold_used": threshold}
       }
   ```

2. **Update Frontend Schema (Optional):**
   ```typescript
   // In App.svelte, add to SCHEMAS object
   'analysis.custom': [
     { key: 'input_path', label: 'Input Path', type: 'string' },
     { key: 'output_path', label: 'Output Path', type: 'string' },
     { key: 'threshold', label: 'Threshold', type: 'number', step: 0.1 }
   ]
   ```

3. **Restart Development Server:**
   ```bash
   # Backend will auto-discover the new node
   # No restart needed in --dev mode
   ```

## 📁 Project Structure

```
SATERYS/
├── saterys/                    # Python package
│   ├── __init__.py
│   ├── app.py                  # FastAPI application
│   ├── cli.py                  # Command-line interface
│   ├── core.py                 # Core functionality
│   ├── scheduling.py           # APScheduler integration
│   ├── nodes/                  # Processing nodes
│   │   ├── __init__.py
│   │   ├── hello.py           # Example nodes
│   │   ├── sum.py
│   │   ├── script.py
│   │   ├── input.py           # Raster input
│   │   ├── NDVI.py            # NDVI calculation
│   │   └── ollama_ai.py       # AI integration
│   ├── static/                # Built frontend assets
│   └── web/                   # Frontend source code
│       ├── src/
│       │   ├── App.svelte     # Main UI component
│       │   ├── main.ts        # Entry point
│       │   └── app.css        # Styles
│       ├── package.json
│       └── vite.config.ts
├── flows/                     # Saved workflows (created at runtime)
├── docs/                      # Documentation
├── examples/                  # Example workflows
├── pyproject.toml            # Python package configuration
├── README.md
└── DEVELOPER_SETUP.md        # This file
```

## 🐛 Troubleshooting

### Common Issues

1. **Frontend build fails:**
   ```bash
   cd saterys/web
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. **OLLAMA connection errors:**
   ```bash
   # Check if OLLAMA is running
   curl http://localhost:11434/api/tags
   
   # If not running, start it
   ollama serve
   ```

3. **Python import errors:**
   ```bash
   # Reinstall in development mode
   pip install -e .
   
   # Check Python path
   python -c "import saterys; print(saterys.__file__)"
   ```

4. **Port conflicts:**
   ```bash
   # Use different ports
   saterys --port 8001
   
   # For frontend dev
   cd saterys/web
   npm run dev -- --port 5174
   ```

### Debug Mode

Enable verbose logging:
```bash
export SATERYS_DEBUG=1
saterys --dev
```

### Performance Issues

1. **Large datasets:** Use smaller test files during development
2. **Slow AI responses:** Try smaller OLLAMA models like `llama3.2:1b`
3. **Memory usage:** Restart OLLAMA periodically: `pkill ollama && ollama serve`

## 📚 Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Svelte Documentation:** https://svelte.dev/docs
- **OLLAMA Documentation:** https://github.com/ollama/ollama
- **Svelvet (Canvas Library):** https://svelvet.io/
- **Leaflet (Maps):** https://leafletjs.com/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following this setup guide
4. Test thoroughly in development mode
5. Build and test production mode
6. Submit a pull request

## 📝 Notes for AI Development

### Working with OLLAMA Models

- **Model Selection:** Different models have different capabilities
  - `llama3.2:latest`: Best overall performance, larger size (~4GB)
  - `llama3.2:1b`: Faster, smaller (~1GB), good for development
  - `codellama:latest`: Better for code generation tasks

- **Prompt Engineering:** The AI node includes a specialized system prompt for geospatial workflows. Modify `/saterys/nodes/ollama_ai.py` to customize AI behavior.

- **Performance:** AI responses can take 5-30 seconds depending on hardware and model size.

### Extending AI Functionality

The AI integration is designed to be extensible:

1. **Custom Prompts:** Modify the system prompt in `ollama_ai.py`
2. **Model Parameters:** Adjust temperature, max_tokens, etc.
3. **Response Parsing:** Enhance JSON extraction and workflow generation
4. **UI Integration:** Add more AI features to the frontend

Happy coding! 🎉