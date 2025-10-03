#!/usr/bin/env python3
"""
Test flip_horizontal and flip_vertical parameters

This test validates that the flip parameters work correctly in:
- make_video_info (flip parameters applicable to videos)
- add_videos (flip parameters applicable to videos)

Note: flip parameters are NOT applicable to images per draft_generator_interface specification.
Images are processed as static VideoSegments and do not support flip operations.
"""

# Mock runtime module
import sys
import types
from typing import Generic, TypeVar

runtime = types.ModuleType('runtime')

T = TypeVar('T')

class Args(Generic[T]):
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None

runtime.Args = Args

sys.modules['runtime'] = runtime

# Now import the handlers
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.make_video_info.handler import handler as make_video_handler, Input as VideoInput


def test_make_video_info_flip_parameters():
    """Test flip parameters in make_video_info"""
    print("=== Testing make_video_info flip parameters ===")
    
    # Test 1: flip_horizontal only
    print("\nTest 1: flip_horizontal only")
    input_data = VideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        flip_horizontal=True
    )
    result = make_video_handler(Args(input_data))
    
    assert result["success"] == True, "Should succeed"
    video_info = json.loads(result["video_info_string"])
    assert "flip_horizontal" in video_info, "Should include flip_horizontal"
    assert video_info["flip_horizontal"] == True, "flip_horizontal should be True"
    assert "flip_vertical" not in video_info, "Should not include flip_vertical (default False)"
    print(f"✅ flip_horizontal only: {result['video_info_string']}")
    
    # Test 2: flip_vertical only
    print("\nTest 2: flip_vertical only")
    input_data = VideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        flip_vertical=True
    )
    result = make_video_handler(Args(input_data))
    
    assert result["success"] == True, "Should succeed"
    video_info = json.loads(result["video_info_string"])
    assert "flip_vertical" in video_info, "Should include flip_vertical"
    assert video_info["flip_vertical"] == True, "flip_vertical should be True"
    assert "flip_horizontal" not in video_info, "Should not include flip_horizontal (default False)"
    print(f"✅ flip_vertical only: {result['video_info_string']}")
    
    # Test 3: both flip parameters
    print("\nTest 3: both flip parameters")
    input_data = VideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        flip_horizontal=True,
        flip_vertical=True
    )
    result = make_video_handler(Args(input_data))
    
    assert result["success"] == True, "Should succeed"
    video_info = json.loads(result["video_info_string"])
    assert "flip_horizontal" in video_info, "Should include flip_horizontal"
    assert "flip_vertical" in video_info, "Should include flip_vertical"
    assert video_info["flip_horizontal"] == True, "flip_horizontal should be True"
    assert video_info["flip_vertical"] == True, "flip_vertical should be True"
    print(f"✅ Both flip parameters: {result['video_info_string']}")
    
    # Test 4: default (no flip) - should not appear in output
    print("\nTest 4: default (no flip)")
    input_data = VideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000
    )
    result = make_video_handler(Args(input_data))
    
    assert result["success"] == True, "Should succeed"
    video_info = json.loads(result["video_info_string"])
    assert "flip_horizontal" not in video_info, "Should not include flip_horizontal when False (default)"
    assert "flip_vertical" not in video_info, "Should not include flip_vertical when False (default)"
    print(f"✅ Default (no flip): {result['video_info_string']}")
    
    print("\n✅ All make_video_info flip parameter tests passed!")
    return True


def test_add_videos_flip_parameters():
    """Test that add_videos correctly handles flip parameters"""
    print("\n=== Testing add_videos with flip parameters ===")
    
    from tools.add_videos.handler import VideoSegmentConfig, TimeRange
    
    # Test creating VideoSegmentConfig with flip parameters
    print("\nTest: Create VideoSegmentConfig with flip parameters")
    
    time_range = TimeRange(0, 5000)
    config = VideoSegmentConfig(
        material_url="https://example.com/video.mp4",
        time_range=time_range,
        flip_horizontal=True,
        flip_vertical=True
    )
    
    assert hasattr(config, 'flip_horizontal'), "Config should have flip_horizontal attribute"
    assert hasattr(config, 'flip_vertical'), "Config should have flip_vertical attribute"
    assert config.flip_horizontal == True, "flip_horizontal should be True"
    assert config.flip_vertical == True, "flip_vertical should be True"
    print("✅ VideoSegmentConfig correctly stores flip parameters")
    
    # Test default values
    print("\nTest: Default flip values")
    config_default = VideoSegmentConfig(
        material_url="https://example.com/video.mp4",
        time_range=time_range
    )
    
    assert config_default.flip_horizontal == False, "Default flip_horizontal should be False"
    assert config_default.flip_vertical == False, "Default flip_vertical should be False"
    print("✅ Default flip values are correct (False)")
    
    print("\n✅ All add_videos flip parameter tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Flip Parameters (flip_horizontal and flip_vertical)")
    print("Note: Flip parameters only apply to videos, not to static images")
    print("=" * 70)
    
    results = []
    results.append(test_make_video_info_flip_parameters())
    results.append(test_add_videos_flip_parameters())
    
    print("\n" + "=" * 70)
    print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
    print("=" * 70)
    
    if all(results):
        print("🎉 All flip parameter tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
