#!/usr/bin/env python3
"""
Make Video Info Demo

Demonstrates the usage of make_video_info tool to generate video configuration strings.
Shows various parameter combinations and the complete workflow with add_videos.
"""

import sys
import types
from typing import Generic, TypeVar

# Setup mock runtime for demo
T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

# Now import the handlers
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')
from coze_plugin.tools.make_video_info.handler import handler as make_video_info_handler
from coze_plugin.tools.make_video_info.handler import Input as MakeVideoInput


class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def demo_basic_usage():
    """Demonstrate basic make_video_info usage"""
    print("=== Demo 1: Basic Usage ===\n")
    
    # Minimal parameters
    print("1. Minimal parameters:")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")
    
    # With some optional parameters
    print("2. With optional parameters:")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        scale_x=1.2,
        scale_y=1.2,
        filter_type="暖冬"
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")


def demo_video_specific_features():
    """Demonstrate video-specific features"""
    print("=== Demo 2: Video-Specific Features ===\n")
    
    # Material range (trimming)
    print("1. Material range (trimming source video):")
    print("   Use case: Extract 5 seconds from a 30-second video")
    input_data = MakeVideoInput(
        video_url="https://example.com/30s_video.mp4",
        start=0,
        end=5000,
        material_start=10000,  # Start from 10s in source
        material_end=15000     # End at 15s in source
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")
    
    # Speed control
    print("2. Speed control:")
    print("   Use case: Fast forward at 2x speed")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        speed=2.0
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")
    
    # Slow motion
    print("3. Slow motion:")
    print("   Use case: Slow motion at 0.5x speed")
    input_data = MakeVideoInput(
        video_url="https://example.com/action.mp4",
        start=0,
        end=10000,
        speed=0.5
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")
    
    # Reverse playback
    print("4. Reverse playback:")
    print("   Use case: Play video backwards")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        reverse=True
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")
    
    # Combined: slow motion + reverse
    print("5. Combined features: slow motion + reverse:")
    print("   Use case: Slow motion reverse playback")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=10000,
        speed=0.5,
        reverse=True
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Result: {result["video_info_string"]}\n")


def demo_complete_configuration():
    """Demonstrate complete video configuration"""
    print("=== Demo 3: Complete Video Configuration ===\n")
    
    print("Use case: Video with all common parameters")
    input_data = MakeVideoInput(
        video_url="https://example.com/complete_video.mp4",
        start=0,
        end=10000,
        material_start=5000,
        material_end=15000,
        position_x=0.1,
        position_y=-0.1,
        scale_x=1.2,
        scale_y=1.2,
        rotation=5.0,
        opacity=0.9,
        speed=1.5,
        filter_type="暖冬",
        filter_intensity=0.8,
        transition_type="淡入淡出",
        transition_duration=1000,
        background_blur=True
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"Result: {result["video_info_string"]}\n")


def demo_workflow_with_add_videos():
    """Demonstrate complete workflow with add_videos"""
    print("=== Demo 4: Complete Workflow (make_video_info → add_videos) ===\n")
    
    from coze_plugin.tools.create_draft.handler import handler as create_handler
    from coze_plugin.tools.create_draft.handler import Input as CreateInput
    from coze_plugin.tools.add_videos.handler import handler as add_videos_handler
    from coze_plugin.tools.add_videos.handler import Input as AddVideosInput
    
    # Step 1: Create a draft
    print("Step 1: Create a draft")
    create_input = CreateInput(
        draft_name="视频工作流演示",
        width=1920,
        height=1080,
        fps=30
    )
    create_result = create_handler(MockArgs(create_input))
    if not create_result["success"]:
        print(f"   Failed to create draft: {create_result["message"]}")
        return
    
    draft_id = create_result["draft_id"]
    print(f"   Created draft: {draft_id}\n")
    
    # Step 2: Generate video info strings
    print("Step 2: Generate video info strings using make_video_info")
    
    # Video 1: Opening scene with fast forward
    video1_input = MakeVideoInput(
        video_url="https://example.com/opening.mp4",
        start=0,
        end=3000,
        speed=1.5,
        filter_type="暖冬"
    )
    video1_result = make_video_info_handler(MockArgs(video1_input))
    print(f"   Video 1: {video1_result["video_info_string"]}")
    
    # Video 2: Main content with material trimming
    video2_input = MakeVideoInput(
        video_url="https://example.com/main_content.mp4",
        start=3000,
        end=13000,
        material_start=5000,
        material_end=15000
    )
    video2_result = make_video_info_handler(MockArgs(video2_input))
    print(f"   Video 2: {video2_result["video_info_string"]}")
    
    # Video 3: Slow motion highlight
    video3_input = MakeVideoInput(
        video_url="https://example.com/highlight.mp4",
        start=13000,
        end=18000,
        speed=0.5,
        scale_x=1.2,
        scale_y=1.2
    )
    video3_result = make_video_info_handler(MockArgs(video3_input))
    print(f"   Video 3: {video3_result["video_info_string"]}\n")
    
    # Step 3: Collect into array
    print("Step 3: Collect video info strings into array")
    video_infos_array = [
        video1_result["video_info_string"],
        video2_result["video_info_string"],
        video3_result["video_info_string"]
    ]
    print(f"   Array contains {len(video_infos_array)} video configs\n")
    
    # Step 4: Add videos to draft
    print("Step 4: Add videos to draft using add_videos")
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos_array
    )
    add_result = add_videos_handler(MockArgs(add_input))
    
    if add_result.success:
        print(f"   ✅ Successfully added {len(add_result.segment_ids)} videos")
        print(f"   Segment IDs: {add_result.segment_ids}")
        print(f"   Total timeline duration: 18 seconds\n")
    else:
        print(f"   ❌ Failed: {add_result.message}\n")


def demo_error_handling():
    """Demonstrate error handling"""
    print("=== Demo 5: Error Handling ===\n")
    
    # Missing required field
    print("1. Missing required field (end):")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=None  # Missing
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")
    
    # Invalid time range
    print("2. Invalid time range (end <= start):")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=5000,
        end=1000
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")
    
    # Material range without both parameters
    print("3. Material range without both parameters:")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        material_start=1000
        # material_end missing
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")
    
    # Invalid speed
    print("4. Invalid speed (> 2.0):")
    input_data = MakeVideoInput(
        video_url="https://example.com/video.mp4",
        start=0,
        end=5000,
        speed=3.0
    )
    result = make_video_info_handler(MockArgs(input_data))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")


def demo_comparison_with_images():
    """Demonstrate differences between video and image tools"""
    print("=== Demo 6: Video vs Image Tool Comparison ===\n")
    
    print("Video-specific features (not available for images):")
    print("  ✓ material_range: Trim source video")
    print("  ✓ speed: Playback speed control (0.5x - 2.0x)")
    print("  ✓ reverse: Reverse playback\n")
    
    print("Image-specific features (not available for videos):")
    print("  ✓ in_animation/outro_animation: Entry/exit animations")
    print("  ✓ fit_mode: Aspect ratio fitting mode\n")
    
    print("Shared features:")
    print("  ✓ Transform: position_x, position_y, scale_x, scale_y, rotation, opacity")
    print("  ✓ Crop: crop_enabled, crop_left, crop_top, crop_right, crop_bottom")
    print("  ✓ Effects: filter_type, filter_intensity, transition_type, transition_duration")
    print("  ✓ Background: background_blur, background_color\n")


if __name__ == "__main__":
    print("Make Video Info Tool Demo\n")
    print("=" * 80)
    print()
    
    demo_basic_usage()
    demo_video_specific_features()
    demo_complete_configuration()
    demo_workflow_with_add_videos()
    demo_error_handling()
    demo_comparison_with_images()
    
    print("=" * 80)
    print("\nDemo completed! ✅")
