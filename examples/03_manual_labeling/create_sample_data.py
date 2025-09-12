#!/usr/bin/env python3
"""
Create Sample Data for Manual Labeling

This script creates synthetic satellite imagery that can be used
to test and demonstrate the SATERYS Manual Labeler functionality.
"""

import os
import numpy as np

def create_sample_raster(output_path="sample_data/demo_image.tif", 
                        width=512, height=512):
    """
    Create a synthetic satellite image with realistic patterns
    
    Args:
        output_path: Path where to save the sample raster
        width: Image width in pixels
        height: Image height in pixels
    """
    try:
        import rasterio
        from rasterio.transform import from_bounds
        
        print(f"Creating sample raster: {output_path}")
        print(f"Dimensions: {width} x {height} pixels")
        
        # Define geographic bounds (example: area around NYC)
        bounds = [-74.2, 40.5, -73.8, 40.9]
        transform = from_bounds(*bounds, width, height)
        
        # Create coordinate grids
        y, x = np.ogrid[:height, :width]
        
        # Normalize coordinates to 0-1 range
        x_norm = x / width
        y_norm = y / height
        
        # Create realistic-looking synthetic data patterns
        np.random.seed(42)  # For reproducible results
        
        # === Red Band ===
        # Base pattern with some urban/rural variation
        red_base = 120 + 40 * np.sin(x_norm * 8 * np.pi) * np.cos(y_norm * 6 * np.pi)
        # Add some "urban" areas (higher reflectance)
        urban_mask = (x_norm > 0.3) & (x_norm < 0.7) & (y_norm > 0.2) & (y_norm < 0.6)
        red_base[urban_mask] += 30
        # Add noise
        red = red_base + np.random.normal(0, 15, (height, width))
        red = np.clip(red, 0, 255).astype(np.uint8)
        
        # === Green Band ===
        # Vegetation areas have higher green reflectance
        green_base = 100 + 50 * np.cos(x_norm * 6 * np.pi) * np.sin(y_norm * 8 * np.pi)
        # Add vegetation areas
        veg_mask = (x_norm < 0.3) | (x_norm > 0.7) | (y_norm < 0.2) | (y_norm > 0.8)
        green_base[veg_mask] += 40
        # Add noise
        green = green_base + np.random.normal(0, 12, (height, width))
        green = np.clip(green, 0, 255).astype(np.uint8)
        
        # === Blue Band ===
        # Water areas have higher blue reflectance
        blue_base = 80 + 30 * np.sin(x_norm * 4 * np.pi + y_norm * 4 * np.pi)
        # Add water areas (lower left and upper right)
        water_mask1 = (x_norm < 0.25) & (y_norm < 0.25)
        water_mask2 = (x_norm > 0.75) & (y_norm > 0.75)
        water_mask = water_mask1 | water_mask2
        blue_base[water_mask] += 50
        # Add noise
        blue = blue_base + np.random.normal(0, 10, (height, width))
        blue = np.clip(blue, 0, 255).astype(np.uint8)
        
        # === Near Infrared Band ===
        # Vegetation has very high NIR reflectance
        nir_base = 120 + 60 * np.cos(x_norm * 5 * np.pi) * np.cos(y_norm * 7 * np.pi)
        # Enhance vegetation areas
        nir_base[veg_mask] += 80
        # Water absorbs NIR
        nir_base[water_mask] -= 60
        # Add noise
        nir = nir_base + np.random.normal(0, 20, (height, width))
        nir = np.clip(nir, 0, 255).astype(np.uint8)
        
        # Stack all bands
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
            compress='lzw',
            tiled=True,
            blockxsize=256,
            blockysize=256
        ) as dst:
            dst.write(data)
            
            # Add band descriptions
            dst.set_band_description(1, 'Red')
            dst.set_band_description(2, 'Green') 
            dst.set_band_description(3, 'Blue')
            dst.set_band_description(4, 'Near Infrared')
            
            # Add metadata
            dst.update_tags(
                AREA_OR_POINT='Point',
                TIFFTAG_SOFTWARE='SATERYS Sample Data Generator',
                TIFFTAG_IMAGEDESCRIPTION='Synthetic satellite imagery for testing'
            )
        
        print(f"✅ Sample raster created successfully!")
        print(f"   File: {output_path}")
        print(f"   Bands: 4 (Red, Green, Blue, NIR)")
        print(f"   Size: {width} x {height} pixels")
        print(f"   CRS: EPSG:4326")
        print(f"   Geographic extent: {bounds}")
        
        # Display some statistics
        print("\\n📊 Band Statistics:")
        with rasterio.open(output_path) as src:
            band_descriptions = ['Red', 'Green', 'Blue', 'Near Infrared']
            for i in range(1, src.count + 1):
                band_data = src.read(i)
                band_name = band_descriptions[i-1] if i <= len(band_descriptions) else f"Band {i}"
                print(f"   Band {i} ({band_name}): "
                      f"min={band_data.min()}, "
                      f"max={band_data.max()}, "
                      f"mean={band_data.mean():.1f}")
        
        return output_path
        
    except ImportError as e:
        print(f"❌ Error: Missing required package - {e}")
        print("   Please install required packages:")
        print("   pip install rasterio numpy")
        raise
    except Exception as e:
        print(f"❌ Error creating sample raster: {e}")
        raise

def create_multiple_samples():
    """Create multiple sample datasets for different scenarios"""
    
    samples = [
        {
            "path": "sample_data/small_test.tif",
            "width": 256,
            "height": 256,
            "description": "Small test image for quick testing"
        },
        {
            "path": "sample_data/medium_demo.tif", 
            "width": 512,
            "height": 512,
            "description": "Medium-sized demo image"
        },
        {
            "path": "sample_data/large_dataset.tif",
            "width": 1024,
            "height": 1024,
            "description": "Large dataset for comprehensive labeling"
        }
    ]
    
    print("🎯 Creating Multiple Sample Datasets")
    print("=" * 50)
    
    created_files = []
    
    for sample in samples:
        print(f"\\n📊 {sample['description']}")
        try:
            output_path = create_sample_raster(
                sample["path"], 
                sample["width"], 
                sample["height"]
            )
            created_files.append(output_path)
        except Exception as e:
            print(f"❌ Failed to create {sample['path']}: {e}")
    
    print(f"\\n✅ Created {len(created_files)} sample datasets:")
    for file_path in created_files:
        print(f"   {file_path}")
    
    return created_files

def main():
    """Main function to create sample data"""
    
    print("🛰️ SATERYS Sample Data Generator")
    print("=" * 40)
    print()
    
    try:
        # Create a single demo dataset
        demo_file = create_sample_raster()
        
        print("\\n🎯 Sample data created successfully!")
        print("\\nNext steps:")
        print("1. Run the basic labeling example:")
        print("   python basic_labeling.py")
        print("\\n2. Or use in SATERYS pipeline:")
        print("   - Add manual_labeler node")
        print(f"   - Set input_path to: {demo_file}")
        print("   - Configure your classes and run!")
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())