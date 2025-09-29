#!/usr/bin/env python3
"""
Test script for the new add content tools

Tests the add_videos, add_audios, add_captions, add_images, and add_effects tools
"""

import os
import sys
import json
import shutil
import tempfile
from typing import NamedTuple


def create_mock_args(input_data):
    """Create mock Args object for testing"""
    class MockLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = MockLogger()
    
    return MockArgs(input_data)


def setup_test_draft():
    """Create a test draft for testing purposes"""
    import uuid
    import time
    
    draft_id = str(uuid.uuid4())
    
    # Create draft folder
    base_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
    draft_folder = os.path.join(base_dir, draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    # Create initial draft config
    config = {
        "draft_id": draft_id,
        "project": {
            "name": "测试项目",
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
        "created_timestamp": time.time(),
        "last_modified": time.time(),
        "status": "created"
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return draft_id


def test_add_videos():
    """Test the add_videos tool"""
    print("=== Testing add_videos tool ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the handler
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_videos')
        import handler as add_videos_handler
        
        # Create test input
        class TestInput(NamedTuple):
            draft_id: str
            video_urls: list
            filters: list = None
            transitions: list = None
            volumes: list = None
            start_time: int = 0
        
        test_input = TestInput(
            draft_id=draft_id,
            video_urls=[
                "https://example.com/video1.mp4",
                "https://example.com/video2.mp4"
            ],
            filters=["暖冬", "电影"],
            transitions=["淡化", "切镜"],
            volumes=[1.0, 0.8],
            start_time=0
        )
        
        # Test the handler
        mock_args = create_mock_args(test_input)
        result = add_videos_handler.handler(mock_args)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Track index: {result.track_index}")
        print(f"Total duration: {result.total_duration}ms")
        
        # Verify the draft was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Total tracks: {len(config.get('tracks', []))}")
        print(f"Media resources: {len(config.get('media_resources', []))}")
        
        assert result.success, "add_videos should succeed"
        assert result.track_index == 0, "First track should have index 0"
        assert len(config['tracks']) == 1, "Should have 1 track"
        assert config['tracks'][0]['track_type'] == "video", "Track should be video type"
        
        print("✅ add_videos test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_videos test failed: {str(e)}")
        return False
    finally:
        sys.path.pop(0)


def test_add_audios():
    """Test the add_audios tool"""
    print("\n=== Testing add_audios tool ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the handler
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_audios')
        import handler as add_audios_handler
        
        # Create test input
        class TestInput(NamedTuple):
            draft_id: str
            audio_urls: list
            volumes: list = None
            fade_ins: list = None
            fade_outs: list = None
            effects: list = None
            start_time: int = 0
        
        test_input = TestInput(
            draft_id=draft_id,
            audio_urls=[
                "https://example.com/audio1.mp3",
                "https://example.com/audio2.mp3"
            ],
            volumes=[0.8, 1.0],
            fade_ins=[1000, 500],
            fade_outs=[2000, 1000],
            effects=["回声", None],
            start_time=0
        )
        
        # Test the handler
        mock_args = create_mock_args(test_input)
        result = add_audios_handler.handler(mock_args)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Track index: {result.track_index}")
        print(f"Total duration: {result.total_duration}ms")
        
        # Verify the draft was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Total tracks: {len(config.get('tracks', []))}")
        print(f"Media resources: {len(config.get('media_resources', []))}")
        
        assert result.success, "add_audios should succeed"
        assert result.track_index == 0, "First track should have index 0"
        assert len(config['tracks']) == 1, "Should have 1 track"
        assert config['tracks'][0]['track_type'] == "audio", "Track should be audio type"
        
        print("✅ add_audios test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_audios test failed: {str(e)}")
        return False
    finally:
        sys.path.pop(0)


def test_add_captions():
    """Test the add_captions tool"""
    print("\n=== Testing add_captions tool ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the handler
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_captions')
        import handler as add_captions_handler
        
        # Create test input
        class TestInput(NamedTuple):
            draft_id: str
            captions: list
            font_family: str = "思源黑体"
            font_size: int = 48
            color: str = "#FFFFFF"
            position_x: float = 0.5
            position_y: float = 0.9
            alignment: str = "center"
        
        test_input = TestInput(
            draft_id=draft_id,
            captions=[
                {
                    "text": "欢迎使用Coze剪映助手",
                    "start_time": 0,
                    "end_time": 3000
                },
                {
                    "text": "这是第二个字幕",
                    "start_time": 3000,
                    "end_time": 6000,
                    "position_x": 0.3,
                    "position_y": 0.8
                }
            ],
            font_family="思源黑体",
            font_size=48,
            color="#FFFFFF",
            position_x=0.5,
            position_y=0.9,
            alignment="center"
        )
        
        # Test the handler
        mock_args = create_mock_args(test_input)
        result = add_captions_handler.handler(mock_args)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Track index: {result.track_index}")
        print(f"Total captions: {result.total_captions}")
        
        # Verify the draft was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Total tracks: {len(config.get('tracks', []))}")
        
        assert result.success, "add_captions should succeed"
        assert result.track_index == 0, "First track should have index 0"
        assert result.total_captions == 2, "Should have 2 captions"
        assert len(config['tracks']) == 1, "Should have 1 track"
        assert config['tracks'][0]['track_type'] == "text", "Track should be text type"
        
        print("✅ add_captions test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_captions test failed: {str(e)}")
        return False
    finally:
        sys.path.pop(0)


def test_add_images():
    """Test the add_images tool"""
    print("\n=== Testing add_images tool ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the handler
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_images')
        import handler as add_images_handler
        
        # Create test input
        class TestInput(NamedTuple):
            draft_id: str
            image_urls: list
            durations: list = None
            transitions: list = None
            positions_x: list = None
            positions_y: list = None
            scales: list = None
            start_time: int = 0
        
        test_input = TestInput(
            draft_id=draft_id,
            image_urls=[
                "https://example.com/image1.jpg",
                "https://example.com/image2.png"
            ],
            durations=[3000, 4000],
            transitions=["淡化", "切镜"],
            positions_x=[0.0, 0.1],
            positions_y=[0.0, -0.1],
            scales=[1.0, 1.2],
            start_time=0
        )
        
        # Test the handler
        mock_args = create_mock_args(test_input)
        result = add_images_handler.handler(mock_args)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Track index: {result.track_index}")
        print(f"Total duration: {result.total_duration}ms")
        
        # Verify the draft was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Total tracks: {len(config.get('tracks', []))}")
        print(f"Media resources: {len(config.get('media_resources', []))}")
        
        assert result.success, "add_images should succeed"
        assert result.track_index == 0, "First track should have index 0"
        assert len(config['tracks']) == 1, "Should have 1 track"
        assert config['tracks'][0]['track_type'] == "video", "Track should be video type (images as video)"
        
        print("✅ add_images test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_images test failed: {str(e)}")
        return False
    finally:
        sys.path.pop(0)


def test_add_effects():
    """Test the add_effects tool"""
    print("\n=== Testing add_effects tool ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Import the handler
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_effects')
        import handler as add_effects_handler
        
        # Create test input
        class TestInput(NamedTuple):
            draft_id: str
            effects: list
            default_intensity: float = 1.0
            default_position_x: float = None
            default_position_y: float = None
            default_scale: float = 1.0
        
        test_input = TestInput(
            draft_id=draft_id,
            effects=[
                {
                    "effect_type": "光效闪烁",
                    "start_time": 1000,
                    "end_time": 3000,
                    "intensity": 0.8,
                    "position_x": 0.5,
                    "position_y": 0.5
                },
                {
                    "effect_type": "粒子爆炸",
                    "start_time": 5000,
                    "end_time": 7000,
                    "properties": {
                        "particle_count": 100,
                        "color": "#FF0000"
                    }
                }
            ],
            default_intensity=1.0,
            default_position_x=None,
            default_position_y=None,
            default_scale=1.0
        )
        
        # Test the handler
        mock_args = create_mock_args(test_input)
        result = add_effects_handler.handler(mock_args)
        
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Track index: {result.track_index}")
        print(f"Total effects: {result.total_effects}")
        
        # Verify the draft was updated
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Total tracks: {len(config.get('tracks', []))}")
        
        assert result.success, "add_effects should succeed"
        assert result.track_index == 0, "First track should have index 0"
        assert result.total_effects == 2, "Should have 2 effects"
        assert len(config['tracks']) == 1, "Should have 1 track"
        assert config['tracks'][0]['track_type'] == "effect", "Track should be effect type"
        
        print("✅ add_effects test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_effects test failed: {str(e)}")
        return False
    finally:
        sys.path.pop(0)


def test_integration():
    """Test integration of all tools with the same draft"""
    print("\n=== Testing integration of all tools ===")
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft for integration: {draft_id}")
    
    try:
        # Test adding videos first
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_videos')
        import handler as add_videos_handler
        
        class VideoInput(NamedTuple):
            draft_id: str
            video_urls: list
            start_time: int = 0
        
        video_input = VideoInput(
            draft_id=draft_id,
            video_urls=["https://example.com/main.mp4"],
            start_time=0
        )
        
        video_result = add_videos_handler.handler(create_mock_args(video_input))
        print(f"Videos added: {video_result.success}")
        sys.path.pop(0)
        
        # Test adding audios
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_audios')
        import handler as add_audios_handler
        
        class AudioInput(NamedTuple):
            draft_id: str
            audio_urls: list
            start_time: int = 0
        
        audio_input = AudioInput(
            draft_id=draft_id,
            audio_urls=["https://example.com/bgm.mp3"],
            start_time=0
        )
        
        audio_result = add_audios_handler.handler(create_mock_args(audio_input))
        print(f"Audios added: {audio_result.success}")
        sys.path.pop(0)
        
        # Test adding captions
        sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_captions')
        import handler as add_captions_handler
        
        class CaptionInput(NamedTuple):
            draft_id: str
            captions: list
        
        caption_input = CaptionInput(
            draft_id=draft_id,
            captions=[
                {"text": "集成测试字幕", "start_time": 1000, "end_time": 4000}
            ]
        )
        
        caption_result = add_captions_handler.handler(create_mock_args(caption_input))
        print(f"Captions added: {caption_result.success}")
        sys.path.pop(0)
        
        # Verify final state
        config_file = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id, "draft_config.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"Final state - Total tracks: {len(config.get('tracks', []))}")
        print(f"Final state - Media resources: {len(config.get('media_resources', []))}")
        
        track_types = [track['track_type'] for track in config.get('tracks', [])]
        print(f"Track types: {track_types}")
        
        assert len(config['tracks']) == 3, "Should have 3 tracks (video, audio, text)"
        assert "video" in track_types, "Should have video track"
        assert "audio" in track_types, "Should have audio track"
        assert "text" in track_types, "Should have text track"
        
        print("✅ Integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False


def cleanup_test_files():
    """Clean up test files"""
    test_path = "/tmp/jianying_assistant"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
        print("Cleaned up test files")


if __name__ == "__main__":
    print("Starting add content tools tests...")
    
    results = []
    results.append(test_add_videos())
    results.append(test_add_audios())
    results.append(test_add_captions())
    results.append(test_add_images())
    results.append(test_add_effects())
    results.append(test_integration())
    
    cleanup_test_files()
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)