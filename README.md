# SATERYS

[![PyPI version](https://img.shields.io/pypi/v/saterys.svg?style=flat-square)](https://pypi.org/project/saterys/)
[![Python versions](https://img.shields.io/pypi/pyversions/saterys.svg?style=flat-square)](https://pypi.org/project/saterys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/bastian6666/saterys/ci.yml?style=flat-square&label=build)](https://github.com/bastian6666/saterys/actions)

**SATERYS** is a geospatial pipeline builder combining a **Svelte** frontend with a **FastAPI** backend.  
It provides an interactive node-based canvas for connecting operations, executing Python plugins, and visualizing raster data directly on a Leaflet map.

---

## ✨ Features

- 🎨 **Interactive Node Editor** using [Svelvet](https://svelvet.io/).
- ⚡ **FastAPI Backend** for plugin execution and REST endpoints.
- 🛰 **Geospatial Preview** with Leaflet, serving raster tiles via [rio-tiler](https://github.com/cogeotiff/rio-tiler).
- 🔌 **Extensible Plugin System**: add your own nodes by dropping Python files into a `nodes/` folder.
- 🌙 **Dark/Light Theme** toggle.
- 📦 Fully **pip-installable** with built frontend assets included.

---

## 📦 Installation

```bash
pip install saterys
# SATERYS
