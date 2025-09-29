#!/usr/bin/env python3
"""
Simple test for add_audios functionality
Tests basic audio segment parsing and creation without requiring existing drafts
"""

import sys
import os
import tempfile
import json
import uuid

# Add project root to sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Create mock runtime module for testing
class MockRuntime:
    class Args:
        def __init__(self, input_data):
            self.input = input_data

# Add mock to sys.modules
import types
runtime_module = types.ModuleType('runtime')
runtime_module.Args = MockRuntime.Args
sys.modules['runtime'] = runtime_module

# Import the add_audios handler and related functions
try:
    from tools.add_audios.handler import (
        parse_audio_infos, 
        create_audio_track_with_segments,
        validate_uuid_format,
        Input, Output
    )
except ImportError as e:
    print(f"Failed to import add_audios components: {e}")
    sys.exit(1)


def test_parse_audio_infos():
    """Test parse_audio_infos function directly"""
    print("=== Testing parse_audio_infos function directly ===")
    
    # Test case 1: Valid input
    test_input = [
        {
            "audio_url": "https://example.com/music.mp3",
            "start": 0,
            "end": 30000,
            "volume": 0.8,
            "fade_in": 1000,
            "fade_out": 2000
        }
    ]
    
    try:
        result = parse_audio_infos(test_input)
        assert len(result) == 1
        assert result[0]["material_url"] == "https://example.com/music.mp3"
        assert result[0]["start"] == 0
        assert result[0]["end"] == 30000
        assert result[0]["volume"] == 0.8
        print("✅ Valid input parsing passed")
    except Exception as e:
        print(f"❌ Valid input parsing failed: {e}")
        return False
    
    # Test case 2: Multiple audios
    test_input_multi = [
        {"audio_url": "https://example.com/music1.mp3", "start": 0, "end": 15000, "volume": 0.7},
        {"audio_url": "https://example.com/music2.wav", "start": 15000, "end": 30000, "volume": 1.0}
    ]
    
    try:
        result = parse_audio_infos(test_input_multi)
        assert len(result) == 2
        assert result[0]["material_url"] == "https://example.com/music1.mp3"
        assert result[1]["material_url"] == "https://example.com/music2.wav"
        print("✅ Multiple audios parsing passed")
    except Exception as e:
        print(f"❌ Multiple audios parsing failed: {e}")
        return False
    
    # Test case 3: Invalid JSON
    try:
        parse_audio_infos("invalid json")
        print("❌ Invalid JSON should have failed")
        return False
    except ValueError:
        print("✅ Invalid JSON error handling passed")
    except Exception as e:
        print(f"❌ Invalid JSON error handling failed with wrong exception: {e}")
        return False
    
    # Test case 4: Missing required fields
    try:
        parse_audio_infos([{"audio_url": "https://example.com/music.mp3", "start": 0}])  # Missing 'end'
        print("❌ Missing required fields should have failed")
        return False
    except ValueError as ve:
        if "Missing required field" in str(ve):
            print("✅ Missing required fields error handling passed")
        else:
            print(f"❌ Wrong error message for missing fields: {ve}")
            return False
    except Exception as e:
        print(f"❌ Missing required fields error handling failed: {e}")
        return False
    
    print("✅ All parse_audio_infos tests passed!")
    return True


def test_audio_segment_creation():
    """Test audio segment structure creation"""
    print("=== Testing audio segment creation ===")
    
    audio_infos = [
        {
            "material_url": "https://example.com/background.mp3",
            "start": 0,
            "end": 30000,
            "volume": 0.8,
            "fade_in": 1000,
            "fade_out": 2000,
            "effect_type": "reverb",
            "effect_intensity": 0.5,
            "speed": 1.0
        }
    ]
    
    try:
        segment_ids, segment_infos, track = create_audio_track_with_segments(audio_infos)
        
        # Validate results
        assert len(segment_ids) == 1
        assert len(segment_infos) == 1
        assert track["track_type"] == "audio"
        assert len(track["segments"]) == 1
        
        segment = track["segments"][0]
        assert segment["type"] == "audio"
        assert segment["material_url"] == "https://example.com/background.mp3"
        assert segment["time_range"]["start"] == 0
        assert segment["time_range"]["end"] == 30000
        assert segment["audio"]["volume"] == 0.8
        assert segment["audio"]["fade_in"] == 1000
        assert segment["audio"]["fade_out"] == 2000
        assert segment["audio"]["effect_type"] == "reverb"
        assert segment["audio"]["effect_intensity"] == 0.5
        assert segment["audio"]["speed"] == 1.0
        
        print("✅ Audio segment structure created correctly")
        return True
    except Exception as e:
        print(f"❌ Audio segment creation failed: {e}")
        return False


