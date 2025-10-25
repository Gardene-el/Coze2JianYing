#!/usr/bin/env python3
"""
Test for make_image_info tool and array of strings support in add_images

Tests the new functionality:
1. make_image_info tool generates correct JSON strings
2. add_images accepts array of strings (数组字符串)
3. Integration: make_image_info → array → add_images
"""

import os
import json
import uuid
import shutil
import sys

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def test_make_image_info_basic():
    """Test basic make_image_info functionality"""
    print("=== Testing make_image_info basic functionality ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from coze_plugin.tools.make_image_info.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Minimal required parameters
    print("\nTest 1: Minimal parameters")
    input_data = Input(
        image_url="https://example.com/image.jpg",
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    assert result["image_info_string"], "Should return a string"
    
    # Parse and verify the output
    parsed = json.loads(result["image_info_string"])
    assert parsed["image_url"] == "https://example.com/image.jpg"
    assert parsed["start"] == 0
    assert parsed["end"] == 3000
    print(f"✅ Output: {result["image_info_string"]}")
    
    # Test 2: With optional parameters
    print("\nTest 2: With optional parameters")
    input_data = Input(
        image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
        start=0,
        end=3936000,
        in_animation="轻微放大",
        in_animation_duration=100000,
        filter_type="暖冬",
        filter_intensity=0.8,
        scale_x=1.2
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"], f"Should succeed: {result["message"]}"
    parsed = json.loads(result["image_info_string"])
    assert parsed["in_animation"] == "轻微放大"
    assert parsed["filter_type"] == "暖冬"
    assert parsed["scale_x"] == 1.2
    print(f"✅ Output with optional params: {result["image_info_string"][:100]}...")
    
    # Test 3: Default values should not be included
    print("\nTest 3: Default values not included")
    input_data = Input(
        image_url="https://example.com/image.jpg",
        start=0,
        end=3000,
        scale_x=1.0,  # Default value
        scale_y=1.0,  # Default value
        opacity=1.0   # Default value
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["image_info_string"])
    assert "scale_x" not in parsed, "Default scale_x should not be included"
    assert "scale_y" not in parsed, "Default scale_y should not be included"
    assert "opacity" not in parsed, "Default opacity should not be included"
    print("✅ Default values correctly excluded")
    
    # Test 4: Error handling - missing required field
    print("\nTest 4: Error handling - missing image_url")
    input_data = Input(
        image_url="",  # Empty
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with empty image_url"
    assert "image_url" in result["message"]
    print(f"✅ Error handling works: {result["message"]}")
    
    # Test 5: Error handling - invalid time range
    print("\nTest 5: Error handling - invalid time range")
    input_data = Input(
        image_url="https://example.com/image.jpg",
        start=3000,
        end=1000  # end < start
    )
    result = handler(MockArgs(input_data))
    
    assert not result["success"], "Should fail with end < start"
    print(f"✅ Time range validation works: {result["message"]}")
    
    print("\n✅ All make_image_info basic tests passed!")
    return True


def test_add_images_array_of_strings():
    """Test that add_images can accept array of strings"""
    print("\n=== Testing add_images with array of strings ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from coze_plugin.tools.add_images.handler import parse_image_infos
    
    # Test 1: Array of JSON strings
    print("\nTest 1: Array of JSON strings")
    array_of_strings = [
        '{"image_url":"https://example.com/image1.jpg","start":0,"end":3000,"width":1920,"height":1080}',
        '{"image_url":"https://example.com/image2.jpg","start":3000,"end":6000,"in_animation":"轻微放大"}'
    ]
    
    result = parse_image_infos(array_of_strings)
    
    assert len(result) == 2, f"Expected 2 items, got {len(result)}"
    assert result[0]["image_url"] == "https://example.com/image1.jpg"
    assert result[0]["width"] == 1920
    assert result[0]["material_url"] == "https://example.com/image1.jpg"  # Should be mapped
    assert result[1]["image_url"] == "https://example.com/image2.jpg"
    assert result[1]["in_animation"] == "轻微放大"
    print("✅ Array of strings parsed correctly")
    
    # Test 2: Mixed with array of objects (should still work)
    print("\nTest 2: Backward compatibility - array of objects")
    array_of_objects = [
        {"image_url": "https://example.com/image1.jpg", "start": 0, "end": 3000},
        {"image_url": "https://example.com/image2.jpg", "start": 3000, "end": 6000}
    ]
    
    result = parse_image_infos(array_of_objects)
    
    assert len(result) == 2
    assert result[0]["image_url"] == "https://example.com/image1.jpg"
    print("✅ Backward compatibility maintained")
    
    # Test 3: Empty array
    print("\nTest 3: Empty array handling")
    result = parse_image_infos([])
    assert len(result) == 0, "Empty array should return empty list"
    print("✅ Empty array handled correctly")
    
    # Test 4: Invalid JSON in array string
    print("\nTest 4: Error handling - invalid JSON in array")
    try:
        parse_image_infos(['not a valid json'])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid JSON" in str(e)
        print(f"✅ Invalid JSON error handling works: {str(e)}")
    
    print("\n✅ All add_images array of strings tests passed!")
    return True


def test_integration_make_image_info_to_add_images():
    """Test full integration: make_image_info → array → add_images"""
    print("\n=== Testing integration: make_image_info → add_images ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from coze_plugin.tools.make_image_info.handler import handler as make_handler, Input as MakeInput
    from coze_plugin.tools.add_images.handler import handler as add_handler, Input as AddInput
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create a test draft first
    draft_id = str(uuid.uuid4())
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    # Create minimal draft config
    draft_config = {
        "project_name": "test_integration",
        "resolution": {"width": 1920, "height": 1080},
        "frame_rate": 30,
        "tracks": [],
        "last_modified": 1234567890.0
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(draft_config, f)
    
    print(f"Created test draft: {draft_id}")
    
    # Step 1: Create image info strings using make_image_info
    print("\nStep 1: Generate image info strings with make_image_info")
    
    image1_result = make_handler(MockArgs(MakeInput(
        image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
        start=0,
        end=3936000,
        in_animation="轻微放大",
        scale_x=1.2
    )))
    assert image1_result["success"]
    print(f"  Image 1: {image1_result["image_info_string"]}")
    
    image2_result = make_handler(MockArgs(MakeInput(
        image_url="https://example.com/image2.jpg",
        start=3936000,
        end=7872000,
        filter_type="暖冬",
        filter_intensity=0.8
    )))
    assert image2_result["success"]
    print(f"  Image 2: {image2_result["image_info_string"]}")
    
    # Step 2: Collect strings into array
    print("\nStep 2: Collect strings into array")
    image_infos_array = [
        image1_result["image_info_string"],
        image2_result["image_info_string"]
    ]
    print(f"  Array length: {len(image_infos_array)}")
    
    # Step 3: Pass array to add_images
    print("\nStep 3: Pass array of strings to add_images")
    add_result = add_handler(MockArgs(AddInput(
        draft_id=draft_id,
        image_infos=image_infos_array
    )))
    
    assert add_result.success, f"add_images should succeed: {add_result.message}"
    assert len(add_result.segment_ids) == 2, f"Should have 2 segments, got {len(add_result.segment_ids)}"
    assert len(add_result.segment_infos) == 2
    
    print(f"✅ Successfully added {len(add_result.segment_ids)} images")
    print(f"  Segment IDs: {add_result.segment_ids}")
    print(f"  Segment infos: {json.dumps(add_result.segment_infos, indent=2)}")
    
    # Verify the draft was updated correctly
    with open(config_file, 'r', encoding='utf-8') as f:
        updated_config = json.load(f)
    
    assert len(updated_config["tracks"]) == 1, "Should have 1 track"
    # Images are placed on video tracks (no separate image track type)
    assert updated_config["tracks"][0]["track_type"] == "video"
    assert len(updated_config["tracks"][0]["segments"]) == 2, "Should have 2 segments"
    # Images don't have volume parameter (static content has no audio)
    assert "volume" not in updated_config["tracks"][0], "Images should not have volume parameter"
    
    # Verify segment details
    segment1 = updated_config["tracks"][0]["segments"][0]
    assert segment1["material_url"] == "https://s.coze.cn/t/W9CvmtJHJWI/"
    assert segment1["animations"]["intro"] == "轻微放大"
    
    segment2 = updated_config["tracks"][0]["segments"][1]
    assert segment2["material_url"] == "https://example.com/image2.jpg"
    assert segment2["effects"]["filter_type"] == "暖冬"
    
    print("✅ Draft updated correctly with all parameters")
    
    # Cleanup
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
    
    print("\n✅ Full integration test passed!")
    return True


def test_chinese_characters():
    """Test that Chinese characters work correctly"""
    print("\n=== Testing Chinese character support ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from coze_plugin.tools.make_image_info.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test with Chinese animation names
    input_data = Input(
        image_url="https://example.com/image.jpg",
        start=0,
        end=3000,
        in_animation="轻微放大",
        filter_type="暖冬"
    )
    result = handler(MockArgs(input_data))
    
    assert result["success"]
    parsed = json.loads(result["image_info_string"])
    assert parsed["in_animation"] == "轻微放大"
    assert parsed["filter_type"] == "暖冬"
    
    print(f"✅ Chinese characters preserved: {result["image_info_string"]}")
    return True


if __name__ == "__main__":
    print("Starting make_image_info and array string support tests...")
    
    results = []
    results.append(test_make_image_info_basic())
    results.append(test_add_images_array_of_strings())
    results.append(test_integration_make_image_info_to_add_images())
    results.append(test_chinese_characters())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)
