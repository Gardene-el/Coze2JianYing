#!/usr/bin/env python3
"""
Test script for the add_images tool logic without runtime dependencies

Tests the core validation and processing logic for the new format
"""

import json
import uuid
import sys


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_image_infos_format(image_infos_str: str) -> tuple[bool, str]:
    """Test the validation logic for image_infos parameter"""
    
    if not image_infos_str:
        return False, "image_infos is required"
    
    if not isinstance(image_infos_str, str):
        return False, "image_infos must be a JSON string"
    
    # Parse JSON
    try:
        image_infos = json.loads(image_infos_str)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in image_infos: {str(e)}"
    
    if not isinstance(image_infos, list) or len(image_infos) == 0:
        return False, "image_infos must contain a non-empty array"
    
    # Validate each image info object
    for i, image_info in enumerate(image_infos):
        if not isinstance(image_info, dict):
            return False, f"Image info at index {i} must be an object"
        
        # Required fields
        if "image_url" not in image_info:
            return False, f"Image info at index {i} must have 'image_url' field"
        
        if not isinstance(image_info["image_url"], str) or not image_info["image_url"].strip():
            return False, f"Image info at index {i}: image_url must be a non-empty string"
        
        if "start" not in image_info:
            return False, f"Image info at index {i} must have 'start' field"
        
        if not isinstance(image_info["start"], int) or image_info["start"] < 0:
            return False, f"Image info at index {i}: start must be a non-negative integer"
        
        if "end" not in image_info:
            return False, f"Image info at index {i} must have 'end' field"
        
        if not isinstance(image_info["end"], int) or image_info["end"] <= image_info["start"]:
            return False, f"Image info at index {i}: end must be greater than start"
        
        # Optional fields validation
        if "width" in image_info and (not isinstance(image_info["width"], int) or image_info["width"] <= 0):
            return False, f"Image info at index {i}: width must be a positive integer"
        
        if "height" in image_info and (not isinstance(image_info["height"], int) or image_info["height"] <= 0):
            return False, f"Image info at index {i}: height must be a positive integer"
        
        if "in_animation_duration" in image_info and (not isinstance(image_info["in_animation_duration"], int) or image_info["in_animation_duration"] < 0):
            return False, f"Image info at index {i}: in_animation_duration must be a non-negative integer"
    
    return True, ""


def create_segments_from_infos(image_infos_str: str) -> tuple[list, list, list]:
    """Create segments from image infos (test implementation)"""
    image_infos = json.loads(image_infos_str)
    
    segments = []
    segment_ids = []
    segment_infos = []
    
    for i, image_info in enumerate(image_infos):
        # Generate unique segment ID
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Extract parameters
        image_url = image_info["image_url"]
        start_time = image_info["start"]
        end_time = image_info["end"]
        duration = end_time - start_time
        
        # Optional parameters
        width = image_info.get("width")
        height = image_info.get("height")
        in_animation = image_info.get("in_animation")
        in_animation_duration = image_info.get("in_animation_duration", 0)
        
        # Create segment info for output
        segment_info = {
            "id": segment_id,
            "start": start_time,
            "end": end_time
        }
        segment_infos.append(segment_info)
        
        # Create segment data
        segment = {
            "type": "video",
            "material_url": image_url,
            "segment_id": segment_id,
            "time_range": {
                "start": start_time,
                "end": end_time
            },
            "material_range": {
                "start": 0,
                "end": duration
            },
            "image_properties": {
                "width": width,
                "height": height,
                "in_animation": in_animation,
                "in_animation_duration": in_animation_duration
            }
        }
        segments.append(segment)
    
    return segments, segment_ids, segment_infos


