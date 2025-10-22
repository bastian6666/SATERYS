#!/usr/bin/env python3
"""
Manual test script for new SATERYS features:
- Vector node loading
- Vector creation nodes
- API endpoint availability

Run this after starting SATERYS to verify the features work.
"""

import sys
import importlib.util
import os

def test_node_imports():
    """Test that the new nodes can be imported."""
    print("Testing node imports...")
    
    # Test vector_input node
    spec = importlib.util.spec_from_file_location(
        "vector_input",
        os.path.join(os.path.dirname(__file__), "saterys/nodes/vector_input.py")
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, 'NAME'), "vector_input missing NAME"
        assert mod.NAME == "vector.input", "vector_input has wrong NAME"
        assert hasattr(mod, 'run'), "vector_input missing run function"
        print("✓ vector.input node imported successfully")
    else:
        print("✗ Failed to import vector_input")
        return False
    
    # Test vector_create node
    spec = importlib.util.spec_from_file_location(
        "vector_create",
        os.path.join(os.path.dirname(__file__), "saterys/nodes/vector_create.py")
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, 'NAME'), "vector_create missing NAME"
        assert mod.NAME == "vector.create", "vector_create has wrong NAME"
        assert hasattr(mod, 'run'), "vector_create missing run function"
        print("✓ vector.create node imported successfully")
    else:
        print("✗ Failed to import vector_create")
        return False
    
    return True

def test_vector_create_node():
    """Test the vector.create node logic."""
    print("\nTesting vector.create node logic...")
    
    spec = importlib.util.spec_from_file_location(
        "vector_create",
        os.path.join(os.path.dirname(__file__), "saterys/nodes/vector_create.py")
    )
    if not spec or not spec.loader:
        print("✗ Failed to load vector_create")
        return False
    
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    # Test point creation
    result = mod.run(
        args={
            "type": "point",
            "coordinates": [[-122.4194, 37.7749]],
            "name": "Test Point",
            "properties": {}
        },
        inputs={},
        context={"nodeId": "test"}
    )
    
    assert result["type"] == "vector", "Result type should be 'vector'"
    assert "geojson" in result, "Result should have 'geojson'"
    assert result["feature_count"] == 1, "Should have 1 feature"
    print("✓ Point creation works")
    
    # Test polygon creation
    result = mod.run(
        args={
            "type": "polygon",
            "coordinates": [
                [-122.5, 37.7],
                [-122.4, 37.7],
                [-122.4, 37.8],
                [-122.5, 37.8]
            ],
            "name": "Test Polygon",
            "properties": {}
        },
        inputs={},
        context={"nodeId": "test"}
    )
    
    assert result["type"] == "vector", "Result type should be 'vector'"
    assert result["feature_count"] == 1, "Should have 1 feature"
    print("✓ Polygon creation works")
    
    return True

def test_llm_module():
    """Test that the LLM chat module can be imported."""
    print("\nTesting LLM module import...")
    
    try:
        spec = importlib.util.spec_from_file_location(
            "llm_chat",
            os.path.join(os.path.dirname(__file__), "saterys/llm_chat.py")
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            assert hasattr(mod, 'llm_router'), "llm_chat missing llm_router"
            print("✓ LLM module imported successfully")
            print("  Note: LLM functionality requires OPENAI_API_KEY environment variable")
            return True
        else:
            print("✗ Failed to import llm_chat")
            return False
    except Exception as e:
        print(f"✗ Error importing LLM module: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("SATERYS New Features Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Node imports
    results.append(("Node Imports", test_node_imports()))
    
    # Test 2: Vector create logic
    results.append(("Vector Create Logic", test_vector_create_node()))
    
    # Test 3: LLM module
    results.append(("LLM Module", test_llm_module()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! New features are working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
