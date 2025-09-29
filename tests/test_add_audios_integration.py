#!/usr/bin/env python3
"""
Integration test for add_audios functionality

Tests complete workflow including draft management and end-to-end operations.
"""

import sys
import os
import tempfile
import json
import uuid
import shutil
import time

# Add project root to sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Create mock runtime module for testing
class MockRuntime:
    class Args:
        def __init__(self, input_data):
            self.input = input_data
        
        def logger(self):
            return None

# Add mock to sys.modules
import types
runtime_module = types.ModuleType('runtime')
runtime_module.Args = MockRuntime.Args
sys.modules['runtime'] = runtime_module

# Import handlers
try:
    from tools.create_draft.handler import handler as create_draft_handler, Input as CreateDraftInput
    from tools.add_audios.handler import handler as add_audios_handler, Input as AddAudiosInput
    from tools.export_drafts.handler import handler as export_drafts_handler, Input as ExportDraftsInput
except ImportError as e:
    print(f"Failed to import handlers: {e}")
    sys.exit(1)


class MockArgs:
    """Mock Args class for testing"""
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def cleanup_test_files():
    """Clean up any test files"""
    test_dirs = ["/tmp/jianying_assistant"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
            except Exception as e:
                print(f"Warning: Could not clean up {test_dir}: {e}")


def test_complete_workflow():
    """Test complete workflow: create draft -> add audios -> export"""
    print("=== Testing complete workflow ===")
    
    cleanup_test_files()
    
    # Step 1: Create a draft
    print("Step 1: Creating draft...")
    create_input = CreateDraftInput(
        draft_name="测试音频项目",
        width=1920,
        height=1080,
        fps=30,
        video_quality="1080p",
        audio_quality="320k",
        background_color="#000000"
    )
    
    create_result = create_draft_handler(MockArgs(create_input))
    if not create_result.success:
        print(f"❌ Draft creation failed: {create_result.message}")
        return False
    
    draft_id = create_result.draft_id
    print(f"✅ Draft created with ID: {draft_id}")
    
    # Step 2: Add audios to the draft
    print("Step 2: Adding audios...")
    audio_infos = [
        {
            "audio_url": "https://example.com/background_music.mp3",
            "start": 0,
            "end": 30000,
            "volume": 0.8,
            "fade_in": 1000,
            "fade_out": 2000,
            "effect_type": "reverb",
            "effect_intensity": 0.5
        },
        {
            "audio_url": "https://example.com/sound_effect.wav",
            "start": 10000,
            "end": 15000,
            "volume": 1.2,
            "speed": 1.1,
            "material_start": 2000,
            "material_end": 7000
        }
    ]
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=audio_infos
    )
    
    add_result = add_audios_handler(MockArgs(add_input))
    if not add_result.success:
        print(f"❌ Audio addition failed: {add_result.message}")
        return False
    
    print(f"✅ Added {len(add_result.segment_ids)} audio segments")
    print(f"Segment IDs: {add_result.segment_ids}")
    
    # Step 3: Export the draft to verify structure
    print("Step 3: Exporting draft...")
    export_input = ExportDraftsInput(
        draft_ids=[draft_id]
    )
    
    export_result = export_drafts_handler(MockArgs(export_input))
    if not export_result.success:
        print(f"❌ Export failed: {export_result.message}")
        return False
    
    # Verify exported structure
    exported_data = json.loads(export_result.draft_data)
    draft_data = exported_data["drafts"][0]
    
    # Check audio track exists
    audio_tracks = [track for track in draft_data["tracks"] if track["track_type"] == "audio"]
    if len(audio_tracks) != 1:
        print(f"❌ Expected 1 audio track, found {len(audio_tracks)}")
        return False
    
    audio_track = audio_tracks[0]
    if len(audio_track["segments"]) != 2:
        print(f"❌ Expected 2 audio segments, found {len(audio_track['segments'])}")
        return False
    
    # Verify segment details
    segment1 = audio_track["segments"][0]
    segment2 = audio_track["segments"][1]
    
    # Check first segment
    assert segment1["type"] == "audio"
    assert segment1["material_url"] == "https://example.com/background_music.mp3"
    assert segment1["time_range"]["start"] == 0
    assert segment1["time_range"]["end"] == 30000
    assert segment1["audio"]["volume"] == 0.8
    assert segment1["audio"]["fade_in"] == 1000
    assert segment1["audio"]["fade_out"] == 2000
    assert segment1["audio"]["effect_type"] == "reverb"
    assert segment1["audio"]["effect_intensity"] == 0.5
    
    # Check second segment
    assert segment2["type"] == "audio"
    assert segment2["material_url"] == "https://example.com/sound_effect.wav"
    assert segment2["time_range"]["start"] == 10000
    assert segment2["time_range"]["end"] == 15000
    assert segment2["audio"]["volume"] == 1.2
    assert segment2["audio"]["speed"] == 1.1
    assert segment2["material_range"]["start"] == 2000
    assert segment2["material_range"]["end"] == 7000
    
    print("✅ Complete workflow test passed!")
    print(f"Draft exported successfully with {len(audio_track['segments'])} audio segments")
    
    cleanup_test_files()
    return True


