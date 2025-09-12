#!/usr/bin/env python3
"""
Basic Manual Labeling Example

This script demonstrates the basic usage of the SATERYS Manual Labeler
for creating training samples from satellite imagery.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directories to the path to import saterys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saterys.nodes.training_sample import run as manual_labeler_run

def main():
    """Run a basic manual labeling session"""
    
    print("🎯 SATERYS Manual Labeler - Basic Example")
    print("=" * 50)
    
    # Create sample data if it doesn't exist
    sample_raster = "sample_data/sample_image.tif"
    if not os.path.exists(sample_raster):
        print("Creating sample raster data...")
        create_sample_raster(sample_raster)
    
    # Configuration for the manual labeler
    args = {
        # Input raster file
        "input_path": sample_raster,
        
        # Output files
        "class_raster_path": "./results/basic_labels.tif",
        "points_path": "./results/basic_training_points.gpkg",
        
        # Define classification classes
        "classes": [
            {"id": 1, "name": "Water", "color": "#1E88E5"},
            {"id": 2, "name": "Vegetation", "color": "#43A047"},
            {"id": 3, "name": "Urban", "color": "#E53935"},
            {"id": 4, "name": "Bare Soil", "color": "#FB8C00"}
        ],
        
        # Class persistence
        "classes_path": "./results/basic_classes.json",
        "persist_classes": True,
        
        # Labeling settings
        "brush_size_px": 3,
        
        # Server settings
        "host": "127.0.0.1",
        "port": 8090,
        "open_browser": True,
        "port_autoselect": True
    }
    
    # Empty inputs (we're using input_path directly)
    inputs = {}
    
    # Context for the node
    context = {"nodeId": "basic-manual-labeler"}
    
    # Create output directory
    os.makedirs("results", exist_ok=True)
    os.makedirs("sample_data", exist_ok=True)
    
    print(f"Input raster: {sample_raster}")
    print(f"Output labels: {args['class_raster_path']}")
    print(f"Output points: {args['points_path']}")
    print()
    
    try:
        print("Starting Manual Labeler...")
        
        # Run the manual labeler node
        result = manual_labeler_run(args, inputs, context)
        
        print("✅ Manual Labeler started successfully!")
        print()
        
        # Extract and display the labeler URL
        labeler_url = None
        for item in result:
            if isinstance(item, dict) and item.get("type") == "info":
                message = item.get("message", "")
                if "Labeler at" in message:
                    labeler_url = message.split("Labeler at ")[-1]
                    break
        
        if labeler_url:
            print("🌐 Manual Labeler Interface:")
            print(f"   {labeler_url}")
            print()
            print("📋 How to use:")
            print("   1. Click '✎ Label: Off' to enable labeling mode")
            print("   2. Select a class from the colored palette")
            print("   3. Click on the map to label pixels")
            print("   4. Use the attribute table to manage labels")
            print("   5. Press '💾 Save' or 'S' to export your work")
            print()
            print("⌨️  Keyboard shortcuts:")
            print("   L     - Toggle labeling mode")
            print("   1-4   - Select class by number")
            print("   [ ]   - Adjust brush size")
            print("   Z     - Undo last operation")
            print("   S     - Save labels")
            print()
            print("🔴 Press Ctrl+C to stop the server when done.")
            
            # Keep the server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\n🛑 Shutting down Manual Labeler...")
                print("✅ Session completed!")
                
        else:
            print("❌ Could not extract labeler URL from result")
            
    except Exception as e:
        print(f"❌ Error starting Manual Labeler: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def create_sample_raster(output_path):
    """Create a synthetic raster for testing"""
    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_bounds
        
        # Create synthetic raster data
        width, height = 256, 256
        bounds = [-74.1, 40.6, -73.9, 40.8]  # NYC area coordinates
        transform = from_bounds(*bounds, width, height)
        
        # Create synthetic multispectral bands with patterns
        np.random.seed(42)  # For reproducible results
        
        # Red band with some spatial patterns
        y, x = np.ogrid[:height, :width]
        red = (128 + 50 * np.sin(x/20) * np.cos(y/25)).astype(np.uint8)
        red = np.clip(red + np.random.randint(-30, 30, (height, width)), 0, 255)
        
        # Green band
        green = (150 + 40 * np.cos(x/15) * np.sin(y/20)).astype(np.uint8)
        green = np.clip(green + np.random.randint(-25, 25, (height, width)), 0, 255)
        
        # Blue band
        blue = (100 + 30 * np.sin(x/10) * np.cos(y/30)).astype(np.uint8)
        blue = np.clip(blue + np.random.randint(-20, 20, (height, width)), 0, 255)
        
        # NIR band (typically higher for vegetation)
        nir = (180 + 60 * np.cos(x/25) * np.sin(y/15)).astype(np.uint8)
        nir = np.clip(nir + np.random.randint(-40, 40, (height, width)), 0, 255)
        
        # Stack bands: R, G, B, NIR
        data = np.stack([red, green, blue, nir])
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as GeoTIFF
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=height,
            width=width,
            count=4,
            dtype=data.dtype,
            crs='EPSG:4326',
            transform=transform,
            compress='lzw'
        ) as dst:
            dst.write(data)
            dst.set_band_description(1, 'Red')
            dst.set_band_description(2, 'Green')
            dst.set_band_description(3, 'Blue')
            dst.set_band_description(4, 'Near Infrared')
        
        print(f"✅ Created sample raster: {output_path}")
        
    except ImportError as e:
        print(f"❌ Error creating sample data: {e}")
        print("   Please ensure rasterio and numpy are installed")
        raise
    except Exception as e:
        print(f"❌ Error creating sample raster: {e}")
        raise

if __name__ == "__main__":
    exit(main())