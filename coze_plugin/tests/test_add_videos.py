#!/usr/bin/env python3
"""
Test the add_videos tool functionality

Tests the complete workflow of adding video segments to existing drafts,
including input validation, video info parsing, and output format verification.
"""

import os
import json
import uuid
import shutil
import tempfile
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

# Now import the handlers
sys.path.append('/home/runner/work/Coze2JianYing/Coze2JianYing')
from coze_plugin.tools.add_videos.handler import handler, Input, parse_video_infos
from coze_plugin.tools.create_draft.handler import handler as create_handler, Input as CreateInput


class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def test_add_videos_basic():
    """Test basic add_videos functionality"""
    print("=== Testing add_videos basic functionality ===\n")
    
    # Step 1: Create a draft first
    create_input = CreateInput(
        draft_name="测试视频草稿",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success, f"Failed to create draft: {create_result.message}"
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}\n")
    
    # Step 2: Prepare video infos
    video_infos = [
        {
            "video_url": "https://example.com/video1.mp4",
            "start": 0,
            "end": 5000
        },
        {
            "video_url": "https://example.com/video2.mp4",
            "start": 5000,
            "end": 10000,
            "speed": 1.5
        }
    ]
    
    video_infos_str = json.dumps(video_infos)
    
    # Step 3: Test add_videos
    add_input = Input(
        draft_id=draft_id,
        video_infos=video_infos_str
    )
    
    result = handler(MockArgs(add_input))
    
    # Verify result
    assert result.success, f"add_videos failed: {result.message}"
    assert len(result.segment_ids) == 2, f"Expected 2 segments, got {len(result.segment_ids)}"
    assert len(result.segment_infos) == 2, f"Expected 2 segment_infos, got {len(result.segment_infos)}"
    
    print(f"✅ Successfully added {len(result.segment_ids)} videos")
    print(f"✅ Segment IDs: {result.segment_ids}\n")
    
    # Step 4: Verify segment_infos format
    for i, info in enumerate(result.segment_infos):
        assert "id" in info, f"segment_infos[{i}] missing 'id' field"
        assert "start" in info, f"segment_infos[{i}] missing 'start' field"
        assert "end" in info, f"segment_infos[{i}] missing 'end' field"
    
    print(f"✅ Segment infos format correct: {result.segment_infos}\n")
    
    # Step 5: Verify draft config was updated
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    assert "tracks" in draft_config
    assert len(draft_config["tracks"]) == 1
    assert draft_config["tracks"][0]["track_type"] == "video"
    assert len(draft_config["tracks"][0]["segments"]) == 2
    
    print("✅ Draft config correctly updated\n")
    print("✅ All basic tests passed!\n")
    return True


def test_array_of_strings():
    """Test add_videos with array of JSON strings (new format)"""
    print("=== Testing add_videos with array of strings ===\n")
    
    # Create a draft
    create_input = CreateInput(
        draft_name="测试数组字符串",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}\n")
    
    # Test 1: Array of JSON strings
    print("Test 1: Array of JSON strings")
    video_infos_array = [
        '{"video_url":"https://example.com/video1.mp4","start":0,"end":5000}',
        '{"video_url":"https://example.com/video2.mp4","start":5000,"end":10000,"speed":1.5}'
    ]
    
    add_input = Input(
        draft_id=draft_id,
        video_infos=video_infos_array
    )
    
    result = handler(MockArgs(add_input))
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 2
    print("✅ Array of strings parsed correctly\n")
    
    # Test 2: Backward compatibility - array of objects
    print("Test 2: Backward compatibility - array of objects")
    video_infos_objects = [
        {"video_url": "https://example.com/video3.mp4", "start": 10000, "end": 15000},
        {"video_url": "https://example.com/video4.mp4", "start": 15000, "end": 20000}
    ]
    
    add_input = Input(
        draft_id=draft_id,
        video_infos=video_infos_objects
    )
    
    result = handler(MockArgs(add_input))
    assert result.success
    assert len(result.segment_ids) == 2
    print("✅ Backward compatibility maintained\n")
    
    # Test 3: Empty array handling
    print("Test 3: Empty array handling")
    add_input = Input(
        draft_id=draft_id,
        video_infos=[]
    )
    
    result = handler(MockArgs(add_input))
    assert not result.success, "Should fail with empty array"
    assert "不能为空" in result.message
    print(f"✅ Empty array handled correctly: {result.message}\n")
    
    # Test 4: Error handling - invalid JSON in array
    print("Test 4: Error handling - invalid JSON in array")
    invalid_array = [
        "not a json string",
        '{"video_url":"https://example.com/video.mp4","start":0,"end":5000}'
    ]
    
    add_input = Input(
        draft_id=draft_id,
        video_infos=invalid_array
    )
    
    result = handler(MockArgs(add_input))
    assert not result.success, "Should fail with invalid JSON"
    print(f"✅ Invalid JSON error handling works: {result.message}\n")
    
    print("✅ All array of strings tests passed!\n")
    return True


