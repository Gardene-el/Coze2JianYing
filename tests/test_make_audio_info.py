#!/usr/bin/env python3
"""
Test for make_audio_info tool

Tests the new audio functionality:
1. make_audio_info tool generates correct JSON strings
2. Parameter validation works correctly
3. Optional parameters are handled properly
"""

import os
import json
import sys

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def test_make_audio_info_basic():
    """Test basic make_audio_info functionality"""
    print("=== Testing make_audio_info basic functionality ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_audio_info.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Minimal required parameters
    print("\nTest 1: Minimal parameters")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    assert result["audio_info_string"], "Should return a string"
    
    # Parse and verify the output
    parsed = json.loads(result["audio_info_string"])
    assert parsed["audio_url"] == "https://example.com/audio.mp3"
    assert parsed["start"] == 0
    assert parsed["end"] == 5000
    print(f"✅ Output: {result["audio_info_string"]}")
    
    # Test 2: With optional parameters
    print("\nTest 2: With optional parameters")
    input_data = Input(
        audio_url="https://example.com/bgm.mp3",
        start=0,
        end=30000,
        volume=0.7,
        fade_in=2000,
        fade_out=3000,
        speed=1.2
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    parsed = json.loads(result["audio_info_string"])
    assert parsed["volume"] == 0.7
    assert parsed["fade_in"] == 2000
    assert parsed["fade_out"] == 3000
    assert parsed["speed"] == 1.2
    print(f"✅ Output with optional params: {result["audio_info_string"]}")
    
    # Test 3: Default values should not be included
    print("\nTest 3: Default values not included")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        volume=1.0,  # Default value
        speed=1.0    # Default value
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert "volume" not in parsed, "Default volume should not be included"
    assert "speed" not in parsed, "Default speed should not be included"
    print(f"✅ Default values excluded: {result["audio_info_string"]}")
    
    # Test 4: Audio effects
    print("\nTest 4: Audio effects")
    input_data = Input(
        audio_url="https://example.com/voice.mp3",
        start=0,
        end=10000,
        effect_type="变声",
        effect_intensity=0.8
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert parsed["effect_type"] == "变声"
    assert parsed["effect_intensity"] == 0.8
    print(f"✅ Audio effects: {result["audio_info_string"]}")
    
    # Test 5: Material range (trimming)
    print("\nTest 5: Material range")
    input_data = Input(
        audio_url="https://example.com/long_audio.mp3",
        start=0,
        end=20000,
        material_start=10000,
        material_end=30000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert parsed["material_start"] == 10000
    assert parsed["material_end"] == 30000
    print(f"✅ Material range: {result["audio_info_string"]}")
    
    print("\n✅ All basic functionality tests passed!")
    return True


def test_make_audio_info_validation():
    """Test parameter validation"""
    print("\n=== Testing parameter validation ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_audio_info.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Missing required field
    print("\nTest 1: Missing audio_url")
    input_data = Input(
        audio_url="",
        start=0,
        end=5000
    )
    result = handler(MockArgs(input_data))
    assert not result["success"], "Should fail with missing audio_url"
    assert "audio_url" in result["message"]
    print(f"✅ Correctly rejected: {result["message"]}")
    
    # Test 2: Invalid time range
    print("\nTest 2: Invalid time range")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=5000,
        end=3000  # end < start
    )
    result = handler(MockArgs(input_data))
    assert not result["success"], "Should fail with invalid time range"
    print(f"✅ Correctly rejected: {result["message"]}")
    
    # Test 3: Invalid volume
    print("\nTest 3: Invalid volume")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        volume=3.0  # > 2.0
    )
    result = handler(MockArgs(input_data))
    assert not result["success"], "Should fail with invalid volume"
    assert "volume" in result["message"]
    print(f"✅ Correctly rejected: {result["message"]}")
    
    # Test 4: Invalid speed
    print("\nTest 4: Invalid speed")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        speed=0.3  # < 0.5
    )
    result = handler(MockArgs(input_data))
    assert not result["success"], "Should fail with invalid speed"
    assert "speed" in result["message"]
    print(f"✅ Correctly rejected: {result["message"]}")
    
    # Test 5: Incomplete material range
    print("\nTest 5: Incomplete material range")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        material_start=1000  # missing material_end
    )
    result = handler(MockArgs(input_data))
    assert not result["success"], "Should fail with incomplete material range"
    assert "material_start" in result["message"] or "material_end" in result["message"]
    print(f"✅ Correctly rejected: {result["message"]}")
    
    print("\n✅ All validation tests passed!")
    return True


def test_make_audio_info_edge_cases():
    """Test edge cases"""
    print("\n=== Testing edge cases ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_audio_info.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Zero fade times (valid)
    print("\nTest 1: Zero fade times")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        fade_in=0,
        fade_out=0
    )
    result = handler(MockArgs(input_data))
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert "fade_in" not in parsed  # Default value, should not be included
    assert "fade_out" not in parsed
    print("✅ Zero fade times handled correctly")
    
    # Test 2: Maximum volume
    print("\nTest 2: Maximum volume")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        volume=2.0
    )
    result = handler(MockArgs(input_data))
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert parsed["volume"] == 2.0
    print("✅ Maximum volume accepted")
    
    # Test 3: Minimum speed
    print("\nTest 3: Minimum speed")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        speed=0.5
    )
    result = handler(MockArgs(input_data))
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert parsed["speed"] == 0.5
    print("✅ Minimum speed accepted")
    
    # Test 4: Effect without intensity (should use default)
    print("\nTest 4: Effect without custom intensity")
    input_data = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=5000,
        effect_type="混响",
        effect_intensity=1.0  # Default value
    )
    result = handler(MockArgs(input_data))
    assert result["success"]
    parsed = json.loads(result["audio_info_string"])
    assert parsed["effect_type"] == "混响"
    assert "effect_intensity" not in parsed  # Default value, should not be included
    print("✅ Effect with default intensity handled correctly")
    
    print("\n✅ All edge case tests passed!")
    return True


if __name__ == "__main__":
    results = []
    
    try:
        results.append(test_make_audio_info_basic())
        results.append(test_make_audio_info_validation())
        results.append(test_make_audio_info_edge_cases())
        
        print(f"\n{'='*50}")
        print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
        print(f"{'='*50}")
        
        if all(results):
            print("✅ All tests passed successfully!")
            sys.exit(0)
        else:
            print("❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
