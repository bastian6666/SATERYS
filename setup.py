# setup.py — only used to hook into setuptools build to run Vite at build time.
import os
import subprocess
from pathlib import Path
from setuptools import setup
from setuptools.command.sdist import sdist as _sdist
from setuptools.command.build_py import build_py as _build_py

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "saterys" / "web"
STATIC = ROOT / "saterys" / "static"
INDEX = STATIC / "index.html"

def build_frontend():
    # Only build if index.html is missing
    if INDEX.exists():
        return
    if not WEB.exists():
        print("No frontend source at saterys/web — skipping.")
        return
    print("🚧 Building Saterys frontend (Vite)…")
    subprocess.check_call(["npm", "ci"], cwd=str(WEB))
    subprocess.check_call(["npm", "run", "build"], cwd=str(WEB))
    if not INDEX.exists():
        raise RuntimeError("Frontend build did not produce saterys/static/index.html")

class build_py(_build_py):
    def run(self):
        build_frontend()
        super().run()

class sdist(_sdist):
    def run(self):
        build_frontend()
        super().run()

setup(cmdclass={"build_py": build_py, "sdist": sdist})
