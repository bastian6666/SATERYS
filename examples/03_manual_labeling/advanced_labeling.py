#!/usr/bin/env python3
"""
Advanced Manual Labeling Example

This script demonstrates advanced configuration options for the SATERYS
Manual Labeler, including custom class schemes, performance tuning,
and integration with existing workflows.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add the parent directories to the path to import saterys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from saterys.nodes.training_sample import run as manual_labeler_run

def land_cover_classification():
    """Advanced example for land cover classification with many classes"""
    
    print("🌍 Advanced Land Cover Classification Example")
    print("=" * 55)
    
    # Advanced class scheme for detailed land cover mapping
    land_cover_classes = [
        # Water bodies
        {"id": 10, "name": "Open Water", "color": "#0066CC"},
        {"id": 11, "name": "Wetlands", "color": "#4C9A2A"},
        
        # Vegetation
        {"id": 20, "name": "Deciduous Forest", "color": "#228B22"},
        {"id": 21, "name": "Evergreen Forest", "color": "#006400"},
        {"id": 22, "name": "Mixed Forest", "color": "#32CD32"},
        {"id": 23, "name": "Grassland", "color": "#9ACD32"},
        {"id": 24, "name": "Pasture/Hay", "color": "#ADFF2F"},
        {"id": 25, "name": "Cultivated Crops", "color": "#FFD700"},
        
        # Developed areas
        {"id": 30, "name": "Developed Open Space", "color": "#CCCCCC"},
        {"id": 31, "name": "Developed Low Intensity", "color": "#999999"},
        {"id": 32, "name": "Developed Medium Intensity", "color": "#666666"},
        {"id": 33, "name": "Developed High Intensity", "color": "#333333"},
        
        # Barren
        {"id": 40, "name": "Barren Land", "color": "#D2B48C"},
        {"id": 41, "name": "Beaches/Sand", "color": "#F4A460"},
        {"id": 42, "name": "Rock/Stone", "color": "#8B7D6B"},
    ]
    
    # Advanced configuration
    config = {
        # Input data
        "input_path": "sample_data/large_dataset.tif",
        
        # Output configuration
        "class_raster_path": "./results/advanced_land_cover_labels.tif",
        "points_path": "./results/advanced_land_cover_points.gpkg",
        "classes_path": "./results/land_cover_classes.json",
        
        # Class definitions
        "classes": land_cover_classes,
        "persist_classes": True,
        
        # Performance settings
        "brush_size_px": 5,  # Larger brush for efficiency
        
        # Server configuration
        "host": "127.0.0.1",
        "port": 8091,  # Different port to avoid conflicts
        "open_browser": True,
        "port_autoselect": True,
        "max_port_scans": 20,
        
        # Optional: Custom tile server (if you have one)
        # "raster_tile_url_template": "https://your-tile-server.com/{z}/{x}/{y}.png"
    }
    
    return run_labeling_session(config, "advanced-land-cover")

def urban_analysis():
    """Example focused on urban area analysis"""
    
    print("🏙️ Urban Analysis Example")
    print("=" * 30)
    
    # Urban-focused classification scheme
    urban_classes = [
        {"id": 1, "name": "Buildings", "color": "#8B0000"},
        {"id": 2, "name": "Roads", "color": "#2F4F4F"},
        {"id": 3, "name": "Parking Lots", "color": "#696969"},
        {"id": 4, "name": "Green Spaces", "color": "#228B22"},
        {"id": 5, "name": "Water Features", "color": "#4682B4"},
        {"id": 6, "name": "Construction", "color": "#DEB887"},
        {"id": 7, "name": "Industrial", "color": "#800080"},
    ]
    
    config = {
        "input_path": "sample_data/medium_demo.tif",
        "class_raster_path": "./results/urban_labels.tif",
        "points_path": "./results/urban_points.gpkg",
        "classes": urban_classes,
        "brush_size_px": 2,  # Smaller brush for detailed urban features
        "port": 8092,
        "port_autoselect": True,
    }
    
    return run_labeling_session(config, "urban-analysis")

def agricultural_monitoring():
    """Example for agricultural field monitoring"""
    
    print("🚜 Agricultural Monitoring Example")
    print("=" * 35)
    
    # Agriculture-focused classes
    ag_classes = [
        {"id": 1, "name": "Corn", "color": "#FFD700"},
        {"id": 2, "name": "Soybeans", "color": "#32CD32"},
        {"id": 3, "name": "Wheat", "color": "#DEB887"},
        {"id": 4, "name": "Pasture", "color": "#9ACD32"},
        {"id": 5, "name": "Fallow", "color": "#D2691E"},
        {"id": 6, "name": "Orchard", "color": "#228B22"},
        {"id": 7, "name": "Vineyard", "color": "#800080"},
        {"id": 8, "name": "Farm Buildings", "color": "#8B4513"},
        {"id": 9, "name": "Water (Irrigation)", "color": "#4682B4"},
    ]
    
    config = {
        "input_path": "sample_data/small_test.tif",
        "class_raster_path": "./results/agriculture_labels.tif",
        "points_path": "./results/agriculture_points.gpkg",
        "classes": ag_classes,
        "brush_size_px": 4,  # Medium brush for field-scale features
        "port": 8093,
        "port_autoselect": True,
    }
    
    return run_labeling_session(config, "agriculture-monitoring")

def run_labeling_session(config, session_name):
    """Run a manual labeling session with given configuration"""
    
    # Ensure output directory exists
    os.makedirs("results", exist_ok=True)
    
    # Create sample data if needed
    if not os.path.exists(config["input_path"]):
        print(f"Input file not found: {config['input_path']}")
        print("Creating sample data...")
        
        # Import the sample data creator
        from create_sample_data import create_sample_raster
        
        # Determine appropriate size based on filename
        if "large" in config["input_path"]:
            width, height = 1024, 1024
        elif "medium" in config["input_path"]:
            width, height = 512, 512
        else:
            width, height = 256, 256
            
        create_sample_raster(config["input_path"], width, height)
    
    # Save configuration for reference
    config_file = f"./results/{session_name}_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📁 Configuration saved to: {config_file}")
    print(f"📊 Input raster: {config['input_path']}")
    print(f"🎯 Output labels: {config['class_raster_path']}")
    print(f"📍 Output points: {config['points_path']}")
    print(f"🎨 Number of classes: {len(config['classes'])}")
    print()
    
    try:
        # Run the manual labeler
        inputs = {}
        context = {"nodeId": session_name}
        
        result = manual_labeler_run(config, inputs, context)
        
        print("✅ Manual Labeler started successfully!")
        
        # Extract URL
        labeler_url = None
        for item in result:
            if isinstance(item, dict) and item.get("type") == "info":
                message = item.get("message", "")
                if "Labeler at" in message:
                    labeler_url = message.split("Labeler at ")[-1]
                    break
        
        if labeler_url:
            print(f"🌐 Labeling Interface: {labeler_url}")
            print()
            print("📋 Advanced Features Available:")
            print("   • Class management (add/edit/remove)")
            print("   • Attribute table with search and sorting")
            print("   • Bulk operations (select multiple, delete)")
            print("   • Export to multiple formats (GPKG, CSV)")
            print("   • Undo/redo functionality")
            print("   • Keyboard shortcuts for efficiency")
            print()
            print("💡 Tips for this session:")
            print(f"   • {len(config['classes'])} classes defined")
            print(f"   • Use brush size {config['brush_size_px']} for efficiency")
            print("   • Focus on representative samples per class")
            print("   • Save frequently (Ctrl+S or Save button)")
            print()
            print("🔴 Press Ctrl+C to stop when finished")
            
            # Keep server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\\n🛑 Stopping {session_name} session...")
                print("✅ Session completed!")
                
                # Show output summary
                print("\\n📊 Session Summary:")
                if os.path.exists(config["points_path"]):
                    try:
                        import fiona
                        with fiona.open(config["points_path"]) as src:
                            point_count = len(list(src))
                        print(f"   • {point_count} points labeled")
                    except Exception:
                        print(f"   • Points saved to: {config['points_path']}")
                
                if os.path.exists(config["class_raster_path"]):
                    print(f"   • Label raster: {config['class_raster_path']}")
                
                if os.path.exists(config["classes_path"]):
                    print(f"   • Class definitions: {config['classes_path']}")
                
        else:
            print("❌ Could not extract labeler URL")
            return 1
            
    except Exception as e:
        print(f"❌ Error in {session_name}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def main():
    """Main function with menu for different examples"""
    
    print("🎯 SATERYS Advanced Manual Labeling Examples")
    print("=" * 50)
    print()
    print("Choose an example scenario:")
    print("1. Land Cover Classification (15 classes)")
    print("2. Urban Analysis (7 classes)")
    print("3. Agricultural Monitoring (9 classes)")
    print("4. Custom configuration (enter your own)")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                return land_cover_classification()
            elif choice == "2":
                return urban_analysis()
            elif choice == "3":
                return agricultural_monitoring()
            elif choice == "4":
                print("\\n📝 For custom configuration, edit this script")
                print("   or create your own based on the examples above.")
                return 0
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\\n👋 Goodbye!")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

if __name__ == "__main__":
    exit(main())