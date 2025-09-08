#!/usr/bin/env python3
"""
Example: NDVI Calculation Workflow

This example demonstrates calculating NDVI (Normalized Difference Vegetation Index)
from satellite imagery using SATERYS.

Requirements:
- SATERYS running on localhost:8000
- A multispectral GeoTIFF file (Landsat, Sentinel, etc.)
- Optional: matplotlib for visualization

Usage:
    python ndvi_calculation.py /path/to/your/satellite/image.tif

Expected Output:
    - NDVI GeoTIFF file saved to disk
    - Preview registered for web map
    - Optional: matplotlib visualization
"""

import requests
import sys
import os
import json
from pathlib import Path

# Configuration  
API_BASE = "http://localhost:8000"
OUTPUT_DIR = "./outputs"

class SATERYSClient:
    """SATERYS API client for geospatial workflows"""
    
    def __init__(self, base_url=API_BASE):
        self.base_url = base_url
        
    def check_connection(self):
        """Check if SATERYS is accessible"""
        try:
            response = requests.get(f"{self.base_url}/node_types", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def run_node(self, node_id, node_type, args=None, inputs=None):
        """Execute a node and return output"""
        payload = {
            "nodeId": node_id,
            "type": node_type,
            "args": args or {},
            "inputs": inputs or {}
        }
        
        response = requests.post(f"{self.base_url}/run_node", json=payload)
        response.raise_for_status()
        
        result = response.json()
        if result["ok"]:
            return result["output"]
        else:
            raise Exception(f"Node execution failed: {result['error']}")
    
    def register_preview(self, preview_id, file_path):
        """Register raster for map preview"""
        payload = {
            "id": preview_id,
            "path": str(file_path)
        }
        
        response = requests.post(f"{self.base_url}/preview/register", json=payload)
        return response.json()

def calculate_ndvi_workflow(client, raster_path, red_band=4, nir_band=5):
    """Complete NDVI calculation workflow"""
    
    print(f"🛰️ Processing: {raster_path}")
    print(f"📊 Bands - Red: {red_band}, NIR: {nir_band}")
    
    # Ensure output directory exists
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load raster input
    print("\n📂 Step 1: Loading raster input...")
    
    raster_output = client.run_node(
        "load-satellite-image", 
        "raster.input",
        args={"path": str(raster_path)}
    )
    
    print(f"✅ Raster loaded:")
    print(f"   - Size: {raster_output['width']} x {raster_output['height']}")
    print(f"   - Bands: {raster_output['count']}")
    print(f"   - CRS: {raster_output.get('crs', 'Unknown')}")
    print(f"   - Bounds: {raster_output.get('bounds', 'Unknown')}")
    
    # Step 2: Calculate NDVI
    print("\n🌿 Step 2: Calculating NDVI...")
    
    ndvi_output_path = os.path.join(OUTPUT_DIR, "ndvi_result.tif")
    
    ndvi_output = client.run_node(
        "calculate-ndvi",
        "raster.ndvi", 
        args={
            "red_band": red_band,
            "nir_band": nir_band,
            "output_path": ndvi_output_path,
            "dtype": "float32",
            "nodata": -9999.0
        },
        inputs={
            "load-satellite-image": raster_output
        }
    )
    
    print(f"✅ NDVI calculated:")
    print(f"   - Output path: {ndvi_output['path']}")
    print(f"   - Data type: {ndvi_output.get('dtype', 'Unknown')}")
    
    # Step 3: Register for preview
    print("\n🗺️ Step 3: Registering preview...")
    
    preview_id = f"ndvi-{int(os.path.getmtime(ndvi_output['path']))}"
    preview_result = client.register_preview(preview_id, ndvi_output['path'])
    
    print(f"✅ Preview registered: ID = {preview_id}")
    print(f"🌐 View in browser: http://localhost:8000")
    print(f"🖼️ Tile URL template: http://localhost:8000/preview/tile/{preview_id}/{{z}}/{{x}}/{{y}}.png")
    
    return {
        "raster_input": raster_output,
        "ndvi_output": ndvi_output,
        "preview_id": preview_id
    }

def visualize_with_matplotlib(ndvi_path):
    """Optional: Visualize NDVI with matplotlib"""
    
    try:
        import matplotlib.pyplot as plt
        import rasterio
        from rasterio.plot import show
        import numpy as np
        
        print("\n📊 Creating matplotlib visualization...")
        
        with rasterio.open(ndvi_path) as src:
            ndvi_data = src.read(1, masked=True)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # NDVI visualization
            im1 = ax1.imshow(ndvi_data, cmap='RdYlGn', vmin=-1, vmax=1)
            ax1.set_title('NDVI (Normalized Difference Vegetation Index)')
            ax1.set_xlabel('X Pixel')
            ax1.set_ylabel('Y Pixel')
            plt.colorbar(im1, ax=ax1, label='NDVI Value')
            
            # Histogram
            valid_data = ndvi_data[~ndvi_data.mask] if hasattr(ndvi_data, 'mask') else ndvi_data.flatten()
            ax2.hist(valid_data, bins=50, alpha=0.7, color='green', edgecolor='black')
            ax2.set_title('NDVI Value Distribution')
            ax2.set_xlabel('NDVI Value')
            ax2.set_ylabel('Frequency')
            ax2.axvline(x=0, color='red', linestyle='--', label='Zero line')
            ax2.legend()
            
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(OUTPUT_DIR, "ndvi_visualization.png")
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            
            print(f"✅ Visualization saved: {plot_path}")
            
            # Show plot if running interactively
            if hasattr(sys, 'ps1'):  # Check if running in interactive mode
                plt.show()
            else:
                plt.close()
                
    except ImportError:
        print("ℹ️ matplotlib not available - skipping visualization")
        print("💡 Install with: pip install matplotlib rasterio")

def main():
    """Main example function"""
    
    print("🚀 SATERYS NDVI Calculation Example")
    print("=" * 40)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("❌ Usage: python ndvi_calculation.py <path_to_raster_file> [red_band] [nir_band]")
        print("\n💡 Examples:")
        print("   python ndvi_calculation.py /data/landsat8.tif")
        print("   python ndvi_calculation.py /data/landsat8.tif 4 5")  # Landsat 8
        print("   python ndvi_calculation.py /data/sentinel2.tif 4 8")  # Sentinel-2
        sys.exit(1)
    
    raster_path = Path(sys.argv[1])
    red_band = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    nir_band = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # Validate input file
    if not raster_path.exists():
        print(f"❌ File not found: {raster_path}")
        sys.exit(1)
    
    print(f"📁 Input file: {raster_path}")
    print(f"🔴 Red band: {red_band}")
    print(f"🌿 NIR band: {nir_band}")
    
    # Initialize client
    client = SATERYSClient()
    
    # Check connection
    print("\n🔍 Checking SATERYS connection...")
    if not client.check_connection():
        print("❌ SATERYS is not running or not accessible")
        print("💡 Start SATERYS with: saterys")
        sys.exit(1)
    
    print("✅ SATERYS is running")
    
    try:
        # Run NDVI workflow
        results = calculate_ndvi_workflow(client, raster_path, red_band, nir_band)
        
        # Optional visualization
        visualize_with_matplotlib(results['ndvi_output']['path'])
        
        print("\n🎉 NDVI calculation completed successfully!")
        print(f"📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
        print(f"🗺️ Preview ID: {results['preview_id']}")
        
        # Print summary statistics
        ndvi_path = results['ndvi_output']['path'] 
        try:
            import rasterio
            with rasterio.open(ndvi_path) as src:
                data = src.read(1, masked=True)
                if hasattr(data, 'mask'):
                    valid_data = data[~data.mask]
                else:
                    valid_data = data.flatten()
                
                print(f"\n📊 NDVI Statistics:")
                print(f"   - Min: {valid_data.min():.4f}")
                print(f"   - Max: {valid_data.max():.4f}")
                print(f"   - Mean: {valid_data.mean():.4f}")
                print(f"   - Std: {valid_data.std():.4f}")
                
        except ImportError:
            print("ℹ️ Install rasterio for detailed statistics: pip install rasterio")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()