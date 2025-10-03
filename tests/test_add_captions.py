#!/usr/bin/env python3
"""
Test for add_captions tool

Tests the caption addition functionality:
1. add_captions tool creates text tracks correctly
2. Multiple input formats are supported
3. Integration with make_caption_info works correctly
"""

import os
import json
import uuid
import shutil
import sys

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def setup_test_environment():
    """Set up test environment with a draft"""
    # Create test draft directory
    draft_id = str(uuid.uuid4())
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    # Create basic draft config
    draft_config = {
        "draft_id": draft_id,
        "project": {
            "name": "Test Caption Project",
            "width": 1920,
            "height": 1080,
            "fps": 30,
        },
        "media_resources": [],
        "tracks": [],
        "total_duration_ms": 0,
        "created_timestamp": 1234567890.0,
        "last_modified": 1234567890.0
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(draft_config, f, ensure_ascii=False, indent=2)
    
    return draft_id


def cleanup_test_environment(draft_id):
    """Clean up test environment"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)


def test_add_captions_basic():
    """Test basic add_captions functionality"""
    print("=== Testing add_captions basic functionality ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_captions.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Set up test environment
    draft_id = setup_test_environment()
    
    try:
        # Test 1: Add single caption with array format
        print("\nTest 1: Add single caption (array format)")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[{
                "content": "Hello World",
                "start": 0,
                "end": 5000,
                "font_size": 48,
                "color": "#FFFFFF"
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"Failed: {result.message}"
        assert len(result.segment_ids) == 1
        print(f"✅ Added 1 caption: {result.segment_ids[0]}")
        
        # Test 2: Add multiple captions
        print("\nTest 2: Add multiple captions")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[
                {"content": "Caption 1", "start": 0, "end": 3000},
                {"content": "Caption 2", "start": 3000, "end": 6000},
                {"content": "Caption 3", "start": 6000, "end": 9000}
            ]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        assert len(result.segment_ids) == 3
        print(f"✅ Added 3 captions: {len(result.segment_ids)} segments")
        
        # Test 3: Caption with styling
        print("\nTest 3: Caption with styling")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[{
                "content": "Styled Caption",
                "start": 0,
                "end": 5000,
                "font_size": 60,
                "font_weight": "bold",
                "color": "#FF0000",
                "stroke_enabled": True,
                "stroke_color": "#000000",
                "stroke_width": 3
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        print(f"✅ Added styled caption")
        
        # Test 4: Caption with shadow
        print("\nTest 4: Caption with shadow")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[{
                "content": "Shadow Caption",
                "start": 0,
                "end": 5000,
                "shadow_enabled": True,
                "shadow_color": "#000000",
                "shadow_offset_x": 2,
                "shadow_offset_y": 2,
                "shadow_blur": 4
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        print(f"✅ Added caption with shadow")
        
        # Test 5: Caption with background
        print("\nTest 5: Caption with background")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[{
                "content": "Background Caption",
                "start": 0,
                "end": 5000,
                "background_enabled": True,
                "background_opacity": 0.7
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        print(f"✅ Added caption with background")
        
        print("\n✅ All basic functionality tests passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


def test_add_captions_array_string_format():
    """Test add_captions with array string format (from make_caption_info)"""
    print("\n=== Testing add_captions with array string format ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_captions.handler import handler, Input
    from tools.make_caption_info.handler import handler as make_handler
    from tools.make_caption_info.handler import Input as MakeInput
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    draft_id = setup_test_environment()
    
    try:
        # Test 1: Using make_caption_info output
        print("\nTest 1: Array string format from make_caption_info")
        
        # Generate caption info strings using make_caption_info
        caption1 = make_handler(MockArgs(MakeInput(
            content="First caption",
            start=0,
            end=3000,
            font_size=48
        )))
        
        caption2 = make_handler(MockArgs(MakeInput(
            content="Second caption",
            start=3000,
            end=6000,
            font_size=48,
            color="#FF0000"
        )))
        
        assert caption1.success and caption2.success
        
        # Use the generated strings in add_captions
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[caption1.caption_info_string, caption2.caption_info_string]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"Failed: {result.message}"
        assert len(result.segment_ids) == 2
        print(f"✅ Array string format: added {len(result.segment_ids)} captions")
        
        # Test 2: JSON string format
        print("\nTest 2: JSON string format")
        json_string = json.dumps([
            {"content": "JSON Caption 1", "start": 0, "end": 3000},
            {"content": "JSON Caption 2", "start": 3000, "end": 6000}
        ])
        
        input_data = Input(
            draft_id=draft_id,
            caption_infos=json_string
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        assert len(result.segment_ids) == 2
        print(f"✅ JSON string format: added {len(result.segment_ids)} captions")
        
        print("\n✅ All array string format tests passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


def test_add_captions_validation():
    """Test add_captions validation"""
    print("\n=== Testing add_captions validation ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_captions.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    draft_id = setup_test_environment()
    
    try:
        # Test 1: Missing required field (content)
        print("\nTest 1: Missing content field")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[{
                "start": 0,
                "end": 5000
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert not result.success
        assert "content" in result.message.lower()
        print(f"✅ Correctly rejected: {result.message}")
        
        # Test 2: Invalid time range (should be caught by make_caption_info, not add_captions)
        print("\nTest 2: Invalid draft_id")
        input_data = Input(
            draft_id="invalid-uuid",
            caption_infos=[{
                "content": "Test",
                "start": 0,
                "end": 5000
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert not result.success
        print(f"✅ Correctly rejected invalid draft_id")
        
        # Test 3: Empty caption_infos
        print("\nTest 3: Empty caption_infos")
        input_data = Input(
            draft_id=draft_id,
            caption_infos=[]
        )
        result = handler(MockArgs(input_data))
        
        # Should fail with appropriate error message
        assert not result.success
        assert "空" in result.message
        print(f"✅ Empty array correctly rejected: {result.message}")
        
        print("\n✅ All validation tests passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


if __name__ == "__main__":
    print("Starting add_captions tests...")
    
    results = []
    
    try:
        results.append(test_add_captions_basic())
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        results.append(False)
    
    try:
        results.append(test_add_captions_array_string_format())
    except Exception as e:
        print(f"❌ Array string format test failed: {e}")
        results.append(False)
    
    try:
        results.append(test_add_captions_validation())
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