def test_output_format():
    """Test output format matches requirements"""
    print("=== Testing output format ===")
    
    # Create a sample output
    segment_ids = ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    segment_infos = [{"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "start": 0, "end": 30000}]
    
    output = Output(
        segment_ids=segment_ids,
        segment_infos=segment_infos,
        success=True,
        message="成功添加 1 个音频片段"
    )
    
    # Validate output structure
    assert output.success == True
    assert len(output.segment_ids) == 1
    assert len(output.segment_infos) == 1
    assert "成功添加" in output.message
    
    print("✅ Output format matches requirements")
    return True


def test_draft_config_integration():
    """Test integration with draft config structure"""
    print("=== Testing draft config integration ===")
    
    # Create temporary test draft config
    test_draft_config = {
        "draft_id": str(uuid.uuid4()),
        "project": {"name": "测试项目"},
        "tracks": [],
        "last_modified": 0
    }
    
    audio_infos = [
        {
            "material_url": "https://example.com/test.mp3",
            "start": 0,
            "end": 15000,
            "volume": 1.0
        }
    ]
    
    try:
        segment_ids, segment_infos, audio_track = create_audio_track_with_segments(audio_infos)
        
        # Simulate adding track to config
        test_draft_config["tracks"].append(audio_track)
        test_draft_config["last_modified"] = 123456789
        
        # Validate integration
        assert len(test_draft_config["tracks"]) == 1
        assert test_draft_config["tracks"][0]["track_type"] == "audio"
        assert test_draft_config["last_modified"] == 123456789
        
        print("✅ Draft config integration working correctly")
        return True
    except Exception as e:
        print(f"❌ Draft config integration failed: {e}")
        return False


def test_input_format_flexibility():
    """Test different input format handling"""
    print("=== Testing input format flexibility ===")
    
    # Test JSON string input
    json_input = '[{"audio_url":"https://example.com/music.mp3","start":0,"end":30000,"volume":0.8}]'
    print("Testing JSON string input...")
    try:
        result = parse_audio_infos(json_input)
        assert len(result) == 1
        assert result[0]["material_url"] == "https://example.com/music.mp3"
        print("✅ JSON string input works correctly")
    except Exception as e:
        print(f"❌ JSON string input failed: {e}")
        return False
    
    # Test list input
    list_input = [{"audio_url": "https://example.com/music.mp3", "start": 0, "end": 30000, "volume": 0.8}]
    print("Testing list input...")
    try:
        result = parse_audio_infos(list_input)
        assert len(result) == 1
        assert result[0]["material_url"] == "https://example.com/music.mp3"
        print("✅ List input works correctly")
    except Exception as e:
        print(f"❌ List input failed: {e}")
        return False
    
    # Test complex audio case similar to images example
    complex_input = '[{"audio_url":"https://example.com/bg_music.mp3","start":0,"end":30000,"volume":0.7,"fade_in":1000,"fade_out":2000,"effect_type":"reverb","effect_intensity":0.5},{"audio_url":"https://example.com/sound_effect.wav","start":10000,"end":15000,"volume":1.2,"speed":1.1}]'
    print("Testing complex audio case...")
    try:
        result = parse_audio_infos(complex_input)
        assert len(result) == 2
        assert result[0]["material_url"] == "https://example.com/bg_music.mp3"
        assert result[0]["volume"] == 0.7
        assert result[0]["fade_in"] == 1000
        assert result[0]["effect_type"] == "reverb"
        assert result[1]["material_url"] == "https://example.com/sound_effect.wav"
        assert result[1]["speed"] == 1.1
        print("✅ Complex audio case works - comprehensive audio parameter support!")
    except Exception as e:
        print(f"❌ Complex audio case failed: {e}")
        return False
    
    print("✅ Input format flexibility test passed!")
    return True


def main():
    """Run all tests"""
    print("Starting simple add_audios tests...")
    
    tests = [
        test_parse_audio_infos,
        test_audio_segment_creation,
        test_output_format,
        test_draft_config_integration,
        test_input_format_flexibility
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)