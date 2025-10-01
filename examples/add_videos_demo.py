#!/usr/bin/env python3
"""
Add Videos Tool Demo

Demonstrates the usage of add_videos tool to add video segments to drafts.
Shows various input formats, parameter combinations, and integration scenarios.
"""

import json
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
from tools.add_videos.handler import handler as add_videos_handler
from tools.add_videos.handler import Input as AddVideosInput
from tools.create_draft.handler import handler as create_handler
from tools.create_draft.handler import Input as CreateInput


class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def create_demo_draft(name):
    """Helper function to create a draft for demos"""
    create_input = CreateInput(
        draft_name=name,
        width=1920,
        height=1080,
        fps=30
    )
    result = create_handler(MockArgs(create_input))
    if result.success:
        return result.draft_id
    else:
        raise Exception(f"Failed to create draft: {result.message}")


def demo_basic_usage():
    """Demonstrate basic add_videos usage with different input formats"""
    print("=== Demo 1: Basic Usage with Different Input Formats ===\n")
    
    # Format 1: Array of objects (static configuration)
    print("1. Array of objects format (recommended for static config):")
    draft_id = create_demo_draft("基本演示-数组对象")
    
    video_infos = [
        {
            "video_url": "https://example.com/video1.mp4",
            "start": 0,
            "end": 5000
        },
        {
            "video_url": "https://example.com/video2.mp4",
            "start": 5000,
            "end": 10000
        }
    ]
    
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos
    )
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added {len(result.segment_ids)} videos")
        print(f"   Segment IDs: {result.segment_ids}\n")
    
    # Format 2: JSON string
    print("2. JSON string format:")
    draft_id = create_demo_draft("基本演示-JSON字符串")
    
    video_infos_json = json.dumps([
        {"video_url": "https://example.com/video1.mp4", "start": 0, "end": 5000},
        {"video_url": "https://example.com/video2.mp4", "start": 5000, "end": 10000}
    ])
    
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos_json
    )
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added {len(result.segment_ids)} videos")
        print(f"   Segment IDs: {result.segment_ids}\n")
    
    # Format 3: Array of strings (dynamic configuration)
    print("3. Array of strings format (recommended for dynamic config):")
    draft_id = create_demo_draft("基本演示-数组字符串")
    
    video_infos_array = [
        '{"video_url":"https://example.com/video1.mp4","start":0,"end":5000}',
        '{"video_url":"https://example.com/video2.mp4","start":5000,"end":10000,"speed":1.5}'
    ]
    
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos_array
    )
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added {len(result.segment_ids)} videos")
        print(f"   Segment IDs: {result.segment_ids}\n")


def demo_video_trimming():
    """Demonstrate video trimming using material_range"""
    print("=== Demo 2: Video Trimming with Material Range ===\n")
    
    draft_id = create_demo_draft("视频裁剪演示")
    
    print("Scenario: Extract highlights from a 30-second video")
    print("  - Use 5-10s segment at position 0-5s")
    print("  - Use 20-25s segment at position 5-10s\n")
    
    video_infos = [
        {
            "video_url": "https://example.com/30s_video.mp4",
            "start": 0,
            "end": 5000,
            "material_start": 5000,   # From 5s
            "material_end": 10000     # To 10s
        },
        {
            "video_url": "https://example.com/30s_video.mp4",
            "start": 5000,
            "end": 10000,
            "material_start": 20000,  # From 20s
            "material_end": 25000     # To 25s
        }
    ]
    
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos
    )
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"✅ Created 10-second video from 30-second source")
        print(f"   Timeline: 0-5s and 5-10s")
        print(f"   Source: 5-10s and 20-25s segments\n")


