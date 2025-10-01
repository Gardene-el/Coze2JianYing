#!/usr/bin/env python3
"""
make_caption_info Tool Usage Examples

This file demonstrates various usage scenarios for the make_caption_info tool,
showing how to generate caption configuration strings for different use cases.
"""

import sys
import json
from typing import NamedTuple, Optional

# Mock the runtime module for standalone testing
import types
from typing import Generic, TypeVar

T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

# Now we can import the handler
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
from tools.make_caption_info.handler import handler, Input


class MockArgs:
    """Mock Args class for testing"""
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def example_1_simple_caption():
    """Example 1: Simple basic caption"""
    print_section("Example 1: Simple Basic Caption")
    
    result = handler(MockArgs(Input(
        content="欢迎观看本视频",
        start=0,
        end=3000
    )))
    
    print(f"Success: {result["success"]}")
    print(f"Message: {result["message"]}")
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_2_title_caption():
    """Example 2: Large title caption at top of screen"""
    print_section("Example 2: Title Caption (Top, Large Font)")
    
    result = handler(MockArgs(Input(
        content="精彩视频标题",
        start=0,
        end=3000,
        position_y=0.3,      # Top third of screen
        font_size=72,         # Larger font
        font_weight="bold",   # Bold text
        color="#FFD700"       # Gold color
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_3_styled_caption():
    """Example 3: Styled caption with custom font and stroke"""
    print_section("Example 3: Styled Caption (Custom Font + Stroke)")
    
    result = handler(MockArgs(Input(
        content="醒目字幕",
        start=2000,
        end=6000,
        font_family="思源黑体",
        font_size=60,
        font_weight="bold",
        color="#FFFFFF",
        stroke_enabled=True,
        stroke_color="#000000",
        stroke_width=4
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_4_shadow_caption():
    """Example 4: Caption with shadow for depth"""
    print_section("Example 4: Caption with Shadow")
    
    result = handler(MockArgs(Input(
        content="带阴影的字幕",
        start=1000,
        end=5000,
        shadow_enabled=True,
        shadow_color="#000000",
        shadow_offset_x=4,
        shadow_offset_y=4,
        shadow_blur=8
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_5_background_caption():
    """Example 5: Caption with background for readability"""
    print_section("Example 5: Caption with Background")
    
    result = handler(MockArgs(Input(
        content="重要提示信息",
        start=3000,
        end=8000,
        background_enabled=True,
        background_color="#FF0000",
        background_opacity=0.8,
        font_size=52
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_6_animated_caption():
    """Example 6: Caption with animations"""
    print_section("Example 6: Animated Caption")
    
    result = handler(MockArgs(Input(
        content="动态字幕效果",
        start=0,
        end=5000,
        intro_animation="淡入",
        outro_animation="淡出",
        font_size=56,
        color="#00FF00"
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_7_fully_styled():
    """Example 7: Fully styled caption with all effects"""
    print_section("Example 7: Fully Styled Caption (All Effects)")
    
    result = handler(MockArgs(Input(
        content="完整样式展示",
        start=2000,
        end=8000,
        position_y=0.5,          # Middle of screen
        font_family="思源黑体",
        font_size=64,
        font_weight="bold",
        color="#FFD700",
        stroke_enabled=True,
        stroke_color="#000000",
        stroke_width=3,
        shadow_enabled=True,
        shadow_color="#000000",
        shadow_offset_x=3,
        shadow_offset_y=3,
        shadow_blur=6,
        background_enabled=True,
        background_color="#000000",
        background_opacity=0.6,
        intro_animation="淡入",
        outro_animation="淡出"
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_8_left_aligned():
    """Example 8: Left-aligned caption"""
    print_section("Example 8: Left-Aligned Caption")
    
    result = handler(MockArgs(Input(
        content="左对齐字幕",
        start=1000,
        end=4000,
        alignment="left",
        position_x=0.1   # Near left edge
    )))
    
    print(f"Caption String: {result["caption_info_string"]}")
    print(f"\nParsed JSON:")
    print(json.dumps(json.loads(result["caption_info_string"]), ensure_ascii=False, indent=2))


def example_9_multiple_captions_workflow():
    """Example 9: Generate multiple captions for a complete workflow"""
    print_section("Example 9: Multiple Captions Workflow")
    
    captions = []
    
    # Opening caption
    result1 = handler(MockArgs(Input(
        content="欢迎观看",
        start=0,
        end=2000,
        intro_animation="淡入"
    )))
    captions.append(result1["caption_info_string"])
    
    # Title caption
    result2 = handler(MockArgs(Input(
        content="精彩视频内容",
        start=2000,
        end=5000,
        position_y=0.3,
        font_size=72,
        font_weight="bold",
        color="#FFD700"
    )))
    captions.append(result2["caption_info_string"])
    
    # Regular captions
    result3 = handler(MockArgs(Input(
        content="第一段内容说明",
        start=5000,
        end=8000
    )))
    captions.append(result3["caption_info_string"])
    
    result4 = handler(MockArgs(Input(
        content="第二段内容说明",
        start=8000,
        end=11000
    )))
    captions.append(result4["caption_info_string"])
    
    # Closing caption
    result5 = handler(MockArgs(Input(
        content="感谢观看",
        start=11000,
        end=13000,
        outro_animation="淡出"
    )))
    captions.append(result5["caption_info_string"])
    
    print(f"Generated {len(captions)} caption strings:")
    for i, caption in enumerate(captions, 1):
        print(f"\n{i}. {caption[:80]}...")
    
    print(f"\n\nReady to be collected into an array and passed to add_captions:")
    print("caption_infos_array = [")
    for caption in captions:
        print(f"    '{caption}',")
    print("]")


def example_10_error_handling():
    """Example 10: Error handling demonstrations"""
    print_section("Example 10: Error Handling")
    
    # Error 1: Empty content
    print("Test 1: Empty content")
    result = handler(MockArgs(Input(
        content="",
        start=0,
        end=3000
    )))
    print(f"  Success: {result["success"]}")
    print(f"  Message: {result["message"]}\n")
    
    # Error 2: Invalid time range
    print("Test 2: Invalid time range (end < start)")
    result = handler(MockArgs(Input(
        content="测试",
        start=5000,
        end=3000
    )))
    print(f"  Success: {result["success"]}")
    print(f"  Message: {result["message"]}\n")
    
    # Error 3: Invalid position
    print("Test 3: Invalid position (> 1.0)")
    result = handler(MockArgs(Input(
        content="测试",
        start=0,
        end=3000,
        position_x=1.5
    )))
    print(f"  Success: {result["success"]}")
    print(f"  Message: {result["message"]}\n")
    
    # Error 4: Invalid alignment
    print("Test 4: Invalid alignment")
    result = handler(MockArgs(Input(
        content="测试",
        start=0,
        end=3000,
        alignment="invalid"
    )))
    print(f"  Success: {result["success"]}")
    print(f"  Message: {result["message"]}\n")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  MAKE_CAPTION_INFO TOOL - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_simple_caption()
        example_2_title_caption()
        example_3_styled_caption()
        example_4_shadow_caption()
        example_5_background_caption()
        example_6_animated_caption()
        example_7_fully_styled()
        example_8_left_aligned()
        example_9_multiple_captions_workflow()
        example_10_error_handling()
        
        print("\n" + "="*70)
        print("  ✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
