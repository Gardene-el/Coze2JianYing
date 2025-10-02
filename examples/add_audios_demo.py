#!/usr/bin/env python3
"""
Demo for add_audios tool

Demonstrates how to use the add_audios tool to add audio tracks to a draft.
Shows integration with make_audio_info and different input formats.
"""

import os
import sys
import json
import uuid
import shutil

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def demo_add_audios():
    """Demonstrate the add_audios tool functionality"""
    
    print("=" * 70)
    print("ADD AUDIOS TOOL DEMO")
    print("=" * 70)
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.create_draft.handler import handler as create_draft_handler
    from tools.create_draft.handler import Input as CreateDraftInput
    from tools.add_audios.handler import handler as add_audios_handler
    from tools.add_audios.handler import Input as AddAudiosInput
    from tools.make_audio_info.handler import handler as make_audio_info_handler
    from tools.make_audio_info.handler import Input as MakeAudioInfoInput
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Step 1: Create a draft
    print("\n" + "=" * 70)
    print("Step 1: Creating a Draft")
    print("=" * 70)
    
    draft_result = create_draft_handler(MockArgs(CreateDraftInput(
        draft_name="Audio Demo Project",
        width=1920,
        height=1080,
        fps=30
    )))
    
    draft_id = draft_result["draft_id"]
    print(f"✅ Created draft with ID: {draft_id}")
    
    # Step 2: Add background music using array format
    print("\n" + "=" * 70)
    print("Step 2: Adding Background Music (Array Format)")
    print("=" * 70)
    
    bgm_data = [{
        "audio_url": "https://example.com/background_music.mp3",
        "start": 0,
        "end": 60000,
        "volume": 0.3,
        "fade_in": 2000,
        "fade_out": 3000
    }]
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=bgm_data
    )))
    
    print(f"Status: {result.message}")
    print(f"Created {len(result.segment_ids)} audio segment(s)")
    print(f"Segment IDs: {result.segment_ids}")
    print(f"\nSegment info:")
    for seg_info in result.segment_infos:
        print(f"  - ID: {seg_info['id']}")
        print(f"    Timeline: {seg_info['start']/1000:.1f}s - {seg_info['end']/1000:.1f}s")
    
    # Step 3: Add narration using make_audio_info (array of strings format)
    print("\n" + "=" * 70)
    print("Step 3: Adding Narration (Array of Strings Format)")
    print("=" * 70)
    print("Using make_audio_info to generate configuration strings")
    
    # Generate audio info strings
    narration_result = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/narration.mp3",
        start=5000,
        end=55000,
        volume=1.0
    )))
    
    print(f"\nGenerated audio info string:")
    print(f"  {narration_result["audio_info_string"]}")
    
    # Use array of strings format
    audio_infos_array = [narration_result["audio_info_string"]]
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=audio_infos_array
    )))
    
    print(f"\n{result.message}")
    print(f"Created {len(result.segment_ids)} audio segment(s)")
    
    # Step 4: Add multiple sound effects at once
    print("\n" + "=" * 70)
    print("Step 4: Adding Multiple Sound Effects")
    print("=" * 70)
    
    # Create multiple sound effect configs using make_audio_info
    sfx_configs = []
    
    # Click sound at 10 seconds
    sfx1 = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/click.mp3",
        start=10000,
        end=10300,
        volume=0.8
    )))
    sfx_configs.append(sfx1["audio_info_string"])
    
    # Whoosh sound at 15 seconds
    sfx2 = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/whoosh.mp3",
        start=15000,
        end=15800,
        volume=0.9
    )))
    sfx_configs.append(sfx2["audio_info_string"])
    
    # Notification at 20 seconds
    sfx3 = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/notification.mp3",
        start=20000,
        end=20500,
        volume=0.7
    )))
    sfx_configs.append(sfx3["audio_info_string"])
    
    print(f"Prepared {len(sfx_configs)} sound effect configurations")
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=sfx_configs
    )))
    
    print(f"\n{result.message}")
    print(f"Created {len(result.segment_ids)} audio segment(s)")
    for i, seg_info in enumerate(result.segment_infos, 1):
        print(f"  Effect {i}: {seg_info['start']/1000:.1f}s - {seg_info['end']/1000:.1f}s")
    
    # Step 5: Add audio with effects and speed control
    print("\n" + "=" * 70)
    print("Step 5: Adding Audio with Effects")
    print("=" * 70)
    
    effect_audio = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/voice_effect.mp3",
        start=25000,
        end=35000,
        volume=0.95,
        effect_type="变声",
        effect_intensity=0.8,
        speed=1.2
    )))
    
    print(f"Audio info with effects:")
    print(f"  {effect_audio["audio_info_string"]}")
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=[effect_audio["audio_info_string"]]
    )))
    
    print(f"\n{result.message}")
    
    # Step 6: Add trimmed audio segment
    print("\n" + "=" * 70)
    print("Step 6: Adding Trimmed Audio Segment")
    print("=" * 70)
    print("Using material_range to extract a portion of a long audio file")
    
    trimmed_audio = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
        audio_url="https://example.com/long_song.mp3",
        start=40000,
        end=55000,  # 15 seconds on timeline
        material_start=120000,  # Start from 2:00 in the audio file
        material_end=135000,    # End at 2:15 in the audio file
        volume=0.4,
        fade_in=1000,
        fade_out=2000
    )))
    
    print(f"Trimmed audio config:")
    print(f"  {trimmed_audio["audio_info_string"]}")
    print(f"\nThis uses 2:00-2:15 from the original audio,")
    print(f"but plays at timeline position 40-55 seconds")
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=[trimmed_audio["audio_info_string"]]
    )))
    
    print(f"\n{result.message}")
    
    # Step 7: Inspect final draft structure
    print("\n" + "=" * 70)
    print("Step 7: Inspecting Final Draft Structure")
    print("=" * 70)
    
    config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    print(f"Draft ID: {draft_config['draft_id']}")
    print(f"Project Name: {draft_config['project']['name']}")
    print(f"Resolution: {draft_config['project']['width']}x{draft_config['project']['height']}")
    print(f"Total Audio Tracks: {len(draft_config['tracks'])}")
    
    # Count total segments across all tracks
    total_segments = sum(len(track['segments']) for track in draft_config['tracks'])
    print(f"Total Audio Segments: {total_segments}")
    
    # Show track details
    print(f"\nTrack breakdown:")
    for i, track in enumerate(draft_config['tracks'], 1):
        print(f"  Track {i}: {track['track_type']} - {len(track['segments'])} segment(s)")
        for j, segment in enumerate(track['segments'], 1):
            duration_sec = (segment['time_range']['end'] - segment['time_range']['start']) / 1000
            print(f"    Segment {j}: {duration_sec:.1f}s, volume={segment['audio']['volume']}")
    
    # Step 8: Demonstrate JSON string format
    print("\n" + "=" * 70)
    print("Step 8: Alternative Format - JSON String")
    print("=" * 70)
    
    json_string_data = json.dumps([{
        "audio_url": "https://example.com/final_audio.mp3",
        "start": 58000,
        "end": 60000,
        "volume": 0.5
    }])
    
    print(f"Using JSON string format:")
    print(f"  {json_string_data}")
    
    result = add_audios_handler(MockArgs(AddAudiosInput(
        draft_id=draft_id,
        audio_infos=json_string_data
    )))
    
    print(f"\n{result.message}")
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    
    # Reload config to get final state
    with open(config_file, 'r', encoding='utf-8') as f:
        final_config = json.load(f)
    
    total_tracks = len(final_config['tracks'])
    total_segments = sum(len(track['segments']) for track in final_config['tracks'])
    
    print(f"""
Successfully demonstrated add_audios tool!

Final Draft Statistics:
- Draft ID: {draft_id}
- Total Audio Tracks: {total_tracks}
- Total Audio Segments: {total_segments}

What we added:
1. Background music (60s, volume 0.3, with fade in/out)
2. Narration (50s, full volume)
3. Multiple sound effects (3 short clips)
4. Audio with voice effect and speed control
5. Trimmed audio segment from a long file
6. Final audio clip using JSON string format

Key Features Demonstrated:
✅ Multiple input formats (array, array of strings, JSON string)
✅ Integration with make_audio_info
✅ Volume control and fade effects
✅ Audio effects and speed control
✅ Material range for trimming
✅ Multiple tracks for audio layering

Each call to add_audios creates a new track.
All tracks are mixed together in the final video.
    """)
    
    # Cleanup
    print("\n" + "=" * 70)
    print("Cleanup")
    print("=" * 70)
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    if os.path.exists(draft_folder):
        shutil.rmtree(draft_folder)
        print(f"✅ Cleaned up test draft: {draft_id}")


if __name__ == "__main__":
    try:
        demo_add_audios()
        print("\n✅ Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