def demo_speed_control():
    """Demonstrate speed control features"""
    print("=== Demo 3: Speed Control ===\n")
    
    # Fast forward
    print("1. Fast forward (2x speed):")
    draft_id = create_demo_draft("快进演示")
    
    video_infos = [
        {
            "video_url": "https://example.com/long_video.mp4",
            "start": 0,
            "end": 5000,
            "speed": 2.0  # 2x speed
        }
    ]
    
    add_input = AddVideosInput(draft_id=draft_id, video_infos=video_infos)
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added video with 2x speed")
        print(f"   A 10-second source plays in 5 seconds\n")
    
    # Slow motion
    print("2. Slow motion (0.5x speed):")
    draft_id = create_demo_draft("慢动作演示")
    
    video_infos = [
        {
            "video_url": "https://example.com/action.mp4",
            "start": 0,
            "end": 10000,
            "speed": 0.5  # 0.5x speed (slow motion)
        }
    ]
    
    add_input = AddVideosInput(draft_id=draft_id, video_infos=video_infos)
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added video with 0.5x speed (slow motion)")
        print(f"   A 5-second source plays in 10 seconds\n")
    
    # Reverse playback
    print("3. Reverse playback:")
    draft_id = create_demo_draft("倒放演示")
    
    video_infos = [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "reverse": True
        }
    ]
    
    add_input = AddVideosInput(draft_id=draft_id, video_infos=video_infos)
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added video with reverse playback\n")
    
    # Combined: slow motion + reverse
    print("4. Combined: slow motion + reverse:")
    draft_id = create_demo_draft("慢动作倒放演示")
    
    video_infos = [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 10000,
            "speed": 0.5,
            "reverse": True
        }
    ]
    
    add_input = AddVideosInput(draft_id=draft_id, video_infos=video_infos)
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"   ✅ Added video with slow motion reverse playback\n")


def demo_picture_in_picture():
    """Demonstrate picture-in-picture effect with multiple video tracks"""
    print("=== Demo 4: Picture-in-Picture Effect ===\n")
    
    draft_id = create_demo_draft("画中画演示")
    
    print("Scenario: Main video + small PiP video in corner")
    
    # Step 1: Add main video (full screen)
    print("\nStep 1: Add main video (full screen)")
    main_video = [
        {
            "video_url": "https://example.com/main_video.mp4",
            "start": 0,
            "end": 10000
        }
    ]
    
    result1 = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=main_video
    )))
    
    if result1.success:
        print(f"   ✅ Added main video track")
    
    # Step 2: Add PiP video (small, positioned in corner)
    print("\nStep 2: Add PiP video (scaled down, positioned in corner)")
    pip_video = [
        {
            "video_url": "https://example.com/pip_video.mp4",
            "start": 2000,
            "end": 8000,
            "scale_x": 0.3,       # 30% size
            "scale_y": 0.3,
            "position_x": 0.6,    # Right side
            "position_y": -0.6,   # Top
            "opacity": 0.9
        }
    ]
    
    result2 = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=pip_video
    )))
    
    if result2.success:
        print(f"   ✅ Added PiP video track")
        print(f"\n✅ Picture-in-picture effect created!")
        print(f"   Main video: 0-10s (full screen)")
        print(f"   PiP video: 2-8s (small, in corner)\n")


def demo_effects_and_filters():
    """Demonstrate effects and filters"""
    print("=== Demo 5: Effects and Filters ===\n")
    
    draft_id = create_demo_draft("效果演示")
    
    video_infos = [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "filter_type": "暖冬",
            "filter_intensity": 0.8,
            "transition_type": "淡入淡出",
            "transition_duration": 1000,
            "background_blur": True
        }
    ]
    
    add_input = AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos
    )
    result = add_videos_handler(MockArgs(add_input))
    
    if result.success:
        print(f"✅ Added video with effects:")
        print(f"   - Filter: 暖冬 (intensity: 0.8)")
        print(f"   - Transition: 淡入淡出 (duration: 1000ms)")
        print(f"   - Background blur: enabled\n")