def test_multiple_audio_tracks():
    """Test adding multiple audio tracks to the same draft"""
    print("=== Testing multiple audio tracks ===")
    
    cleanup_test_files()
    
    # Create a draft
    create_input = CreateDraftInput(
        draft_name="多音频轨道测试",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_draft_handler(MockArgs(create_input))
    if not create_result.success:
        print(f"❌ Draft creation failed: {create_result.message}")
        return False
    
    draft_id = create_result.draft_id
    
    # Add first audio track
    print("Adding first audio track...")
    first_track_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=[{
            "audio_url": "https://example.com/music1.mp3",
            "start": 0,
            "end": 20000,
            "volume": 0.7
        }]
    )
    
    first_result = add_audios_handler(MockArgs(first_track_input))
    if not first_result.success:
        print(f"❌ First track addition failed: {first_result.message}")
        return False
    
    # Add second audio track
    print("Adding second audio track...")
    second_track_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=[{
            "audio_url": "https://example.com/music2.wav",
            "start": 5000,
            "end": 25000,
            "volume": 0.9,
            "fade_in": 500
        }]
    )
    
    second_result = add_audios_handler(MockArgs(second_track_input))
    if not second_result.success:
        print(f"❌ Second track addition failed: {second_result.message}")
        return False
    
    # Export and verify
    export_input = ExportDraftsInput(draft_ids=[draft_id])
    export_result = export_drafts_handler(MockArgs(export_input))
    
    if not export_result.success:
        print(f"❌ Export failed: {export_result.message}")
        return False
    
    exported_data = json.loads(export_result.draft_data)
    draft_data = exported_data["drafts"][0]
    
    # Should have 2 audio tracks
    audio_tracks = [track for track in draft_data["tracks"] if track["track_type"] == "audio"]
    if len(audio_tracks) != 2:
        print(f"❌ Expected 2 audio tracks, found {len(audio_tracks)}")
        return False
    
    print("✅ Multiple audio tracks test passed!")
    print(f"Successfully created {len(audio_tracks)} audio tracks")
    
    cleanup_test_files()
    return True


def test_json_string_input():
    """Test JSON string input format"""
    print("=== Testing JSON string input ===")
    
    cleanup_test_files()
    
    # Create a draft
    create_input = CreateDraftInput(draft_name="JSON字符串测试")
    create_result = create_draft_handler(MockArgs(create_input))
    if not create_result.success:
        return False
    
    draft_id = create_result.draft_id
    
    # Test with JSON string input (matching the images example format)
    json_string = '[{"audio_url":"https://example.com/test.mp3","start":0,"end":30000,"volume":0.8,"fade_in":1000,"fade_out":2000,"effect_type":"echo","effect_intensity":0.7}]'
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=json_string
    )
    
    add_result = add_audios_handler(MockArgs(add_input))
    if not add_result.success:
        print(f"❌ JSON string input failed: {add_result.message}")
        return False
    
    print("✅ JSON string input test passed!")
    
    cleanup_test_files()
    return True


def test_error_handling():
    """Test various error conditions"""
    print("=== Testing error handling ===")
    
    # Test 1: Invalid draft ID
    add_input = AddAudiosInput(
        draft_id="invalid-uuid",
        audio_infos=[{"audio_url": "test.mp3", "start": 0, "end": 1000}]
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if result.success:
        print("❌ Should have failed with invalid UUID")
        return False
    print("✅ Invalid UUID handling works")
    
    # Test 2: Non-existent draft
    add_input = AddAudiosInput(
        draft_id=str(uuid.uuid4()),
        audio_infos=[{"audio_url": "test.mp3", "start": 0, "end": 1000}]
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if result.success:
        print("❌ Should have failed with non-existent draft")
        return False
    print("✅ Non-existent draft handling works")
    
    # Test 3: Invalid audio_infos format
    cleanup_test_files()
    create_input = CreateDraftInput(draft_name="错误测试")
    create_result = create_draft_handler(MockArgs(create_input))
    draft_id = create_result.draft_id
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos="invalid json"
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if result.success:
        print("❌ Should have failed with invalid JSON")
        return False
    print("✅ Invalid JSON handling works")
    
    print("✅ Error handling test passed!")
    cleanup_test_files()
    return True


def main():
    """Run all integration tests"""
    print("Starting add_audios integration tests...")
    
    tests = [
        test_complete_workflow,
        test_multiple_audio_tracks,
        test_json_string_input,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n=== Integration Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)