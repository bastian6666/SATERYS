from setuptools import setup, find_packages

setup(
    name="saterys_plugin_starter",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "saterys.plugins": [
            "starter = saterys_plugin_starter:register",
        ],
    },
)
