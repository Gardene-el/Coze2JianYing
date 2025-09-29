#!/usr/bin/env python3
"""
Test script for the updated add_images tool with new input/output format

Tests the new JSON-based image_infos input and segment_ids/segment_infos output
"""

import os
import sys
import json
import shutil
import uuid
import time
from typing import NamedTuple


def setup_test_draft():
    """Create a test draft for testing purposes"""
    draft_id = str(uuid.uuid4())
    
    # Create draft folder
    base_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
    draft_folder = os.path.join(base_dir, draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    # Create initial draft config
    config = {
        "draft_id": draft_id,
        "project": {
            "name": "测试项目",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_quality": "1080p",
            "audio_quality": "320k",
            "background_color": "#000000"
        },
        "media_resources": [],
        "tracks": [],
        "total_duration_ms": 0,
        "created_timestamp": time.time(),
        "last_modified": time.time(),
        "status": "created"
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return draft_id


def test_add_images_new_format():
    """Test the add_images tool with new input/output format"""
    print("=== Testing add_images tool with new format ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the new handler logic directly
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images')
        
        # Import functions directly to test logic
        from handler import validate_input_parameters, parse_image_infos, create_image_segments
        
        # Create test input in new format
        class TestInput(NamedTuple):
            draft_id: str
            image_infos: str
        
        # Test image infos matching the user's expected format
        image_infos_data = [
            {
                "image_url": "https://s.coze.cn/t/W9CvmtJHJWI/",
                "start": 0,
                "end": 3936000,
                "width": 1440,
                "height": 1080
            },
            {
                "image_url": "https://s.coze.cn/t/iGLRGx6JvZ0/",
                "start": 3936000,
                "end": 7176000,
                "width": 1440,
                "height": 1080,
                "in_animation": "轻微放大",
                "in_animation_duration": 100000
            },
            {
                "image_url": "https://s.coze.cn/t/amCMhpjzEC8/",
                "start": 7176000,
                "end": 11688000,
                "width": 1440,
                "height": 1080
            }
        ]
        
        test_input = TestInput(
            draft_id=draft_id,
            image_infos=json.dumps(image_infos_data)
        )
        
        # Test validation
        print("Testing input validation...")
        is_valid, error_msg = validate_input_parameters(test_input)
        assert is_valid, f"Validation should pass: {error_msg}"
        print("✅ Input validation passed")
        
        # Test parsing
        print("Testing JSON parsing...")
        parsed_infos = parse_image_infos(test_input.image_infos)
        assert len(parsed_infos) == 3, "Should parse 3 image infos"
        assert parsed_infos[0]["image_url"] == "https://s.coze.cn/t/W9CvmtJHJWI/", "First URL should match"
        assert parsed_infos[1]["in_animation"] == "轻微放大", "Animation should be preserved"
        print("✅ JSON parsing passed")
        
        # Test segment creation
        print("Testing segment creation...")
        segments, segment_ids, segment_infos = create_image_segments(test_input)
        
        assert len(segments) == 3, "Should create 3 segments"
        assert len(segment_ids) == 3, "Should generate 3 segment IDs"
        assert len(segment_infos) == 3, "Should create 3 segment infos"
        
        # Verify segment IDs are valid UUIDs
        for seg_id in segment_ids:
            try:
                uuid.UUID(seg_id)
            except ValueError:
                raise AssertionError(f"Invalid UUID format: {seg_id}")
        
        # Verify segment infos format
        expected_segment_info_keys = {"id", "start", "end"}
        for seg_info in segment_infos:
            assert set(seg_info.keys()) == expected_segment_info_keys, f"Segment info should have {expected_segment_info_keys}"
            assert seg_info["end"] > seg_info["start"], "End time should be greater than start time"
        
        # Verify segment data
        first_segment = segments[0]
        assert first_segment["type"] == "video", "Images should be treated as video segments"
        assert first_segment["material_url"] == "https://s.coze.cn/t/W9CvmtJHJWI/", "URL should match"
        assert first_segment["time_range"]["start"] == 0, "Start time should match"
        assert first_segment["time_range"]["end"] == 3936000, "End time should match"
        assert "image_properties" in first_segment, "Should have image_properties"
        assert first_segment["image_properties"]["width"] == 1440, "Width should be preserved"
        
        # Verify second segment with animation
        second_segment = segments[1]
        assert second_segment["image_properties"]["in_animation"] == "轻微放大", "Animation should be preserved"
        assert second_segment["image_properties"]["in_animation_duration"] == 100000, "Animation duration should be preserved"
        
        print("✅ Segment creation passed")
        
        # Test output format
        print("Testing expected output format...")
        
        # Check that we can create the expected output format
        output_data = {
            "segment_ids": segment_ids,
            "segment_infos": segment_infos
        }
        
        # Verify it matches the expected structure from the comment
        assert isinstance(output_data["segment_ids"], list), "segment_ids should be a list"
        assert isinstance(output_data["segment_infos"], list), "segment_infos should be a list"
        assert len(output_data["segment_ids"]) == len(output_data["segment_infos"]), "Lists should have same length"
        
        print("✅ Output format matches expected structure")
        print(f"Generated {len(segment_ids)} segments with IDs: {segment_ids[:2]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ add_images new format test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 0 in sys.path:
            sys.path.remove('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images')


def test_validation_edge_cases():
    """Test validation with various edge cases"""
    print("\n=== Testing validation edge cases ===")
    
    try:
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images')
        from handler import validate_input_parameters
        
        class TestInput(NamedTuple):
            draft_id: str
            image_infos: str
        
        # Test invalid JSON
        test_input = TestInput(draft_id=str(uuid.uuid4()), image_infos="invalid json")
        is_valid, error_msg = validate_input_parameters(test_input)
        assert not is_valid, "Should fail with invalid JSON"
        print("✅ Invalid JSON properly rejected")
        
        # Test empty array
        test_input = TestInput(draft_id=str(uuid.uuid4()), image_infos="[]")
        is_valid, error_msg = validate_input_parameters(test_input)
        assert not is_valid, "Should fail with empty array"
        print("✅ Empty array properly rejected")
        
        # Test missing required fields
        invalid_data = [{"image_url": "https://example.com/test.jpg"}]  # Missing start/end
        test_input = TestInput(draft_id=str(uuid.uuid4()), image_infos=json.dumps(invalid_data))
        is_valid, error_msg = validate_input_parameters(test_input)
        assert not is_valid, "Should fail with missing required fields"
        print("✅ Missing required fields properly rejected")
        
        # Test invalid time range
        invalid_data = [{"image_url": "https://example.com/test.jpg", "start": 5000, "end": 3000}]  # end < start
        test_input = TestInput(draft_id=str(uuid.uuid4()), image_infos=json.dumps(invalid_data))
        is_valid, error_msg = validate_input_parameters(test_input)
        assert not is_valid, "Should fail with end < start"
        print("✅ Invalid time range properly rejected")
        
        print("✅ All validation edge cases passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation edge cases test failed: {str(e)}")
        return False
    finally:
        if '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images' in sys.path:
            sys.path.remove('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images')


def cleanup_test_files():
    """Clean up test files"""
    test_path = "/tmp/jianying_assistant"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
        print("Cleaned up test files")


if __name__ == "__main__":
    print("Starting add_images tool new format tests...")
    
    results = []
    results.append(test_add_images_new_format())
    results.append(test_validation_edge_cases())
    
    cleanup_test_files()
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All add_images new format tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)