#!/usr/bin/env python3
"""
Example: Hello World with SATERYS

This example demonstrates the most basic SATERYS operation:
executing a simple "hello" node via the REST API.

Requirements:
- SATERYS running on localhost:8000
- No additional dependencies

Usage:
    python hello_world.py

Expected Output:
    {'text': 'hello SATERYS'}
"""

import requests
import sys

# Configuration
API_BASE = "http://localhost:8000"

def check_saterys_connection():
    """Check if SATERYS is running"""
    try:
        response = requests.get(f"{API_BASE}/node_types", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def run_hello_node(name="SATERYS"):
    """Execute a hello node"""
    
    payload = {
        "nodeId": "hello-example",
        "type": "hello",
        "args": {"name": name},
        "inputs": {}
    }
    
    try:
        response = requests.post(f"{API_BASE}/run_node", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result["ok"]:
            return result["output"]
        else:
            print(f"❌ Node execution failed: {result['error']}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None

def main():
    """Main example function"""
    
    print("🚀 SATERYS Hello World Example")
    print("=" * 40)
    
    # Check connection
    print("🔍 Checking SATERYS connection...")
    if not check_saterys_connection():
        print("❌ SATERYS is not running or not accessible")
        print("💡 Start SATERYS with: saterys")
        sys.exit(1)
    
    print("✅ SATERYS is running")
    
    # Run hello node with different names
    names = ["World", "SATERYS", "Geospatial Community", "你好"]
    
    for name in names:
        print(f"\n👋 Running hello node with name: '{name}'")
        result = run_hello_node(name)
        
        if result:
            print(f"📤 Output: {result}")
        else:
            print("❌ Failed to get result")
    
    print("\n✅ Hello World example completed successfully!")

if __name__ == "__main__":
    main()