def demo_complete_workflow():
    """Demonstrate complete workflow with make_video_info"""
    print("=== Demo 6: Complete Workflow (make_video_info → add_videos) ===\n")
    
    from tools.make_video_info.handler import handler as make_video_info_handler
    from tools.make_video_info.handler import Input as MakeVideoInput
    
    draft_id = create_demo_draft("完整工作流演示")
    
    print("Scenario: Create a video montage with 3 segments")
    
    # Step 1: Generate video info strings
    print("\nStep 1: Generate video info strings using make_video_info")
    
    video1 = make_video_info_handler(MockArgs(MakeVideoInput(
        video_url="https://example.com/intro.mp4",
        start=0,
        end=3000,
        speed=1.5,
        filter_type="暖冬"
    )))
    print(f"   Video 1: {video1.video_info_string[:80]}...")
    
    video2 = make_video_info_handler(MockArgs(MakeVideoInput(
        video_url="https://example.com/main.mp4",
        start=3000,
        end=13000,
        material_start=5000,
        material_end=15000
    )))
    print(f"   Video 2: {video2.video_info_string[:80]}...")
    
    video3 = make_video_info_handler(MockArgs(MakeVideoInput(
        video_url="https://example.com/outro.mp4",
        start=13000,
        end=16000,
        speed=0.5,
        reverse=True
    )))
    print(f"   Video 3: {video3.video_info_string[:80]}...")
    
    # Step 2: Collect into array
    print("\nStep 2: Collect into array")
    video_infos_array = [
        video1.video_info_string,
        video2.video_info_string,
        video3.video_info_string
    ]
    print(f"   Array contains {len(video_infos_array)} videos")
    
    # Step 3: Add to draft
    print("\nStep 3: Add videos to draft")
    result = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=video_infos_array
    )))
    
    if result.success:
        print(f"   ✅ Successfully added {len(result.segment_ids)} videos")
        print(f"   Total duration: 16 seconds")
        print(f"   Segment IDs: {result.segment_ids}\n")


def demo_multiple_tracks():
    """Demonstrate creating multiple video tracks"""
    print("=== Demo 7: Multiple Video Tracks ===\n")
    
    draft_id = create_demo_draft("多轨道演示")
    
    print("Creating 3 video tracks with overlapping content")
    
    # Track 1: Background video
    print("\nTrack 1: Background video (0-10s)")
    result1 = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=[{
            "video_url": "https://example.com/background.mp4",
            "start": 0,
            "end": 10000
        }]
    )))
    
    # Track 2: Overlay video 1 (2-6s)
    print("Track 2: Overlay video 1 (2-6s, scaled)")
    result2 = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=[{
            "video_url": "https://example.com/overlay1.mp4",
            "start": 2000,
            "end": 6000,
            "scale_x": 0.5,
            "scale_y": 0.5,
            "position_x": -0.5
        }]
    )))
    
    # Track 3: Overlay video 2 (6-10s)
    print("Track 3: Overlay video 2 (6-10s, scaled)")
    result3 = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=[{
            "video_url": "https://example.com/overlay2.mp4",
            "start": 6000,
            "end": 10000,
            "scale_x": 0.5,
            "scale_y": 0.5,
            "position_x": 0.5
        }]
    )))
    
    if all([result1.success, result2.success, result3.success]):
        print(f"\n✅ Created 3 video tracks with overlapping content")
        print(f"   Track 1: Full screen background")
        print(f"   Track 2: Left overlay (2-6s)")
        print(f"   Track 3: Right overlay (6-10s)\n")


def demo_error_scenarios():
    """Demonstrate error handling"""
    print("=== Demo 8: Error Handling ===\n")
    
    # Invalid draft_id
    print("1. Invalid draft_id:")
    result = add_videos_handler(MockArgs(AddVideosInput(
        draft_id="invalid-uuid",
        video_infos=[{"video_url": "https://example.com/video.mp4", "start": 0, "end": 5000}]
    )))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")
    
    # Empty video_infos
    print("2. Empty video_infos:")
    draft_id = create_demo_draft("错误测试")
    result = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=[]
    )))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")
    
    # Missing required field
    print("3. Missing required field:")
    result = add_videos_handler(MockArgs(AddVideosInput(
        draft_id=draft_id,
        video_infos=[{"video_url": "https://example.com/video.mp4", "start": 0}]
    )))
    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}\n")


if __name__ == "__main__":
    print("Add Videos Tool Demo\n")
    print("=" * 80)
    print()
    
    demo_basic_usage()
    demo_video_trimming()
    demo_speed_control()
    demo_picture_in_picture()
    demo_effects_and_filters()
    demo_complete_workflow()
    demo_multiple_tracks()
    demo_error_scenarios()
    
    print("=" * 80)
    print("\nDemo completed! ✅")
    print("\nKey takeaways:")
    print("  • add_videos supports multiple input formats (arrays, JSON strings)")
    print("  • Video-specific features: material_range, speed, reverse")
    print("  • Multiple tracks can be created for overlays and PiP effects")
    print("  • Works seamlessly with make_video_info for dynamic configuration")
