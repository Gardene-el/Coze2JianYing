#!/usr/bin/env python3
"""
Test for make_caption_info tool and array of strings support in add_captions

Tests the new functionality:
1. make_caption_info tool generates correct JSON strings
2. add_captions accepts array of strings (数组字符串)
3. Integration: make_caption_info → array → add_captions
"""

import os
import json
import uuid
import shutil
import sys

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def test_make_caption_info_basic():
    """Test basic make_caption_info functionality"""
    print("=== Testing make_caption_info basic functionality ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_caption_info.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Minimal required parameters
    print("\nTest 1: Minimal parameters")
    input_data = Input(
        content="这是一句字幕",
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    
    assert result.success, f"Should succeed: {result.message}"
    assert result.caption_info_string, "Should return a string"
    
    # Parse and verify the output
    parsed = json.loads(result.caption_info_string)
    assert parsed["content"] == "这是一句字幕"
    assert parsed["start"] == 0
    assert parsed["end"] == 3000
    print(f"✅ Output: {result.caption_info_string}")
    
    # Test 2: With text style parameters
    print("\nTest 2: With text style parameters")
    input_data = Input(
        content="自定义样式字幕",
        start=0,
        end=5000,
        font_family="思源黑体",
        font_size=60,
        font_weight="bold",
        color="#FFD700",
        stroke_enabled=True,
        stroke_color="#000000",
        stroke_width=3
    )
    result = handler(MockArgs(input_data))
    
    assert result.success, f"Should succeed: {result.message}"
    parsed = json.loads(result.caption_info_string)
    assert parsed["font_family"] == "思源黑体"
    assert parsed["font_size"] == 60
    assert parsed["font_weight"] == "bold"
    assert parsed["color"] == "#FFD700"
    assert parsed["stroke_enabled"] == True
    assert parsed["stroke_width"] == 3
    print(f"✅ Output with text style: {result.caption_info_string[:100]}...")
    
    # Test 3: Default values not included
    print("\nTest 3: Default values not included")
    input_data = Input(
        content="测试默认值",
        start=1000,
        end=4000,
        position_x=0.5,  # default value
        position_y=0.9,  # default value
        font_size=48,    # default value
        color="#FFFFFF"  # default value
    )
    result = handler(MockArgs(input_data))
    parsed = json.loads(result.caption_info_string)
    
    # Default values should not appear in output
    assert "position_x" not in parsed, "Default position_x should not be in output"
    assert "position_y" not in parsed, "Default position_y should not be in output"
    assert "font_size" not in parsed, "Default font_size should not be in output"
    assert "color" not in parsed, "Default color should not be in output"
    print("✅ Default values correctly excluded")
    
    # Test 4: With shadow and background
    print("\nTest 4: With shadow and background")
    input_data = Input(
        content="醒目字幕",
        start=2000,
        end=6000,
        shadow_enabled=True,
        shadow_offset_x=4,
        shadow_offset_y=4,
        shadow_blur=8,
        background_enabled=True,
        background_color="#FF0000",
        background_opacity=0.7
    )
    result = handler(MockArgs(input_data))
    parsed = json.loads(result.caption_info_string)
    assert parsed["shadow_enabled"] == True
    assert parsed["shadow_offset_x"] == 4
    assert parsed["background_enabled"] == True
    assert parsed["background_color"] == "#FF0000"
    print(f"✅ Shadow and background parameters included")
    
    # Test 5: With animations
    print("\nTest 5: With animations")
    input_data = Input(
        content="动画字幕",
        start=0,
        end=5000,
        intro_animation="淡入",
        outro_animation="淡出",
        loop_animation="闪烁"
    )
    result = handler(MockArgs(input_data))
    parsed = json.loads(result.caption_info_string)
    assert parsed["intro_animation"] == "淡入"
    assert parsed["outro_animation"] == "淡出"
    assert parsed["loop_animation"] == "闪烁"
    print(f"✅ Animation parameters included")
    
    # Test 6: Error handling - missing content
    print("\nTest 6: Error handling - missing content")
    input_data = Input(
        content="",
        start=0,
        end=3000
    )
    result = handler(MockArgs(input_data))
    assert not result.success, "Should fail with empty content"
    assert "content" in result.message.lower()
    print(f"✅ Error handling works: {result.message}")
    
    # Test 7: Error handling - invalid time range
    print("\nTest 7: Error handling - invalid time range")
    input_data = Input(
        content="测试",
        start=5000,
        end=3000  # end < start
    )
    result = handler(MockArgs(input_data))
    assert not result.success, "Should fail with invalid time range"
    assert "end" in result.message and "start" in result.message
    print(f"✅ Time range validation works: {result.message}")
    
    # Test 8: Error handling - invalid position
    print("\nTest 8: Error handling - invalid position")
    input_data = Input(
        content="测试",
        start=0,
        end=3000,
        position_x=1.5  # > 1.0
    )
    result = handler(MockArgs(input_data))
    assert not result.success, "Should fail with invalid position"
    assert "position_x" in result.message
    print(f"✅ Position validation works: {result.message}")
    
    # Test 9: Error handling - invalid alignment
    print("\nTest 9: Error handling - invalid alignment")
    input_data = Input(
        content="测试",
        start=0,
        end=3000,
        alignment="invalid"
    )
    result = handler(MockArgs(input_data))
    assert not result.success, "Should fail with invalid alignment"
    assert "alignment" in result.message
    print(f"✅ Alignment validation works: {result.message}")
    
    print("\n✅ All make_caption_info basic tests passed!")
    return True


def test_add_captions_array_strings():
    """Test add_captions with array of strings"""
    print("\n=== Testing add_captions with array of strings ===")
    
    from tools.add_captions.handler import parse_caption_infos
    
    # Test 1: Array of JSON strings
    print("\nTest 1: Array of JSON strings")
    array_of_strings = [
        '{"content":"第一句","start":0,"end":3000}',
        '{"content":"第二句","start":3000,"end":6000,"font_size":56}'
    ]
    
    result = parse_caption_infos(array_of_strings)
    assert len(result) == 2
    assert result[0]["content"] == "第一句"
    assert result[1]["font_size"] == 56
    print("✅ Array of strings parsed correctly")
    
    # Test 2: Backward compatibility - array of objects
    print("\nTest 2: Backward compatibility - array of objects")
    array_of_objects = [
        {"content": "第一句", "start": 0, "end": 3000},
        {"content": "第二句", "start": 3000, "end": 6000}
    ]
    
    result = parse_caption_infos(array_of_objects)
    assert len(result) == 2
    assert result[0]["content"] == "第一句"
    print("✅ Backward compatibility maintained")
    
    # Test 3: JSON string format
    print("\nTest 3: JSON string format")
    json_string = '[{"content":"测试","start":0,"end":3000}]'
    
    result = parse_caption_infos(json_string)
    assert len(result) == 1
    assert result[0]["content"] == "测试"
    print("✅ JSON string format works")
    
    # Test 4: Empty array handling
    print("\nTest 4: Empty array handling")
    result = parse_caption_infos([])
    assert len(result) == 0
    print("✅ Empty array handled correctly")
    
    # Test 5: Error handling - invalid JSON in array
    print("\nTest 5: Error handling - invalid JSON in array")
    try:
        parse_caption_infos(["not valid json"])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid JSON" in str(e)
        print(f"✅ Invalid JSON error handling works: {str(e)[:50]}...")
    
    # Test 6: Error handling - missing required field
    print("\nTest 6: Error handling - missing required field")
    try:
        parse_caption_infos([{"content": "测试", "start": 0}])  # missing 'end'
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Missing required field" in str(e)
        print(f"✅ Missing field error handling works: {str(e)[:50]}...")
    
    print("\n✅ All add_captions array of strings tests passed!")
    return True


def test_integration_make_and_add():
    """Test integration: make_caption_info → add_captions"""
    print("\n=== Testing integration: make_caption_info → add_captions ===")
    
    from tools.create_draft.handler import handler as create_handler
    from tools.create_draft.handler import Input as CreateInput
    from tools.make_caption_info.handler import handler as make_handler
    from tools.make_caption_info.handler import Input as MakeInput
    from tools.add_captions.handler import handler as add_handler
    from tools.add_captions.handler import Input as AddInput
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create a test draft
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Caption Test Project",
        width=1920,
        height=1080,
        fps=30
    )))
    
    assert create_result.success, "Draft creation should succeed"
    draft_id = create_result.draft_id
    print(f"Created test draft: {draft_id}")
    
    # Step 1: Generate caption info strings with make_caption_info
    print("\nStep 1: Generate caption info strings with make_caption_info")
    
    caption1_result = make_handler(MockArgs(MakeInput(
        content="欢迎观看本视频",
        start=0,
        end=3000
    )))
    assert caption1_result.success
    print(f"  Caption 1: {caption1_result.caption_info_string}")
    
    caption2_result = make_handler(MockArgs(MakeInput(
        content="精彩内容马上开始",
        start=3000,
        end=6000,
        font_size=60,
        color="#FFD700",
        stroke_enabled=True
    )))
    assert caption2_result.success
    print(f"  Caption 2: {caption2_result.caption_info_string}")
    
    caption3_result = make_handler(MockArgs(MakeInput(
        content="感谢观看",
        start=6000,
        end=9000,
        intro_animation="淡入",
        outro_animation="淡出"
    )))
    assert caption3_result.success
    print(f"  Caption 3: {caption3_result.caption_info_string}")
    
    # Step 2: Collect strings into array
    print("\nStep 2: Collect strings into array")
    caption_infos_array = [
        caption1_result.caption_info_string,
        caption2_result.caption_info_string,
        caption3_result.caption_info_string
    ]
    print(f"  Array length: {len(caption_infos_array)}")
    
    # Step 3: Pass array of strings to add_captions
    print("\nStep 3: Pass array of strings to add_captions")
    add_result = add_handler(MockArgs(AddInput(
        draft_id=draft_id,
        caption_infos=caption_infos_array
    )))
    
    assert add_result.success, f"Should succeed: {add_result.message}"
    print(f"✅ Successfully added {len(add_result.segment_ids)} captions")
    print(f"  Segment IDs: {add_result.segment_ids}")
    print(f"  Segment infos: {json.dumps(add_result.segment_infos, ensure_ascii=False, indent=2)}")
    
    # Step 4: Verify draft configuration
    print("\nStep 4: Verify draft configuration")
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    assert "tracks" in draft_config, "Draft should have tracks"
    assert len(draft_config["tracks"]) == 1, "Should have 1 text track"
    
    text_track = draft_config["tracks"][0]
    assert text_track["track_type"] == "text", "Track type should be text"
    assert len(text_track["segments"]) == 3, "Should have 3 text segments"
    
    # Verify segment content
    seg1 = text_track["segments"][0]
    assert seg1["content"] == "欢迎观看本视频"
    assert seg1["time_range"]["start"] == 0
    assert seg1["time_range"]["end"] == 3000
    print(f"  ✅ Segment 1 verified: {seg1['content']}")
    
    seg2 = text_track["segments"][1]
    assert seg2["content"] == "精彩内容马上开始"
    assert seg2["style"]["font_size"] == 60
    assert seg2["style"]["color"] == "#FFD700"
    assert seg2["style"]["stroke"]["enabled"] == True
    print(f"  ✅ Segment 2 verified: {seg2['content']}")
    
    seg3 = text_track["segments"][2]
    assert seg3["content"] == "感谢观看"
    assert seg3["animations"]["intro"] == "淡入"
    assert seg3["animations"]["outro"] == "淡出"
    print(f"  ✅ Segment 3 verified: {seg3['content']}")
    
    # Clean up
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"\nCleaned up test draft folder: {draft_folder}")
    
    print("\n✅ All integration tests passed!")
    return True


def test_chinese_characters():
    """Test Chinese character support"""
    print("\n=== Testing Chinese character support ===")
    
    from tools.make_caption_info.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test with various Chinese characters
    print("\nTest 1: Chinese content")
    input_data = Input(
        content="这是一段中文字幕，包含各种字符：！@#￥%",
        start=0,
        end=5000,
        font_family="思源黑体",
        intro_animation="淡入"
    )
    result = handler(MockArgs(input_data))
    
    assert result.success
    parsed = json.loads(result.caption_info_string)
    assert parsed["content"] == "这是一段中文字幕，包含各种字符：！@#￥%"
    assert parsed["font_family"] == "思源黑体"
    assert parsed["intro_animation"] == "淡入"
    print(f"✅ Chinese characters handled correctly")
    print(f"  Output: {result.caption_info_string[:80]}...")
    
    print("\n✅ All Chinese character tests passed!")
    return True


if __name__ == "__main__":
    try:
        print("Starting make_caption_info and array string support tests...")
        
        # Test make_caption_info basic functionality
        test_make_caption_info_basic()
        
        # Test add_captions with array of strings
        test_add_captions_array_strings()
        
        # Test integration
        test_integration_make_and_add()
        
        # Test Chinese character support
        test_chinese_characters()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
