#!/usr/bin/env python3
"""
Test the add_images tool functionality

Tests the complete workflow of adding image segments to existing drafts,
including input validation, image info parsing, and output format verification.
"""

import os
import json
import uuid
import shutil
import tempfile


def test_add_images_basic():
    """Test basic add_images functionality"""
    print("=== Testing add_images basic functionality ===")
    
    # Import the add_images handler with mock runtime
    import sys
    sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_images.handler import handler, Input, parse_image_infos
    from tools.create_draft.handler import handler as create_handler, Input as CreateInput
    
    # Create a mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Step 1: Create a draft first
    create_input = CreateInput(
        draft_name="测试图片草稿",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success, f"Failed to create draft: {create_result.message}"
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}")
    
    # Step 2: Prepare image infos
    image_infos = [
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
        }
    ]
    
    image_infos_str = json.dumps(image_infos)
    
    # Step 3: Test add_images
    add_input = Input(
        draft_id=draft_id,
        image_infos=image_infos_str
    )
    
    result = handler(MockArgs(add_input))
    
    # Verify result
    assert result.success, f"add_images failed: {result.message}"
    assert len(result.segment_ids) == 2, f"Expected 2 segments, got {len(result.segment_ids)}"
    assert len(result.segment_infos) == 2, f"Expected 2 segment_infos, got {len(result.segment_infos)}"
    
    print(f"✅ Successfully added {len(result.segment_ids)} images")
    print(f"✅ Segment IDs: {result.segment_ids}")
    
    # Step 4: Verify segment_infos format
    for i, info in enumerate(result.segment_infos):
        assert "id" in info, f"segment_infos[{i}] missing 'id' field"
        assert "start" in info, f"segment_infos[{i}] missing 'start' field"
        assert "end" in info, f"segment_infos[{i}] missing 'end' field"
        assert info["start"] == image_infos[i]["start"], f"Start time mismatch for segment {i}"
        assert info["end"] == image_infos[i]["end"], f"End time mismatch for segment {i}"
    
    print("✅ Segment infos format verified")
    
    # Step 5: Verify draft was updated
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        updated_config = json.load(f)
    
    assert "tracks" in updated_config, "No tracks found in updated config"
    assert len(updated_config["tracks"]) == 1, f"Expected 1 track, got {len(updated_config['tracks'])}"
    
    image_track = updated_config["tracks"][0]
    assert image_track["track_type"] == "image", f"Expected image track, got {image_track['track_type']}"
    assert len(image_track["segments"]) == 2, f"Expected 2 segments in track, got {len(image_track['segments'])}"
    
    print("✅ Draft configuration updated correctly")
    
    # Cleanup
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
    
    print("✅ Test passed!")
    return True


def test_add_images_validation():
    """Test input validation for add_images"""
    print("=== Testing add_images input validation ===")
    
    import sys
    sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_images.handler import handler, Input, validate_uuid_format, parse_image_infos
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Invalid UUID
    result = handler(MockArgs(Input(draft_id="invalid-uuid", image_infos="[]")))
    assert not result.success, "Should fail with invalid UUID"
    assert "无效的 draft_id 格式" in result.message, f"Wrong error message: {result.message}"
    print("✅ Invalid UUID validation passed")
    
    # Test 2: Empty draft_id
    result = handler(MockArgs(Input(draft_id="", image_infos="[]")))
    assert not result.success, "Should fail with empty draft_id"
    print("✅ Empty draft_id validation passed")
    
    # Test 3: Invalid JSON
    valid_uuid = str(uuid.uuid4())
    result = handler(MockArgs(Input(draft_id=valid_uuid, image_infos="invalid json")))
    assert not result.success, "Should fail with invalid JSON"
    assert "解析 image_infos 失败" in result.message, f"Wrong error message: {result.message}"
    print("✅ Invalid JSON validation passed")
    
    # Test 4: Empty image_infos
    result = handler(MockArgs(Input(draft_id=valid_uuid, image_infos="[]")))
    assert not result.success, "Should fail with empty image_infos"
    assert "image_infos 不能为空" in result.message, f"Wrong error message: {result.message}"
    print("✅ Empty image_infos validation passed")
    
    # Test 5: Missing required fields
    result = handler(MockArgs(Input(draft_id=valid_uuid, image_infos='[{"image_url": "test"}]')))
    assert not result.success, "Should fail with missing required fields"
    print("✅ Missing required fields validation passed")
    
    # Test 6: Nonexistent draft
    result = handler(MockArgs(Input(draft_id=valid_uuid, image_infos='[{"image_url": "test", "start": 0, "end": 1000}]')))
    assert not result.success, "Should fail with nonexistent draft"
    assert "加载草稿配置失败" in result.message, f"Wrong error message: {result.message}"
    print("✅ Nonexistent draft validation passed")
    
    print("✅ All validation tests passed!")
    return True


