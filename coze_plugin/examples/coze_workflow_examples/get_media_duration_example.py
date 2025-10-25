#!/usr/bin/env python3
"""
Example usage of the get_media_duration Coze plugin tool

This example demonstrates how to use the media duration tool in different scenarios
that would be encountered in Coze workflows.

Note: This example shows the expected input/output format and usage patterns.
Actual usage requires the Coze platform runtime environment.
"""

import json


def example_single_video():
    """Example: Processing a single video file"""
    print("=== Example 1: Single Video ===")
    
    input_data = {
        "links": [
            "https://example.com/my-video.mp4"
        ]
    }
    
    print("Input:")
    print(json.dumps(input_data, indent=2))
    
    # For demo, we'll show expected output format
    expected_output = {
        "all_timelines": [{"start": 0, "end": 30000}],  # 30 seconds
        "timelines": [{"start": 0, "end": 30000}]
    }
    
    print("\nExpected Output:")
    print(json.dumps(expected_output, indent=2))
    print(f"Duration: 30.0s")


def example_multiple_videos():
    """Example: Processing multiple video files for a complete timeline"""
    print("\n=== Example 2: Multiple Videos ===")
    
    input_data = {
        "links": [
            "https://example.com/intro.mp4",
            "https://example.com/main-content.mp4", 
            "https://example.com/outro.mp4"
        ]
    }
    
    print("Input:")
    print(json.dumps(input_data, indent=2))
    
    # Mock durations: 5s intro, 120s main, 10s outro
    mock_durations = [5000, 120000, 10000]
    expected_output = {
        "all_timelines": [{"start": 0, "end": 135000}],
        "timelines": [
            {"start": 0, "end": 5000},
            {"start": 5000, "end": 125000},
            {"start": 125000, "end": 135000}
        ]
    }
    
    print("\nExpected Output:")
    print(json.dumps(expected_output, indent=2))
    
    print("\nTimeline Breakdown:")
    media_info = [
        ("Video 1", 5000, "5.0s"),
        ("Video 2", 120000, "2m 0.0s"), 
        ("Video 3", 10000, "10.0s")
    ]
    
    for i, (timeline, (name, duration, duration_str)) in enumerate(zip(expected_output["timelines"], media_info)):
        start_str = f"{timeline['start']/1000:.1f}s" if timeline['start'] < 60000 else f"{timeline['start']//60000}m {(timeline['start']%60000)/1000:.1f}s"
        end_str = f"{timeline['end']/1000:.1f}s" if timeline['end'] < 60000 else f"{timeline['end']//60000}m {(timeline['end']%60000)/1000:.1f}s"
        print(f"  {name}: {start_str} - {end_str} (duration: {duration_str})")
    
    total_duration = expected_output["all_timelines"][0]["end"]
    total_str = f"{total_duration//60000}m {(total_duration%60000)/1000:.1f}s"
    print(f"  Total: {total_str}")


def example_mixed_media():
    """Example: Processing mixed audio and video files"""
    print("\n=== Example 3: Mixed Media ===")
    
    input_data = {
        "links": [
            "https://example.com/background-music.mp3",
            "https://example.com/narration.wav",
            "https://example.com/video-clip.mp4"
        ]
    }
    
    print("Input:")
    print(json.dumps(input_data, indent=2))
    
    # Mock durations: 180s music, 90s narration, 60s video
    expected_output = {
        "all_timelines": [{"start": 0, "end": 330000}],
        "timelines": [
            {"start": 0, "end": 180000},
            {"start": 180000, "end": 270000},
            {"start": 270000, "end": 330000}
        ]
    }
    
    print("\nExpected Output:")
    print(json.dumps(expected_output, indent=2))
    
    print("\nMedia Breakdown:")
    media_types = ["Background Music", "Narration", "Video Clip"]
    durations = ["3m 0.0s", "1m 30.0s", "1m 0.0s"]
    
    for i, (timeline, media_type, duration_str) in enumerate(zip(expected_output["timelines"], media_types, durations)):
        start_str = f"{timeline['start']//60000}m {(timeline['start']%60000)/1000:.1f}s" if timeline['start'] >= 60000 else f"{timeline['start']/1000:.1f}s"
        end_str = f"{timeline['end']//60000}m {(timeline['end']%60000)/1000:.1f}s"
        print(f"  {media_type}: {start_str} - {end_str} (duration: {duration_str})")


def example_error_handling():
    """Example: How the tool handles errors"""
    print("\n=== Example 4: Error Handling ===")
    
    input_data = {
        "links": [
            "https://example.com/valid-video.mp4",
            "invalid-url",  # Invalid URL
            "https://example.com/missing-file.mp4",  # File doesn't exist
            "https://example.com/another-valid.mp3"
        ]
    }
    
    print("Input (with some invalid URLs):")
    print(json.dumps(input_data, indent=2))
    
    # In real usage, invalid files would be skipped
    # Only valid files contribute to timeline
    expected_output = {
        "all_timelines": [{"start": 0, "end": 90000}],  # Only 2 valid files
        "timelines": [
            {"start": 0, "end": 45000},      # First valid file
            {"start": 45000, "end": 90000}   # Second valid file
        ]
    }
    
    print("\nExpected Output (invalid files skipped):")
    print(json.dumps(expected_output, indent=2))
    
    print("\nNote: Invalid URLs and failed downloads are automatically skipped.")
    print("Only successfully processed files contribute to the timeline.")


def example_coze_workflow_integration():
    """Example: How this would be used in a Coze workflow"""
    print("\n=== Example 5: Coze Workflow Integration ===")
    
    print("""
In a typical Coze workflow, this tool would be used as follows:

1. Coze Workflow generates media URLs:
   - User uploads or specifies media files
   - Workflow collects URLs into an array
   
2. Coze calls get_media_duration tool:
   - Passes the URLs array as 'links' parameter
   - Tool downloads and analyzes each file
   - Returns timeline information
   
3. Workflow uses timeline data:
   - Plans video editing sequence
   - Calculates total project duration
   - Passes to other tools for draft generation

Example workflow step:
""")
    
    workflow_step = {
        "tool": "get_media_duration",
        "input": {
            "links": [
                "{{user_video_1_url}}",
                "{{user_video_2_url}}",
                "{{user_audio_1_url}}"
            ]
        },
        "output_variable": "media_timelines"
    }
    
    print("Workflow Configuration:")
    print(json.dumps(workflow_step, indent=2))
    
    print("""
The 'media_timelines' variable would then contain:
- all_timelines: Total project duration
- timelines: Individual file timelines for editing

This data would be passed to subsequent tools for:
- Draft generation
- Timeline synchronization
- Effects and transitions placement
""")


def main():
    """Run all examples"""
    print("🎬 Coze Media Duration Tool Examples")
    print("=" * 50)
    
    example_single_video()
    example_multiple_videos()
    example_mixed_media()
    example_error_handling()
    example_coze_workflow_integration()
    
    print("\n" + "=" * 50)
    print("✅ Examples completed!")
    print("\nFor actual usage in Coze:")
    print("1. Configure the tool in your Coze workflow")
    print("2. Pass media URLs in the 'links' parameter")
    print("3. Use the returned timeline data for video editing")


if __name__ == "__main__":
    main()