#!/usr/bin/env python3
"""
Test script to demonstrate the manual labeler functionality
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# Add the current directory to the path to import saterys
sys.path.insert(0, str(Path(__file__).parent))

from saterys.nodes.training_sample import run as manual_labeler_run

def test_manual_labeler():
    """Test the manual labeler with sample data"""
    
    # Configuration for manual labeler
    args = {
        "input_path": "sample_data/sample_image.tif",
        "class_raster_path": "./results/labels.tif",
        "points_path": "./results/labels_points.gpkg",
        "classes": [
            {"id": 1, "name": "Water", "color": "#1E88E5"},
            {"id": 2, "name": "Vegetation", "color": "#43A047"},
            {"id": 3, "name": "Urban", "color": "#E53935"},
            {"id": 4, "name": "Bare Soil", "color": "#FB8C00"}
        ],
        "host": "127.0.0.1",
        "port": 8090,
        "open_browser": False,  # We'll open manually for screenshots
        "port_autoselect": True
    }
    
    inputs = {}
    context = {"nodeId": "manual-labeler-test"}
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    print("Starting manual labeler...")
    print("="*50)
    
    try:
        # Run the manual labeler
        result = manual_labeler_run(args, inputs, context)
        print(f"Manual labeler started successfully!")
        print(f"Result: {result}")
        
        # Extract the URL from the result
        url = None
        for item in result:
            if isinstance(item, dict) and item.get("type") == "info":
                message = item.get("message", "")
                if "Labeler at" in message:
                    url = message.split("Labeler at ")[-1]
                    break
        
        if url:
            print(f"\n🌐 Manual Labeler Interface: {url}")
            print("\nThe manual labeler is now running!")
            print("You can access the interface in your browser at the URL above.")
            print("\nPress Ctrl+C to stop the server when done.")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                
        else:
            print("Could not extract URL from result")
            
    except Exception as e:
        print(f"Error starting manual labeler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_labeler()