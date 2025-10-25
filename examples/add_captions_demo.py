#!/usr/bin/env python3
"""
add_captions Tool Usage Examples

This file demonstrates complete workflows for the add_captions tool,
showing how to add text/subtitle tracks to a video draft.
"""

import sys
import json
import os
import shutil

# Mock the runtime module for standalone testing
import types
from typing import Generic, TypeVar

T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

# Now we can import the handlers
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
from coze_plugin.tools.create_draft.handler import handler as create_handler
from coze_plugin.tools.create_draft.handler import Input as CreateInput
from coze_plugin.tools.make_caption_info.handler import handler as make_caption_handler
from coze_plugin.tools.make_caption_info.handler import Input as MakeCaptionInput
from coze_plugin.tools.add_captions.handler import handler as add_captions_handler
from coze_plugin.tools.add_captions.handler import Input as AddCaptionsInput
from coze_plugin.tools.export_drafts.handler import handler as export_handler
from coze_plugin.tools.export_drafts.handler import Input as ExportInput


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


def example_1_simple_captions():
    """Example 1: Add simple captions using array format"""
    print_section("Example 1: Simple Captions (Array Format)")
    
    # Step 1: Create a draft
    print("Step 1: Creating draft...")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Simple Caption Demo",
        width=1920,
        height=1080,
        fps=30
    )))
    
    if not create_result["success"]:
        print(f"❌ Failed to create draft: {create_result["message"]}")
        return
    
    draft_id = create_result["draft_id"]
    print(f"✅ Draft created: {draft_id}")
    
    # Step 2: Add captions using array format
    print("\nStep 2: Adding captions using array format...")
    add_result = add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[
            {
                "content": "欢迎观看本视频",
                "start": 0,
                "end": 3000
            },
            {
                "content": "精彩内容马上开始",
                "start": 3000,
                "end": 6000
            },
            {
                "content": "感谢观看",
                "start": 6000,
                "end": 9000
            }
        ]
    )))
    
    if not add_result.success:
        print(f"❌ Failed to add captions: {add_result.message}")
        return
    
    print(f"✅ Added {len(add_result.segment_ids)} captions")
    print(f"   Segment IDs: {add_result.segment_ids}")
    
    # Step 3: Export and display
    print("\nStep 3: Exporting draft configuration...")
    export_result = export_handler(MockArgs(ExportInput(
        draft_ids=draft_id
    )))
    
    if export_result["success"]:
        export_data = json.loads(export_result["draft_data"])
        draft_data = export_data['drafts'][0]  # Get first draft
        print(f"✅ Draft exported successfully")
        print(f"   Tracks: {len(draft_data['tracks'])}")
        print(f"   Caption track segments: {len(draft_data['tracks'][0]['segments'])}")
    
    # Cleanup
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"\n🧹 Cleaned up test draft")


def example_2_styled_captions():
    """Example 2: Add styled captions with custom formatting"""
    print_section("Example 2: Styled Captions (Custom Formatting)")
    
    # Step 1: Create a draft
    print("Step 1: Creating draft...")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Styled Caption Demo",
        width=1920,
        height=1080,
        fps=30
    )))
    draft_id = create_result["draft_id"]
    print(f"✅ Draft created: {draft_id}")
    
    # Step 2: Add styled captions
    print("\nStep 2: Adding styled captions...")
    add_result = add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[
            {
                "content": "视频标题",
                "start": 0,
                "end": 3000,
                "position_y": 0.3,
                "font_size": 72,
                "font_weight": "bold",
                "color": "#FFD700",
                "stroke_enabled": True,
                "stroke_width": 4
            },
            {
                "content": "重要提示",
                "start": 3000,
                "end": 6000,
                "font_size": 56,
                "color": "#FF0000",
                "background_enabled": True,
                "background_color": "#000000",
                "background_opacity": 0.8
            }
        ]
    )))
    
    print(f"✅ Added {len(add_result.segment_ids)} styled captions")
    
    # Cleanup
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"🧹 Cleaned up test draft")


