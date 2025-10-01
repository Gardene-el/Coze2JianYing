#!/usr/bin/env python3
"""
Test for make_effect_info tool

Tests the new effect functionality:
1. make_effect_info tool generates correct JSON strings
2. Parameter validation works correctly
3. Optional parameters are handled properly
"""

import os
import json
import sys
import importlib.util

# Add project path at the beginning to avoid conflicts
sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def load_handler_module():
    """Load handler module using importlib to avoid package conflicts"""
    # Mock runtime module first
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    # Load the handler module directly
    spec = importlib.util.spec_from_file_location(
        "make_effect_info_handler",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/make_effect_info/handler.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules['make_effect_info_handler'] = module
    spec.loader.exec_module(module)
    
    return module


def test_make_effect_info_basic():
    """Test basic make_effect_info functionality"""
    print("=== Testing make_effect_info basic functionality ===")
    
    handler_module = load_handler_module()
    handler = handler_module.handler
    Input = handler_module.Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Minimal required parameters
    print("\nTest 1: Minimal parameters")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    assert result["effect_info_string"], "Should return a string"
    
    # Parse and verify the output
    parsed = json.loads(result["effect_info_string"])
    assert parsed["effect_type"] == "模糊"
    assert parsed["start"] == 0
    assert parsed["end"] == 3000
    print(f"✅ Output: {result["effect_info_string"]}")
    
    # Test 2: With optional parameters
    print("\nTest 2: With optional parameters")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=5000,
        intensity=0.7,
        position_x=0.5,
        position_y=0.5,
        scale=1.5
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    parsed = json.loads(result["effect_info_string"])
    assert parsed["intensity"] == 0.7
    assert parsed["position_x"] == 0.5
    assert parsed["scale"] == 1.5
    print(f"✅ Output with optional params: {result["effect_info_string"]}")
    
    # Test 3: Default values should not be included
    print("\nTest 3: Default values not included")
    input_data = Input(
        effect_type="锐化",
        start=0,
        end=3000,
        intensity=1.0,  # Default value
        scale=1.0       # Default value
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert "intensity" not in parsed, "Default intensity should not be included"
    assert "scale" not in parsed, "Default scale should not be included"
    print(f"✅ Default values excluded: {result["effect_info_string"]}")
    
    # Test 4: With custom properties
    print("\nTest 4: Custom properties")
    custom_props = {"blur_radius": 15, "edge_detection": True}
    input_data = Input(
        effect_type="高级模糊",
        start=1000,
        end=4000,
        intensity=0.9,
        properties=json.dumps(custom_props)
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert parsed["effect_type"] == "高级模糊"
    assert parsed["properties"]["blur_radius"] == 15
    assert parsed["properties"]["edge_detection"] == True
    print(f"✅ Custom properties: {result["effect_info_string"]}")
    
    # Test 5: Position parameters
    print("\nTest 5: Position parameters")
    input_data = Input(
        effect_type="马赛克",
        start=0,
        end=2000,
        position_x=100.5,
        position_y=200.3
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert parsed["position_x"] == 100.5
    assert parsed["position_y"] == 200.3
    print(f"✅ Position parameters: {result["effect_info_string"]}")
    
    print("\n✅ All make_effect_info basic tests passed!")
    return True


def test_make_effect_info_validation():
    """Test parameter validation"""
    print("\n=== Testing make_effect_info validation ===")
    
    handler_module = load_handler_module()
    handler = handler_module.handler
    Input = handler_module.Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Missing effect_type
    print("\nTest 1: Error handling - missing effect_type")
    input_data = Input(
        effect_type="",
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with missing effect_type"
    assert "effect_type" in result["message"]
    print(f"✅ Error handling works: {result["message"]}")
    
    # Test 2: Invalid time range
    print("\nTest 2: Error handling - invalid time range")
    input_data = Input(
        effect_type="模糊",
        start=5000,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with invalid time range"
    assert "时间" in result["message"] or "start" in result["message"] or "end" in result["message"]
    print(f"✅ Time range validation works: {result["message"]}")
    
    # Test 3: Negative start time
    print("\nTest 3: Error handling - negative start time")
    input_data = Input(
        effect_type="模糊",
        start=-1000,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with negative start time"
    print(f"✅ Negative time validation works: {result["message"]}")
    
    # Test 4: Invalid properties JSON
    print("\nTest 4: Error handling - invalid properties JSON")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=3000,
        properties="not valid json"
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with invalid JSON"
    assert "JSON" in result["message"] or "properties" in result["message"]
    print(f"✅ JSON validation works: {result["message"]}")
    
    print("\n✅ All make_effect_info validation tests passed!")
    return True


def test_make_effect_info_edge_cases():
    """Test edge cases"""
    print("\n=== Testing make_effect_info edge cases ===")
    
    handler_module = load_handler_module()
    handler = handler_module.handler
    Input = handler_module.Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Zero intensity
    print("\nTest 1: Zero intensity")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=3000,
        intensity=0.0
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert parsed["intensity"] == 0.0
    print(f"✅ Zero intensity: {result["effect_info_string"]}")
    
    # Test 2: Very long duration
    print("\nTest 2: Very long duration")
    input_data = Input(
        effect_type="黑白",
        start=0,
        end=3600000  # 1 hour
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert parsed["end"] == 3600000
    print(f"✅ Long duration: {result["effect_info_string"]}")
    
    # Test 3: Empty properties dict
    print("\nTest 3: Empty properties dict")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=3000,
        properties="{}"
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert "properties" not in parsed, "Empty properties should not be included"
    print(f"✅ Empty properties excluded: {result["effect_info_string"]}")
    
    # Test 4: Negative position values
    print("\nTest 4: Negative position values")
    input_data = Input(
        effect_type="模糊",
        start=0,
        end=3000,
        position_x=-50.0,
        position_y=-100.0
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["effect_info_string"])
    assert parsed["position_x"] == -50.0
    assert parsed["position_y"] == -100.0
    print(f"✅ Negative positions: {result["effect_info_string"]}")
    
    # Test 5: Chinese effect names
    print("\nTest 5: Chinese effect names")
    chinese_effects = ["模糊", "锐化", "马赛克", "黑白", "怀旧", "色彩校正"]
    for effect in chinese_effects:
        input_data = Input(
            effect_type=effect,
            start=0,
            end=1000
        )
        result = handler(MockArgs(input_data))
        assert result["success"]
        parsed = json.loads(result["effect_info_string"])
        assert parsed["effect_type"] == effect
    print(f"✅ Chinese effect names: {len(chinese_effects)} effects tested")
    
    print("\n✅ All make_effect_info edge case tests passed!")
    return True


if __name__ == "__main__":
    print("Starting make_effect_info tests...\n")
    
    results = []
    
    try:
        results.append(test_make_effect_info_basic())
        results.append(test_make_effect_info_validation())
        results.append(test_make_effect_info_edge_cases())
        
        print(f"\n{'='*50}")
        print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
        print(f"{'='*50}")
        
        if all(results):
            print("\n🎉 All make_effect_info tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