def test_video_specific_parameters():
    """Test video-specific parameters (material_range, speed, reverse)"""
    print("=== Testing video-specific parameters ===\n")
    
    # Create a draft
    create_input = CreateInput(
        draft_name="测试视频特定参数",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}\n")
    
    # Test with material_range, speed, and reverse
    video_infos = [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "material_start": 2000,
            "material_end": 7000,
            "speed": 1.5,
            "reverse": True,
            "filter_type": "暖冬",
            "background_blur": True
        }
    ]
    
    add_input = Input(
        draft_id=draft_id,
        video_infos=video_infos
    )
    
    result = handler(MockArgs(add_input))
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 1
    
    # Verify draft config contains all parameters
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    segment = draft_config["tracks"][0]["segments"][0]
    
    # Check material_range
    assert segment["material_range"] is not None
    assert segment["material_range"]["start"] == 2000
    assert segment["material_range"]["end"] == 7000
    
    # Check speed control
    assert segment["speed"]["speed"] == 1.5
    assert segment["speed"]["reverse"] is True
    
    # Check effects
    assert segment["effects"]["filter_type"] == "暖冬"
    
    # Check background
    assert segment["background"]["blur"] is True
    
    print("✅ All video-specific parameters correctly saved\n")
    print("✅ Video-specific parameter tests passed!\n")
    return True


def test_integration_make_video_info_to_add_videos():
    """Test integration: make_video_info → add_videos"""
    print("=== Testing integration: make_video_info → add_videos ===\n")
    
    from coze_plugin.tools.make_video_info.handler import handler as make_video_info_handler
    from coze_plugin.tools.make_video_info.handler import Input as MakeVideoInput
    
    # Create a draft
    create_input = CreateInput(
        draft_name="集成测试草稿",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success
    draft_id = create_result.draft_id
    print(f"Created test draft: {draft_id}\n")
    
    # Step 1: Generate video info strings with make_video_info
    print("Step 1: Generate video info strings with make_video_info")
    video1_input = MakeVideoInput(
        video_url="https://example.com/video1.mp4",
        start=0,
        end=5000,
        scale_x=1.2,
        speed=1.5
    )
    video1_result = make_video_info_handler(MockArgs(video1_input))
    assert video1_result.success
    print(f"  Video 1: {video1_result.video_info_string}")
    
    video2_input = MakeVideoInput(
        video_url="https://example.com/video2.mp4",
        start=5000,
        end=10000,
        material_start=2000,
        material_end=7000,
        filter_type="暖冬",
        filter_intensity=0.8
    )
    video2_result = make_video_info_handler(MockArgs(video2_input))
    assert video2_result.success
    print(f"  Video 2: {video2_result.video_info_string}\n")
    
    # Step 2: Collect strings into array
    print("Step 2: Collect strings into array")
    video_infos_array = [
        video1_result.video_info_string,
        video2_result.video_info_string
    ]
    print(f"  Array length: {len(video_infos_array)}\n")
    
    # Step 3: Pass array of strings to add_videos
    print("Step 3: Pass array of strings to add_videos")
    add_input = Input(
        draft_id=draft_id,
        video_infos=video_infos_array
    )
    
    result = handler(MockArgs(add_input))
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 2
    
    print(f"✅ Successfully added {len(result.segment_ids)} videos")
    print(f"  Segment IDs: {result.segment_ids}")
    print(f"  Segment infos: {json.dumps(result.segment_infos, indent=2, ensure_ascii=False)}\n")
    
    # Verify all parameters were preserved
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    segments = draft_config["tracks"][0]["segments"]
    
    # Verify video 1 parameters
    assert segments[0]["transform"]["scale_x"] == 1.2
    assert segments[0]["speed"]["speed"] == 1.5
    
    # Verify video 2 parameters
    assert segments[1]["material_range"]["start"] == 2000
    assert segments[1]["material_range"]["end"] == 7000
    assert segments[1]["effects"]["filter_type"] == "暖冬"
    assert segments[1]["effects"]["filter_intensity"] == 0.8
    
    print("✅ All parameters correctly preserved through the workflow\n")
    print("✅ Integration test passed!\n")
    return True


def test_error_handling():
    """Test error handling for various invalid inputs"""
    print("=== Testing error handling ===\n")
    
    # Test 1: Invalid draft_id
    print("Test 1: Invalid draft_id")
    add_input = Input(
        draft_id="invalid-uuid",
        video_infos=[{"video_url": "https://example.com/video.mp4", "start": 0, "end": 5000}]
    )
    result = handler(MockArgs(add_input))
    assert not result.success
    assert "无效的 draft_id 格式" in result.message
    print(f"✅ Invalid draft_id handled: {result.message}\n")
    
    # Test 2: Non-existent draft
    print("Test 2: Non-existent draft")
    add_input = Input(
        draft_id=str(uuid.uuid4()),
        video_infos=[{"video_url": "https://example.com/video.mp4", "start": 0, "end": 5000}]
    )
    result = handler(MockArgs(add_input))
    assert not result.success
    assert "not found" in result.message or "找不到" in result.message or "加载草稿配置失败" in result.message
    print(f"✅ Non-existent draft handled: {result.message}\n")
    
    # Test 3: Missing required field in video_info
    print("Test 3: Missing required field in video_info")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="错误测试",
        width=1920,
        height=1080,
        fps=30
    )))
    draft_id = create_result.draft_id
    
    add_input = Input(
        draft_id=draft_id,
        video_infos=[{"video_url": "https://example.com/video.mp4", "start": 0}]  # Missing 'end'
    )
    result = handler(MockArgs(add_input))
    assert not result.success
    assert "end" in result.message
    print(f"✅ Missing field handled: {result.message}\n")
    
    print("✅ All error handling tests passed!\n")
    return True


if __name__ == "__main__":
    print("Starting add_videos tests...\n")
    
    results = []
    results.append(test_add_videos_basic())
    results.append(test_array_of_strings())
    results.append(test_video_specific_parameters())
    results.append(test_integration_make_video_info_to_add_videos())
    results.append(test_error_handling())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