def test_parse_image_infos():
    """Test the parse_image_infos function"""
    print("=== Testing parse_image_infos function ===")
    
    import sys
    sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_images.handler import parse_image_infos
    
    # Test 1: Valid input
    valid_json = '[{"image_url": "https://test.com/img.jpg", "start": 0, "end": 1000}]'
    result = parse_image_infos(valid_json)
    assert len(result) == 1, f"Expected 1 item, got {len(result)}"
    assert result[0]["material_url"] == "https://test.com/img.jpg", "material_url not set correctly"
    print("✅ Valid input parsing passed")
    
    # Test 2: Multiple images
    multi_json = '''[
        {"image_url": "https://test1.com/img1.jpg", "start": 0, "end": 1000},
        {"image_url": "https://test2.com/img2.jpg", "start": 1000, "end": 2000, "width": 1920, "height": 1080}
    ]'''
    result = parse_image_infos(multi_json)
    assert len(result) == 2, f"Expected 2 items, got {len(result)}"
    assert result[1]["width"] == 1920, "Additional parameters not preserved"
    print("✅ Multiple images parsing passed")
    
    # Test 3: Invalid JSON
    try:
        parse_image_infos("invalid json")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid JSON format" in str(e), f"Wrong error message: {str(e)}"
    print("✅ Invalid JSON error handling passed")
    
    # Test 4: Non-list input
    try:
        parse_image_infos('{"not": "a list"}')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "list" in str(e).lower(), f"Wrong error message: {str(e)}"
    print("✅ Non-list input error handling passed")
    
    print("✅ All parse_image_infos tests passed!")
    return True


def test_add_images_multiple_calls():
    """Test multiple calls to add_images creating separate tracks"""
    print("=== Testing multiple add_images calls ===")
    
    import sys
    sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_images.handler import handler, Input
    from tools.create_draft.handler import handler as create_handler, Input as CreateInput
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create a draft
    create_input = CreateInput(draft_name="多轨道测试")
    create_result = create_handler(MockArgs(create_input))
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}")
    
    # First call - add 2 images
    image_infos_1 = json.dumps([
        {"image_url": "https://test1.com/img1.jpg", "start": 0, "end": 2000},
        {"image_url": "https://test1.com/img2.jpg", "start": 2000, "end": 4000}
    ])
    
    result1 = handler(MockArgs(Input(draft_id=draft_id, image_infos=image_infos_1)))
    assert result1.success, f"First call failed: {result1.message}"
    assert len(result1.segment_ids) == 2, "First call should return 2 segment IDs"
    
    # Second call - add 1 image
    image_infos_2 = json.dumps([
        {"image_url": "https://test2.com/img3.jpg", "start": 4000, "end": 6000}
    ])
    
    result2 = handler(MockArgs(Input(draft_id=draft_id, image_infos=image_infos_2)))
    assert result2.success, f"Second call failed: {result2.message}"
    assert len(result2.segment_ids) == 1, "Second call should return 1 segment ID"
    
    # Verify draft has 2 tracks
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    assert len(config["tracks"]) == 2, f"Expected 2 tracks, got {len(config['tracks'])}"
    assert config["tracks"][0]["track_type"] == "image", "First track should be image type"
    assert config["tracks"][1]["track_type"] == "image", "Second track should be image type"
    assert len(config["tracks"][0]["segments"]) == 2, "First track should have 2 segments"
    assert len(config["tracks"][1]["segments"]) == 1, "Second track should have 1 segment"
    
    print("✅ Multiple calls created separate tracks correctly")
    
    # Cleanup
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
    
    print("✅ Test passed!")
    return True


if __name__ == "__main__":
    print("Starting add_images tool tests...")
    
    results = []
    results.append(test_parse_image_infos())
    results.append(test_add_images_validation())
    results.append(test_add_images_basic())
    results.append(test_add_images_multiple_calls())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
        exit(1)