def test_user_example_format():
    """Test with the exact format from user's comment"""
    print("=== Testing user's expected format ===")
    
    # User's input format
    draft_id = "d5eaa880-ae11-441c-ae7e-1872d95d108f"
    image_infos_str = '[{"image_url":"https://s.coze.cn/t/W9CvmtJHJWI/","start":0,"end":3936000,"width":1440,"height":1080},{"image_url":"https://s.coze.cn/t/iGLRGx6JvZ0/","start":3936000,"end":7176000,"width":1440,"height":1080,"in_animation":"轻微放大","in_animation_duration":100000},{"image_url":"https://s.coze.cn/t/amCMhpjzEC8/","start":7176000,"end":11688000,"width":1440,"height":1080}]'
    
    try:
        # Test validation
        is_valid, error_msg = validate_image_infos_format(image_infos_str)
        assert is_valid, f"Validation should pass: {error_msg}"
        print("✅ Input validation passed")
        
        # Test processing
        segments, segment_ids, segment_infos = create_segments_from_infos(image_infos_str)
        
        # Verify output format
        assert len(segment_ids) == 3, "Should generate 3 segment IDs"
        assert len(segment_infos) == 3, "Should create 3 segment infos"
        
        # Check segment IDs are valid UUIDs
        for seg_id in segment_ids:
            try:
                uuid.UUID(seg_id)
            except ValueError:
                raise AssertionError(f"Invalid UUID: {seg_id}")
        
        # Verify segment infos format matches expected output
        expected_keys = {"id", "start", "end"}
        for seg_info in segment_infos:
            assert set(seg_info.keys()) == expected_keys
            assert seg_info["end"] > seg_info["start"]
        
        # Check specific values
        assert segment_infos[0]["start"] == 0
        assert segment_infos[0]["end"] == 3936000
        assert segment_infos[1]["start"] == 3936000
        assert segment_infos[1]["end"] == 7176000
        
        # Verify segments contain image properties
        assert segments[0]["image_properties"]["width"] == 1440
        assert segments[0]["image_properties"]["height"] == 1080
        assert segments[1]["image_properties"]["in_animation"] == "轻微放大"
        assert segments[1]["image_properties"]["in_animation_duration"] == 100000
        
        print("✅ Processing logic passed")
        print(f"Generated segment IDs: {segment_ids}")
        print(f"First segment info: {segment_infos[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ User format test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_cases():
    """Test various validation scenarios"""
    print("\n=== Testing validation cases ===")
    
    try:
        # Test valid case
        valid_data = '[{"image_url":"https://example.com/test.jpg","start":0,"end":3000}]'
        is_valid, error_msg = validate_image_infos_format(valid_data)
        assert is_valid, f"Valid data should pass: {error_msg}"
        
        # Test invalid JSON
        is_valid, error_msg = validate_image_infos_format("invalid json")
        assert not is_valid, "Invalid JSON should fail"
        
        # Test empty array
        is_valid, error_msg = validate_image_infos_format("[]")
        assert not is_valid, "Empty array should fail"
        
        # Test missing required field
        invalid_data = '[{"image_url":"https://example.com/test.jpg","start":0}]'  # Missing end
        is_valid, error_msg = validate_image_infos_format(invalid_data)
        assert not is_valid, "Missing required field should fail"
        
        # Test invalid time range
        invalid_data = '[{"image_url":"https://example.com/test.jpg","start":5000,"end":3000}]'
        is_valid, error_msg = validate_image_infos_format(invalid_data)
        assert not is_valid, "Invalid time range should fail"
        
        print("✅ All validation cases passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation cases test failed: {str(e)}")
        return False


def test_expected_output_format():
    """Test that output matches the expected format from user's comment"""
    print("\n=== Testing expected output format ===")
    
    try:
        # Use a simple example
        image_infos_str = '[{"image_url":"https://example.com/test1.jpg","start":0,"end":3000},{"image_url":"https://example.com/test2.jpg","start":3000,"end":6000}]'
        
        segments, segment_ids, segment_infos = create_segments_from_infos(image_infos_str)
        
        # Create output structure matching user's expected format
        output = {
            "segment_ids": segment_ids,
            "segment_infos": segment_infos
        }
        
        # Verify structure
        assert "segment_ids" in output
        assert "segment_infos" in output
        assert isinstance(output["segment_ids"], list)
        assert isinstance(output["segment_infos"], list)
        assert len(output["segment_ids"]) == len(output["segment_infos"])
        
        # Check each segment_info has required fields
        for seg_info in output["segment_infos"]:
            assert "id" in seg_info
            assert "start" in seg_info
            assert "end" in seg_info
            assert seg_info["id"] in output["segment_ids"]
        
        print("✅ Output format matches expected structure")
        print("Example output:")
        print(json.dumps(output, indent=2)[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ Output format test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing add_images tool logic (new format)")
    print("=" * 50)
    
    results = []
    results.append(test_user_example_format())
    results.append(test_validation_cases())
    results.append(test_expected_output_format())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All add_images logic tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)