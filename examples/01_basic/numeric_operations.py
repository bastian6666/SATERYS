#!/usr/bin/env python3
"""
Example: Numeric Operations Pipeline

This example demonstrates connecting multiple nodes in a pipeline
to perform numeric operations using SATERYS.

Requirements:
- SATERYS running on localhost:8000
- No additional dependencies

Usage:
    python numeric_operations.py

Expected Output:
    Pipeline results showing connected node operations
"""

import requests
import sys
import json

# Configuration
API_BASE = "http://localhost:8000"

class SATERYSClient:
    """Simple SATERYS API client"""
    
    def __init__(self, base_url=API_BASE):
        self.base_url = base_url
        
    def check_connection(self):
        """Check if SATERYS is accessible"""
        try:
            response = requests.get(f"{self.base_url}/node_types", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_node_types(self):
        """Get available node types"""
        response = requests.get(f"{self.base_url}/node_types")
        return response.json()["types"]
    
    def run_node(self, node_id, node_type, args=None, inputs=None):
        """Execute a node and return the output"""
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

def demonstrate_simple_pipeline():
    """Demonstrate a simple numeric pipeline"""
    
    client = SATERYSClient()
    
    print("\n🔢 Simple Numeric Pipeline")
    print("-" * 30)
    
    # Step 1: Create two "hello" nodes that output numeric-like text
    print("📝 Step 1: Create hello nodes with numeric outputs")
    
    hello1_output = client.run_node(
        "hello-num1",
        "hello", 
        args={"name": "10"}
    )
    print(f"   Hello Node 1 output: {hello1_output}")
    
    hello2_output = client.run_node(
        "hello-num2", 
        "hello",
        args={"name": "5"}
    )
    print(f"   Hello Node 2 output: {hello2_output}")
    
    # Step 2: Use sum node to combine values
    print("\n➕ Step 2: Sum the values using sum node")
    
    sum_output = client.run_node(
        "sum-operation",
        "sum",
        args={"a": 20, "b": 15},  # Direct numeric values
        inputs={
            "hello-num1": hello1_output,
            "hello-num2": hello2_output
        }
    )
    print(f"   Sum Node output: {sum_output}")
    
    return sum_output

def demonstrate_chained_operations():
    """Demonstrate chained numeric operations"""
    
    client = SATERYSClient()
    
    print("\n🔗 Chained Operations")
    print("-" * 25)
    
    # Create a series of sum operations
    results = []
    
    # First operation
    result1 = client.run_node(
        "sum-1",
        "sum", 
        args={"a": 10, "b": 5}
    )
    results.append(("10 + 5", result1))
    print(f"   Operation 1: {result1}")
    
    # Second operation - using different values
    result2 = client.run_node(
        "sum-2",
        "sum",
        args={"a": 100, "b": 23}
    )
    results.append(("100 + 23", result2))
    print(f"   Operation 2: {result2}")
    
    # Third operation - combining with hello node
    hello_result = client.run_node(
        "hello-chain",
        "hello",
        args={"name": "PIPELINE"}
    )
    results.append(("hello PIPELINE", hello_result))
    print(f"   Hello Chain: {hello_result}")
    
    return results

def demonstrate_parameter_variations():
    """Demonstrate different parameter configurations"""
    
    client = SATERYSClient()
    
    print("\n⚙️ Parameter Variations")
    print("-" * 25)
    
    # Test different hello node configurations
    configurations = [
        {"name": "Configuration Test 1"},
        {"name": "SATERYS Rocks!"},
        {"name": "🚀 Emojis work too!"},
        {"name": "123.456"}
    ]
    
    for i, config in enumerate(configurations, 1):
        result = client.run_node(
            f"param-test-{i}",
            "hello",
            args=config
        )
        print(f"   Config {i}: {config} → {result}")
    
    # Test sum node with different numeric values
    sum_tests = [
        {"a": 0, "b": 0},
        {"a": -10, "b": 10}, 
        {"a": 3.14, "b": 2.86},
        {"a": 1000000, "b": 1}
    ]
    
    print("\n   Sum Node Variations:")
    for i, config in enumerate(sum_tests, 1):
        result = client.run_node(
            f"sum-test-{i}",
            "sum",
            args=config
        )
        print(f"   Sum {i}: {config} → {result}")

def main():
    """Main example function"""
    
    print("🚀 SATERYS Numeric Operations Example")
    print("=" * 45)
    
    client = SATERYSClient()
    
    # Check connection
    print("🔍 Checking SATERYS connection...")
    if not client.check_connection():
        print("❌ SATERYS is not running or not accessible")
        print("💡 Start SATERYS with: saterys")
        sys.exit(1)
    
    print("✅ SATERYS is running")
    
    # Show available node types
    print("\n📋 Available Node Types:")
    node_types = client.get_node_types()
    for node_type in node_types:
        print(f"   - {node_type['name']}: {json.dumps(node_type['default_args'], indent=None)}")
    
    try:
        # Run demonstrations
        demonstrate_simple_pipeline()
        demonstrate_chained_operations() 
        demonstrate_parameter_variations()
        
        print("\n✅ Numeric operations example completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()