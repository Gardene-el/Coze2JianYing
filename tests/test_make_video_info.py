#!/usr/bin/env python3
"""
Test the make_video_info tool functionality

Tests the video info string generation with all parameter combinations,
validation, and error handling.
"""

import json
import sys
import types
from typing import Generic, TypeVar

# Setup mock runtime for testing
T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

# Now import the handler
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
from tools.make_video_info.handler import handler, Input


class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def test_make_video_info_basic():
    """Test basic make_video_info functionality"""
    print("=== Testing make_video_info basic functionality ===\n")
    
    # Test 1: Minimal parameters
    print("Test 1: Minimal parameters")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    parsed = json.loads(result["video_info_string"])
    assert parsed["video_url"] == "https://example.com/video.mp4"
    assert parsed["start"] == 0
    assert parsed["end"] == 5000
    print(f"✅ Output: {result["video_info_string"]}\n")
    
    # Test 2: With optional parameters including video-specific ones
    print("Test 2: With optional parameters including video-specific ones")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        material_start=1000,
        material_end=6000,
        speed=1.5,
        filter_type="暖冬",
        scale_x=1.2
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    parsed = json.loads(result["video_info_string"])
    assert parsed["material_start"] == 1000
    assert parsed["material_end"] == 6000
    assert parsed["speed"] == 1.5
    assert parsed["filter_type"] == "暖冬"
    assert parsed["scale_x"] == 1.2
    print(f"✅ Output with optional params: {result["video_info_string"][:100]}...\n")
    
    # Test 3: Default values should not be included
    print("Test 3: Default values not included")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        scale_x=1.0,  # Default value
        scale_y=1.0,  # Default value
        opacity=1.0,  # Default value
        speed=1.0     # Default value
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert "scale_x" not in parsed, "Default scale_x should not be included"
    assert "scale_y" not in parsed, "Default scale_y should not be included"
    assert "opacity" not in parsed, "Default opacity should not be included"
    assert "speed" not in parsed, "Default speed should not be included"
    print("✅ Default values correctly excluded\n")
    
    # Test 4: Error handling - missing required field
    print("Test 4: Error handling - missing video_url")
    input_data = Input(
        video_url="",  # Empty
        start=0,
        end=5000
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with empty video_url"
    assert "video_url" in result["message"]
    print(f"✅ Error handling works: {result["message"]}\n")
    
    # Test 5: Error handling - invalid time range
    print("Test 5: Error handling - invalid time range")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=5000,
        end=1000  # end < start
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with invalid time range"
    assert "end 时间必须大于 start 时间" in result["message"]
    print(f"✅ Time range validation works: {result["message"]}\n")
    
    # Test 6: Error handling - invalid material range
    print("Test 6: Error handling - invalid material range")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        material_start=1000,
        material_end=500  # material_end < material_start
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with invalid material range"
    assert "material_end 时间必须大于 material_start 时间" in result["message"]
    print(f"✅ Material range validation works: {result["message"]}\n")
    
    # Test 7: Error handling - material_start without material_end
    print("Test 7: Error handling - material_start without material_end")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        material_start=1000
        # material_end not provided
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail when only one material parameter is provided"
    assert "material_start 和 material_end 必须同时提供" in result["message"]
    print(f"✅ Material range pairing validation works: {result["message"]}\n")
    
    # Test 8: Error handling - invalid speed
    print("Test 8: Error handling - invalid speed")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        speed=3.0  # Too high
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with invalid speed"
    assert "speed 必须在 0.5 到 2.0 之间" in result["message"]
    print(f"✅ Speed validation works: {result["message"]}\n")
    
    print("✅ All make_video_info basic tests passed!\n")
    return True


def test_video_specific_features():
    """Test video-specific features (material_range, speed, reverse)"""
    print("=== Testing video-specific features ===\n")
    
    # Test 1: Material range
    print("Test 1: Material range")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        material_start=2000,
        material_end=7000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert "material_start" in parsed
    assert "material_end" in parsed
    assert parsed["material_start"] == 2000
    assert parsed["material_end"] == 7000
    print(f"✅ Material range: {result["video_info_string"]}\n")
    
    # Test 2: Speed control
    print("Test 2: Speed control")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        speed=1.5
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert "speed" in parsed
    assert parsed["speed"] == 1.5
    print(f"✅ Speed control: {result["video_info_string"]}\n")
    
    # Test 3: Reverse playback
    print("Test 3: Reverse playback")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        reverse=True
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert "reverse" in parsed
    assert parsed["reverse"] is True
    print(f"✅ Reverse playback: {result["video_info_string"]}\n")
    
    # Test 4: Combined speed and reverse
    print("Test 4: Combined speed and reverse")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        speed=0.5,
        reverse=True
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert parsed["speed"] == 0.5
    assert parsed["reverse"] is True
    print(f"✅ Combined speed and reverse: {result["video_info_string"]}\n")
    
    # Test 5: All video-specific parameters
    print("Test 5: All video-specific parameters")
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=10000,
        material_start=5000,
        material_end=15000,
        speed=2.0,
        reverse=True,
        position_x=0.1,
        scale_x=1.2,
        filter_type="暖冬",
        background_blur=True
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert parsed["material_start"] == 5000
    assert parsed["material_end"] == 15000
    assert parsed["speed"] == 2.0
    assert parsed["reverse"] is True
    assert parsed["position_x"] == 0.1
    assert parsed["scale_x"] == 1.2
    assert parsed["filter_type"] == "暖冬"
    assert parsed["background_blur"] is True
    print(f"✅ All video-specific parameters: {result["video_info_string"]}\n")
    
    print("✅ All video-specific feature tests passed!\n")
    return True


def test_chinese_support():
    """Test Chinese character support in filter names"""
    print("=== Testing Chinese character support ===\n")
    
    input_data = Input(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        filter_type="暖冬",
        transition_type="淡入淡出"
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["video_info_string"])
    assert parsed["filter_type"] == "暖冬"
    assert parsed["transition_type"] == "淡入淡出"
    
    # Verify JSON is properly encoded
    assert "暖冬" in result["video_info_string"]
    assert "淡入淡出" in result["video_info_string"]
    
    print(f"✅ Chinese characters correctly handled: {result["video_info_string"]}\n")
    print("✅ Chinese character support test passed!\n")
    return True


if __name__ == "__main__":
    print("Starting make_video_info tests...\n")
    
    results = []
    results.append(test_make_video_info_basic())
    results.append(test_video_specific_features())
    results.append(test_chinese_support())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
