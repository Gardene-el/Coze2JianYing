#!/usr/bin/env python3
"""
Test for add_audios tool

Tests the audio addition functionality:
1. add_audios tool creates audio tracks correctly
2. Multiple input formats are supported
3. Integration with make_audio_info works correctly
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
            "name": "Test Audio Project",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_quality": "1080p",
            "audio_quality": "320k",
            "background_color": "#000000"
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


def test_add_audios_basic():
    """Test basic add_audios functionality"""
    print("=== Testing add_audios basic functionality ===")
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_audios.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Set up test environment
    draft_id = setup_test_environment()
    
    try:
        # Test 1: Add single audio with array format
        print("\nTest 1: Add single audio (array format)")
        input_data = Input(
            draft_id=draft_id,
            audio_infos=[{
                "audio_url": "https://example.com/bgm.mp3",
                "start": 0,
                "end": 30000,
                "volume": 0.7,
                "fade_in": 2000,
                "fade_out": 3000
            }]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"Should succeed: {result.message}"
        assert len(result.segment_ids) == 1, "Should create 1 segment"
        assert len(result.segment_infos) == 1, "Should return 1 segment info"
        print(f"✅ Created segment: {result.segment_ids[0]}")
        
        # Verify the draft config was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            draft_config = json.load(f)
        
        assert len(draft_config["tracks"]) == 1, "Should have 1 track"
        assert draft_config["tracks"][0]["track_type"] == "audio", "Should be audio track"
        assert len(draft_config["tracks"][0]["segments"]) == 1, "Track should have 1 segment"
        
        segment = draft_config["tracks"][0]["segments"][0]
        assert segment["type"] == "audio"
        assert segment["material_url"] == "https://example.com/bgm.mp3"
        assert segment["audio"]["volume"] == 0.7
        assert segment["audio"]["fade_in"] == 2000
        assert segment["audio"]["fade_out"] == 3000
        print("✅ Draft config updated correctly")
        
        # Test 2: Add multiple audios
        print("\nTest 2: Add multiple audios")
        input_data = Input(
            draft_id=draft_id,
            audio_infos=[
                {
                    "audio_url": "https://example.com/narration.mp3",
                    "start": 5000,
                    "end": 25000,
                    "volume": 1.0
                },
                {
                    "audio_url": "https://example.com/effect.mp3",
                    "start": 10000,
                    "end": 11000,
                    "volume": 0.8
                }
            ]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success
        assert len(result.segment_ids) == 2, "Should create 2 segments"
        print(f"✅ Created {len(result.segment_ids)} segments")
        
        # Verify multiple tracks were created
        with open(config_file, 'r', encoding='utf-8') as f:
            draft_config = json.load(f)
        
        assert len(draft_config["tracks"]) == 2, "Should have 2 tracks now"
        print("✅ Multiple tracks created successfully")
        
        print("\n✅ All basic functionality tests passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


def test_add_audios_formats():
    """Test different input formats"""
    print("\n=== Testing different input formats ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_audios.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    draft_id = setup_test_environment()
    
    try:
        # Test 1: JSON string format
        print("\nTest 1: JSON string format")
        audio_infos_json = json.dumps([{
            "audio_url": "https://example.com/audio1.mp3",
            "start": 0,
            "end": 5000
        }])
        
        input_data = Input(
            draft_id=draft_id,
            audio_infos=audio_infos_json
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"JSON string format should work: {result.message}"
        assert len(result.segment_ids) == 1
        print("✅ JSON string format works")
        
        # Test 2: Array of strings format (from make_audio_info)
        print("\nTest 2: Array of strings format")
        audio_info_str1 = '{"audio_url":"https://example.com/audio2.mp3","start":0,"end":10000,"volume":0.7}'
        audio_info_str2 = '{"audio_url":"https://example.com/audio3.mp3","start":10000,"end":20000,"fade_in":1000}'
        
        input_data = Input(
            draft_id=draft_id,
            audio_infos=[audio_info_str1, audio_info_str2]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"Array of strings should work: {result.message}"
        assert len(result.segment_ids) == 2
        print("✅ Array of strings format works")
        
        # Test 3: Direct array of dicts (most common)
        print("\nTest 3: Direct array of dicts")
        input_data = Input(
            draft_id=draft_id,
            audio_infos=[
                {"audio_url": "https://example.com/audio4.mp3", "start": 0, "end": 5000}
            ]
        )
        result = handler(MockArgs(input_data))
        
        assert result.success, f"Array of dicts should work: {result.message}"
        assert len(result.segment_ids) == 1
        print("✅ Array of dicts format works")
        
        print("\n✅ All format tests passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


def test_add_audios_integration():
    """Test integration with make_audio_info"""
    print("\n=== Testing integration with make_audio_info ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_audio_info.handler import handler as make_audio_info_handler
    from tools.make_audio_info.handler import Input as MakeAudioInfoInput
    from tools.add_audios.handler import handler as add_audios_handler
    from tools.add_audios.handler import Input as AddAudiosInput
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    draft_id = setup_test_environment()
    
    try:
        print("\nCreating audio info strings with make_audio_info...")
        
        # Create audio info strings
        audio1_result = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
            audio_url="https://example.com/bgm.mp3",
            start=0,
            end=30000,
            volume=0.3,
            fade_in=2000
        )))
        
        audio2_result = make_audio_info_handler(MockArgs(MakeAudioInfoInput(
            audio_url="https://example.com/narration.mp3",
            start=5000,
            end=25000,
            volume=0.9
        )))
        
        assert audio1_result.success
        assert audio2_result.success
        print(f"✅ Created 2 audio info strings")
        print(f"   Audio 1: {audio1_result.audio_info_string}")
        print(f"   Audio 2: {audio2_result.audio_info_string}")
        
        # Use the strings with add_audios
        print("\nAdding audios using the info strings...")
        audio_infos_array = [
            audio1_result.audio_info_string,
            audio2_result.audio_info_string
        ]
        
        result = add_audios_handler(MockArgs(AddAudiosInput(
            draft_id=draft_id,
            audio_infos=audio_infos_array
        )))
        
        assert result.success, f"Should succeed: {result.message}"
        assert len(result.segment_ids) == 2
        print(f"✅ Successfully added {len(result.segment_ids)} audios")
        
        # Verify the segments have correct properties
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            draft_config = json.load(f)
        
        track = draft_config["tracks"][0]
        assert len(track["segments"]) == 2
        
        # Check first audio (bgm)
        seg1 = track["segments"][0]
        assert seg1["material_url"] == "https://example.com/bgm.mp3"
        assert seg1["audio"]["volume"] == 0.3
        assert seg1["audio"]["fade_in"] == 2000
        
        # Check second audio (narration)
        seg2 = track["segments"][1]
        assert seg2["material_url"] == "https://example.com/narration.mp3"
        assert seg2["audio"]["volume"] == 0.9
        
        print("✅ All audio properties preserved correctly")
        
        print("\n✅ Integration test passed!")
        return True
        
    finally:
        cleanup_test_environment(draft_id)


def test_add_audios_validation():
    """Test parameter validation"""
    print("\n=== Testing parameter validation ===")
    
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.add_audios.handler import handler, Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Invalid draft_id
    print("\nTest 1: Invalid draft_id")
    input_data = Input(
        draft_id="invalid-uuid",
        audio_infos=[{"audio_url": "https://example.com/audio.mp3", "start": 0, "end": 5000}]
    )
    result = handler(MockArgs(input_data))
    assert not result.success
    print(f"✅ Correctly rejected: {result.message}")
    
    # Test 2: Non-existent draft
    print("\nTest 2: Non-existent draft")
    fake_uuid = str(uuid.uuid4())
    input_data = Input(
        draft_id=fake_uuid,
        audio_infos=[{"audio_url": "https://example.com/audio.mp3", "start": 0, "end": 5000}]
    )
    result = handler(MockArgs(input_data))
    assert not result.success
    assert "not found" in result.message.lower()
    print(f"✅ Correctly rejected: {result.message}")
    
    # Test 3: Missing required field in audio_info
    draft_id = setup_test_environment()
    try:
        print("\nTest 3: Missing required field")
        input_data = Input(
            draft_id=draft_id,
            audio_infos=[{"audio_url": "https://example.com/audio.mp3", "start": 0}]  # missing 'end'
        )
        result = handler(MockArgs(input_data))
        assert not result.success
        assert "end" in result.message.lower()
        print(f"✅ Correctly rejected: {result.message}")
        
    finally:
        cleanup_test_environment(draft_id)
    
    print("\n✅ All validation tests passed!")
    return True


if __name__ == "__main__":
    results = []
    
    try:
        results.append(test_add_audios_basic())
        results.append(test_add_audios_formats())
        results.append(test_add_audios_integration())
        results.append(test_add_audios_validation())
        
        print(f"\n{'='*50}")
        print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
        print(f"{'='*50}")
        
        if all(results):
            print("✅ All tests passed successfully!")
            sys.exit(0)
        else:
            print("❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