def example_3_dynamic_captions():
    """Example 3: Use make_caption_info for dynamic caption generation"""
    print_section("Example 3: Dynamic Captions (make_caption_info)")
    
    # Step 1: Create a draft
    print("Step 1: Creating draft...")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Dynamic Caption Demo",
        width=1920,
        height=1080,
        fps=30
    )))
    draft_id = create_result["draft_id"]
    print(f"✅ Draft created: {draft_id}")
    
    # Step 2: Generate caption strings dynamically
    print("\nStep 2: Generating caption strings with make_caption_info...")
    
    caption_strings = []
    
    # Opening caption
    result1 = make_caption_handler(MockArgs(MakeCaptionInput(
        content="欢迎观看",
        start=0,
        end=2000,
        intro_animation="淡入"
    )))
    caption_strings.append(result1["caption_info_string"])
    print(f"   Caption 1: {result1["caption_info_string"][:60]}...")
    
    # Title caption
    result2 = make_caption_handler(MockArgs(MakeCaptionInput(
        content="精彩内容展示",
        start=2000,
        end=5000,
        position_y=0.3,
        font_size=72,
        font_weight="bold"
    )))
    caption_strings.append(result2["caption_info_string"])
    print(f"   Caption 2: {result2["caption_info_string"][:60]}...")
    
    # Regular captions
    for i in range(3):
        result = make_caption_handler(MockArgs(MakeCaptionInput(
            content=f"内容段落 {i+1}",
            start=5000 + i * 3000,
            end=8000 + i * 3000
        )))
        caption_strings.append(result["caption_info_string"])
        print(f"   Caption {i+3}: {result["caption_info_string"][:60]}...")
    
    # Closing caption
    result_end = make_caption_handler(MockArgs(MakeCaptionInput(
        content="感谢观看",
        start=14000,
        end=16000,
        outro_animation="淡出"
    )))
    caption_strings.append(result_end["caption_info_string"])
    print(f"   Caption 6: {result_end["caption_info_string"][:60]}...")
    
    # Step 3: Add all captions at once
    print(f"\nStep 3: Adding {len(caption_strings)} captions to draft...")
    add_result = add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=caption_strings
    )))
    
    print(f"✅ Added {len(add_result.segment_ids)} captions dynamically")
    
    # Cleanup
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"🧹 Cleaned up test draft")


def example_4_multilayer_captions():
    """Example 4: Add multiple caption tracks (e.g., for bilingual subtitles)"""
    print_section("Example 4: Multi-Layer Captions (Bilingual)")
    
    # Step 1: Create a draft
    print("Step 1: Creating draft...")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Bilingual Caption Demo",
        width=1920,
        height=1080,
        fps=30
    )))
    draft_id = create_result["draft_id"]
    print(f"✅ Draft created: {draft_id}")
    
    # Step 2: Add Chinese captions (bottom)
    print("\nStep 2: Adding Chinese captions (bottom)...")
    add_result1 = add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[
            {
                "content": "这是中文字幕",
                "start": 0,
                "end": 3000,
                "position_y": 0.9  # Bottom
            },
            {
                "content": "第二句中文",
                "start": 3000,
                "end": 6000,
                "position_y": 0.9
            }
        ]
    )))
    print(f"✅ Added {len(add_result1.segment_ids)} Chinese captions")
    
    # Step 3: Add English captions (top)
    print("\nStep 3: Adding English captions (top)...")
    add_result2 = add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[
            {
                "content": "This is English subtitle",
                "start": 0,
                "end": 3000,
                "position_y": 0.1,  # Top
                "font_size": 40
            },
            {
                "content": "Second English line",
                "start": 3000,
                "end": 6000,
                "position_y": 0.1,
                "font_size": 40
            }
        ]
    )))
    print(f"✅ Added {len(add_result2.segment_ids)} English captions")
    
    # Step 4: Verify
    print("\nStep 4: Verifying draft structure...")
    export_result = export_handler(MockArgs(ExportInput(draft_ids=draft_id)))
    export_data = json.loads(export_result["draft_data"])
    draft_data = export_data['drafts'][0]  # Get first draft
    print(f"✅ Total tracks: {len(draft_data['tracks'])}")
    print(f"   Track 1 (Chinese): {len(draft_data['tracks'][0]['segments'])} segments")
    print(f"   Track 2 (English): {len(draft_data['tracks'][1]['segments'])} segments")
    
    # Cleanup
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"\n🧹 Cleaned up test draft")


def example_5_complete_workflow():
    """Example 5: Complete workflow with all features"""
    print_section("Example 5: Complete Workflow (All Features)")
    
    # Step 1: Create draft
    print("Step 1: Creating draft...")
    create_result = create_handler(MockArgs(CreateInput(
        draft_name="Complete Caption Demo",
        width=1920,
        height=1080,
        fps=30
    )))
    draft_id = create_result["draft_id"]
    print(f"✅ Draft created: {draft_id}")
    
    # Step 2: Add opening caption
    print("\nStep 2: Adding opening caption...")
    opening = make_caption_handler(MockArgs(MakeCaptionInput(
        content="欢迎观看",
        start=0,
        end=2000,
        position_y=0.5,
        font_size=72,
        intro_animation="淡入"
    )))
    
    add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[opening["caption_info_string"]]
    )))
    print(f"✅ Added opening caption")
    
    # Step 3: Add title caption
    print("\nStep 3: Adding title caption...")
    title = make_caption_handler(MockArgs(MakeCaptionInput(
        content="精彩视频标题",
        start=2000,
        end=5000,
        position_y=0.3,
        font_family="思源黑体",
        font_size=80,
        font_weight="bold",
        color="#FFD700",
        stroke_enabled=True,
        stroke_width=4
    )))
    
    add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[title["caption_info_string"]]
    )))
    print(f"✅ Added title caption")
    
    # Step 4: Add content captions
    print("\nStep 4: Adding content captions...")
    content_captions = []
    for i in range(3):
        caption = make_caption_handler(MockArgs(MakeCaptionInput(
            content=f"内容段落 {i+1}：这是详细的说明文字",
            start=5000 + i * 4000,
            end=9000 + i * 4000,
            shadow_enabled=True,
            shadow_blur=6
        )))
        content_captions.append(caption["caption_info_string"])
    
    add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=content_captions
    )))
    print(f"✅ Added {len(content_captions)} content captions")
    
    # Step 5: Add closing caption
    print("\nStep 5: Adding closing caption...")
    closing = make_caption_handler(MockArgs(MakeCaptionInput(
        content="感谢观看，请点赞关注",
        start=17000,
        end=20000,
        position_y=0.5,
        font_size=60,
        color="#FF0000",
        background_enabled=True,
        background_opacity=0.7,
        outro_animation="淡出"
    )))
    
    add_captions_handler(MockArgs(AddCaptionsInput(
        draft_id=draft_id,
        caption_infos=[closing["caption_info_string"]]
    )))
    print(f"✅ Added closing caption")
    
    # Step 6: Export and display
    print("\nStep 6: Exporting final draft...")
    export_result = export_handler(MockArgs(ExportInput(draft_ids=draft_id)))
    
    if export_result["success"]:
        export_data = json.loads(export_result["draft_data"])
        draft_data = export_data['drafts'][0]  # Get first draft
        print(f"✅ Draft exported successfully")
        print(f"   Total tracks: {len(draft_data['tracks'])}")
        total_segments = sum(len(track['segments']) for track in draft_data['tracks'])
        print(f"   Total caption segments: {total_segments}")
        print(f"\n   Track breakdown:")
        for i, track in enumerate(draft_data['tracks'], 1):
            print(f"     Track {i}: {len(track['segments'])} segments")
    
    # Cleanup
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"\n🧹 Cleaned up test draft")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  ADD_CAPTIONS TOOL - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_simple_captions()
        example_2_styled_captions()
        example_3_dynamic_captions()
        example_4_multilayer_captions()
        example_5_complete_workflow()
        
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
