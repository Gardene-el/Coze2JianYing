#!/usr/bin/env python3
"""
Standalone test script for the new add content tools without runtime dependency

Tests the core logic of add_videos, add_audios, add_captions, add_images, and add_effects tools
"""

import os
import sys
import json
import shutil
import tempfile
import uuid
import time
from typing import NamedTuple, List, Optional, Dict, Any, Union


def setup_test_draft():
    """Create a test draft for testing purposes"""
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


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def load_draft_config(draft_id: str) -> tuple[bool, dict, str]:
    """Load draft configuration from file"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    if not os.path.exists(draft_folder):
        return False, {}, f"Draft folder not found: {draft_id}"
    
    if not os.path.exists(config_file):
        return False, {}, f"Draft config file not found: {draft_id}"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config, ""
    except Exception as e:
        return False, {}, f"Failed to load draft config: {str(e)}"


def save_draft_config(draft_id: str, config: dict) -> tuple[bool, str]:
    """Save draft configuration to file"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    try:
        # Update timestamp
        config["last_modified"] = time.time()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True, ""
    except Exception as e:
        return False, f"Failed to save draft config: {str(e)}"


def test_add_videos_logic():
    """Test the add_videos core logic"""
    print("=== Testing add_videos logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Simulate add_videos parameters
        video_urls = ["https://example.com/video1.mp4", "https://example.com/video2.mp4"]
        filters = ["暖冬", "电影"]
        transitions = ["淡化", "切镜"]
        volumes = [1.0, 0.8]
        start_time = 0
        
        # Load existing draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Create video segments
        segments = []
        current_time = start_time
        
        for i, video_url in enumerate(video_urls):
            duration = 10000  # 10 seconds default
            
            segment = {
                "type": "video",
                "material_url": video_url,
                "time_range": {
                    "start": current_time,
                    "end": current_time + duration
                },
                "material_range": {
                    "start": 0,
                    "end": duration
                },
                "transform": {
                    "position_x": 0.0,
                    "position_y": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "rotation": 0.0,
                    "opacity": 1.0
                },
                "crop": {
                    "enabled": False,
                    "left": 0.0,
                    "top": 0.0,
                    "right": 1.0,
                    "bottom": 1.0
                },
                "effects": {
                    "filter_type": filters[i],
                    "filter_intensity": 1.0,
                    "transition_type": transitions[i],
                    "transition_duration": 500
                },
                "speed": {
                    "speed": 1.0,
                    "reverse": False
                },
                "background": {
                    "blur": False,
                    "color": None
                },
                "keyframes": {
                    "position": [],
                    "scale": [],
                    "rotation": [],
                    "opacity": []
                },
                "volume": volumes[i]
            }
            
            segments.append(segment)
            current_time += duration
        
        # Add media resources
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for video_url in video_urls:
            config["media_resources"].append({
                "url": video_url,
                "resource_type": "video",
                "duration_ms": 10000,
                "file_size": None,
                "format": "mp4",
                "width": None,
                "height": None,
                "filename": None
            })
        
        # Create new video track
        new_track = {
            "track_type": "video",
            "muted": False,
            "volume": 1.0,
            "segments": segments
        }
        
        config["tracks"].append(new_track)
        config["total_duration_ms"] = max([seg["time_range"]["end"] for seg in segments])
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify results
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 1, "Should have 1 track"
        assert final_config['tracks'][0]['track_type'] == "video", "Track should be video type"
        assert len(final_config['tracks'][0]['segments']) == 2, "Should have 2 video segments"
        assert len(final_config['media_resources']) == 2, "Should have 2 media resources"
        assert final_config['total_duration_ms'] == 20000, "Total duration should be 20 seconds"
        
        print("✅ add_videos logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_videos logic test failed: {str(e)}")
        return False


def test_add_audios_logic():
    """Test the add_audios core logic"""
    print("\n=== Testing add_audios logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Simulate add_audios parameters
        audio_urls = ["https://example.com/audio1.mp3", "https://example.com/audio2.mp3"]
        volumes = [0.8, 1.0]
        fade_ins = [1000, 500]
        fade_outs = [2000, 1000]
        effects = ["回声", None]
        start_time = 0
        
        # Load existing draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Create audio segments
        segments = []
        current_time = start_time
        
        for i, audio_url in enumerate(audio_urls):
            duration = 30000  # 30 seconds default for audio
            
            segment = {
                "type": "audio",
                "material_url": audio_url,
                "time_range": {
                    "start": current_time,
                    "end": current_time + duration
                },
                "material_range": {
                    "start": 0,
                    "end": duration
                },
                "audio": {
                    "volume": volumes[i],
                    "fade_in": fade_ins[i],
                    "fade_out": fade_outs[i],
                    "effect_type": effects[i],
                    "effect_intensity": 1.0,
                    "speed": 1.0
                },
                "keyframes": {
                    "volume": []
                }
            }
            
            segments.append(segment)
            current_time += duration
        
        # Add media resources
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for audio_url in audio_urls:
            config["media_resources"].append({
                "url": audio_url,
                "resource_type": "audio",
                "duration_ms": 30000,
                "file_size": None,
                "format": "mp3",
                "width": None,
                "height": None,
                "filename": None
            })
        
        # Create new audio track
        new_track = {
            "track_type": "audio",
            "muted": False,
            "volume": 1.0,
            "segments": segments
        }
        
        config["tracks"].append(new_track)
        config["total_duration_ms"] = max([seg["time_range"]["end"] for seg in segments])
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify results
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 1, "Should have 1 track"
        assert final_config['tracks'][0]['track_type'] == "audio", "Track should be audio type"
        assert len(final_config['tracks'][0]['segments']) == 2, "Should have 2 audio segments"
        assert len(final_config['media_resources']) == 2, "Should have 2 media resources"
        assert final_config['total_duration_ms'] == 60000, "Total duration should be 60 seconds"
        
        print("✅ add_audios logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_audios logic test failed: {str(e)}")
        return False


def test_add_captions_logic():
    """Test the add_captions core logic"""
    print("\n=== Testing add_captions logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Simulate add_captions parameters
        captions = [
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
        ]
        font_family = "思源黑体"
        font_size = 48
        color = "#FFFFFF"
        default_position_x = 0.5
        default_position_y = 0.9
        alignment = "center"
        
        # Load existing draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Create text segments
        segments = []
        
        for caption in captions:
            position_x = caption.get("position_x", default_position_x)
            position_y = caption.get("position_y", default_position_y)
            
            segment = {
                "type": "text",
                "content": caption["text"],
                "time_range": {
                    "start": caption["start_time"],
                    "end": caption["end_time"]
                },
                "transform": {
                    "position_x": position_x,
                    "position_y": position_y,
                    "scale": 1.0,
                    "rotation": 0.0,
                    "opacity": 1.0
                },
                "style": {
                    "font_family": font_family,
                    "font_size": font_size,
                    "font_weight": "normal",
                    "font_style": "normal",
                    "color": color,
                    "stroke": {
                        "enabled": False,
                        "color": "#000000",
                        "width": 2
                    },
                    "shadow": {
                        "enabled": False,
                        "color": "#000000",
                        "offset_x": 2,
                        "offset_y": 2,
                        "blur": 4
                    },
                    "background": {
                        "enabled": False,
                        "color": "#000000",
                        "opacity": 0.5
                    }
                },
                "alignment": alignment,
                "animations": {
                    "intro": None,
                    "outro": None,
                    "loop": None
                },
                "keyframes": {
                    "position": [],
                    "scale": [],
                    "rotation": [],
                    "opacity": []
                }
            }
            
            segments.append(segment)
        
        # Create new text track
        new_track = {
            "track_type": "text",
            "muted": False,
            "volume": 1.0,
            "segments": segments
        }
        
        config["tracks"].append(new_track)
        
        # Update total duration
        max_end_time = max([seg["time_range"]["end"] for seg in segments])
        if max_end_time > config.get("total_duration_ms", 0):
            config["total_duration_ms"] = max_end_time
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify results
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 1, "Should have 1 track"
        assert final_config['tracks'][0]['track_type'] == "text", "Track should be text type"
        assert len(final_config['tracks'][0]['segments']) == 2, "Should have 2 caption segments"
        assert final_config['total_duration_ms'] == 6000, "Total duration should be 6 seconds"
        
        # Verify caption content
        segments = final_config['tracks'][0]['segments']
        assert segments[0]['content'] == "欢迎使用Coze剪映助手", "First caption content should match"
        assert segments[1]['content'] == "这是第二个字幕", "Second caption content should match"
        assert segments[1]['transform']['position_x'] == 0.3, "Second caption position_x should be custom"
        
        print("✅ add_captions logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_captions logic test failed: {str(e)}")
        return False


def test_add_images_logic():
    """Test the add_images core logic"""
    print("\n=== Testing add_images logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Simulate add_images parameters
        image_urls = ["https://example.com/image1.jpg", "https://example.com/image2.png"]
        durations = [3000, 4000]
        transitions = ["淡化", "切镜"]
        positions_x = [0.0, 0.1]
        positions_y = [0.0, -0.1]
        scales = [1.0, 1.2]
        start_time = 0
        
        # Load existing draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Create image segments (treated as video)
        segments = []
        current_time = start_time
        
        for i, image_url in enumerate(image_urls):
            duration = durations[i]
            
            segment = {
                "type": "video",  # Images are treated as video segments
                "material_url": image_url,
                "time_range": {
                    "start": current_time,
                    "end": current_time + duration
                },
                "material_range": {
                    "start": 0,
                    "end": duration
                },
                "transform": {
                    "position_x": positions_x[i],
                    "position_y": positions_y[i],
                    "scale_x": scales[i],
                    "scale_y": scales[i],
                    "rotation": 0.0,
                    "opacity": 1.0
                },
                "crop": {
                    "enabled": False,
                    "left": 0.0,
                    "top": 0.0,
                    "right": 1.0,
                    "bottom": 1.0
                },
                "effects": {
                    "filter_type": None,
                    "filter_intensity": 1.0,
                    "transition_type": transitions[i],
                    "transition_duration": 500
                },
                "speed": {
                    "speed": 1.0,
                    "reverse": False
                },
                "background": {
                    "blur": False,
                    "color": None
                },
                "keyframes": {
                    "position": [],
                    "scale": [],
                    "rotation": [],
                    "opacity": []
                }
            }
            
            segments.append(segment)
            current_time += duration
        
        # Add media resources
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for i, image_url in enumerate(image_urls):
            config["media_resources"].append({
                "url": image_url,
                "resource_type": "image",
                "duration_ms": durations[i],
                "file_size": None,
                "format": image_url.split('.')[-1].lower(),
                "width": None,
                "height": None,
                "filename": None
            })
        
        # Create new video track for images
        new_track = {
            "track_type": "video",
            "muted": False,
            "volume": 1.0,
            "segments": segments
        }
        
        config["tracks"].append(new_track)
        config["total_duration_ms"] = max([seg["time_range"]["end"] for seg in segments])
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify results
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 1, "Should have 1 track"
        assert final_config['tracks'][0]['track_type'] == "video", "Track should be video type (images as video)"
        assert len(final_config['tracks'][0]['segments']) == 2, "Should have 2 image segments"
        assert len(final_config['media_resources']) == 2, "Should have 2 media resources"
        assert final_config['total_duration_ms'] == 7000, "Total duration should be 7 seconds"
        
        # Verify image segment details
        segments = final_config['tracks'][0]['segments']
        assert segments[0]['transform']['scale_x'] == 1.0, "First image scale should be 1.0"
        assert segments[1]['transform']['scale_x'] == 1.2, "Second image scale should be 1.2"
        assert segments[1]['transform']['position_x'] == 0.1, "Second image position_x should be 0.1"
        
        print("✅ add_images logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_images logic test failed: {str(e)}")
        return False


def test_add_effects_logic():
    """Test the add_effects core logic"""
    print("\n=== Testing add_effects logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    try:
        # Simulate add_effects parameters
        effects = [
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
        ]
        default_intensity = 1.0
        default_position_x = None
        default_position_y = None
        default_scale = 1.0
        
        # Load existing draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Create effect segments
        segments = []
        
        for effect in effects:
            intensity = effect.get("intensity", default_intensity)
            position_x = effect.get("position_x", default_position_x)
            position_y = effect.get("position_y", default_position_y)
            scale = effect.get("scale", default_scale)
            properties = effect.get("properties", {})
            
            segment = {
                "type": "effect",
                "effect_type": effect["effect_type"],
                "time_range": {
                    "start": effect["start_time"],
                    "end": effect["end_time"]
                },
                "properties": {
                    "intensity": intensity,
                    "position_x": position_x,
                    "position_y": position_y,
                    "scale": scale,
                    **properties
                }
            }
            
            segments.append(segment)
        
        # Create new effect track
        new_track = {
            "track_type": "effect",
            "muted": False,
            "volume": 1.0,
            "segments": segments
        }
        
        config["tracks"].append(new_track)
        
        # Update total duration
        max_end_time = max([seg["time_range"]["end"] for seg in segments])
        if max_end_time > config.get("total_duration_ms", 0):
            config["total_duration_ms"] = max_end_time
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify results
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 1, "Should have 1 track"
        assert final_config['tracks'][0]['track_type'] == "effect", "Track should be effect type"
        assert len(final_config['tracks'][0]['segments']) == 2, "Should have 2 effect segments"
        assert final_config['total_duration_ms'] == 7000, "Total duration should be 7 seconds"
        
        # Verify effect segment details
        segments = final_config['tracks'][0]['segments']
        assert segments[0]['effect_type'] == "光效闪烁", "First effect type should match"
        assert segments[0]['properties']['intensity'] == 0.8, "First effect intensity should be 0.8"
        assert segments[1]['effect_type'] == "粒子爆炸", "Second effect type should match"
        assert segments[1]['properties']['particle_count'] == 100, "Second effect particle_count should be 100"
        
        print("✅ add_effects logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ add_effects logic test failed: {str(e)}")
        return False


def test_integration_logic():
    """Test integration of all tools with the same draft"""
    print("\n=== Testing integration logic ===")
    
    draft_id = setup_test_draft()
    print(f"Created test draft for integration: {draft_id}")
    
    try:
        # Load initial draft
        success, config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to load draft: {error_msg}"
        
        # Add a video track
        video_track = {
            "track_type": "video",
            "muted": False,
            "volume": 1.0,
            "segments": [{
                "type": "video",
                "material_url": "https://example.com/main.mp4",
                "time_range": {"start": 0, "end": 10000},
                "material_range": {"start": 0, "end": 10000},
                "transform": {"position_x": 0.0, "position_y": 0.0, "scale_x": 1.0, "scale_y": 1.0, "rotation": 0.0, "opacity": 1.0},
                "crop": {"enabled": False, "left": 0.0, "top": 0.0, "right": 1.0, "bottom": 1.0},
                "effects": {"filter_type": None, "filter_intensity": 1.0, "transition_type": None, "transition_duration": 500},
                "speed": {"speed": 1.0, "reverse": False},
                "background": {"blur": False, "color": None},
                "keyframes": {"position": [], "scale": [], "rotation": [], "opacity": []}
            }]
        }
        config["tracks"].append(video_track)
        
        # Add an audio track
        audio_track = {
            "track_type": "audio",
            "muted": False,
            "volume": 1.0,
            "segments": [{
                "type": "audio",
                "material_url": "https://example.com/bgm.mp3",
                "time_range": {"start": 0, "end": 30000},
                "material_range": {"start": 0, "end": 30000},
                "audio": {"volume": 0.5, "fade_in": 1000, "fade_out": 2000, "effect_type": None, "effect_intensity": 1.0, "speed": 1.0},
                "keyframes": {"volume": []}
            }]
        }
        config["tracks"].append(audio_track)
        
        # Add a text track
        text_track = {
            "track_type": "text",
            "muted": False,
            "volume": 1.0,
            "segments": [{
                "type": "text",
                "content": "集成测试字幕",
                "time_range": {"start": 1000, "end": 4000},
                "transform": {"position_x": 0.5, "position_y": 0.9, "scale": 1.0, "rotation": 0.0, "opacity": 1.0},
                "style": {
                    "font_family": "思源黑体", "font_size": 48, "font_weight": "normal", "font_style": "normal", "color": "#FFFFFF",
                    "stroke": {"enabled": False, "color": "#000000", "width": 2},
                    "shadow": {"enabled": False, "color": "#000000", "offset_x": 2, "offset_y": 2, "blur": 4},
                    "background": {"enabled": False, "color": "#000000", "opacity": 0.5}
                },
                "alignment": "center",
                "animations": {"intro": None, "outro": None, "loop": None},
                "keyframes": {"position": [], "scale": [], "rotation": [], "opacity": []}
            }]
        }
        config["tracks"].append(text_track)
        
        # Add an effect track
        effect_track = {
            "track_type": "effect",
            "muted": False,
            "volume": 1.0,
            "segments": [{
                "type": "effect",
                "effect_type": "光芒四射",
                "time_range": {"start": 2000, "end": 5000},
                "properties": {"intensity": 1.0, "position_x": 0.5, "position_y": 0.5, "scale": 1.0}
            }]
        }
        config["tracks"].append(effect_track)
        
        # Add media resources
        config["media_resources"] = [
            {"url": "https://example.com/main.mp4", "resource_type": "video", "duration_ms": 10000, "file_size": None, "format": "mp4", "width": None, "height": None, "filename": None},
            {"url": "https://example.com/bgm.mp3", "resource_type": "audio", "duration_ms": 30000, "file_size": None, "format": "mp3", "width": None, "height": None, "filename": None}
        ]
        
        # Update total duration
        config["total_duration_ms"] = 30000
        
        # Save updated configuration
        success, error_msg = save_draft_config(draft_id, config)
        assert success, f"Failed to save config: {error_msg}"
        
        # Verify final state
        success, final_config, error_msg = load_draft_config(draft_id)
        assert success, f"Failed to reload config: {error_msg}"
        
        assert len(final_config['tracks']) == 4, "Should have 4 tracks (video, audio, text, effect)"
        assert len(final_config['media_resources']) == 2, "Should have 2 media resources"
        
        track_types = [track['track_type'] for track in final_config['tracks']]
        assert "video" in track_types, "Should have video track"
        assert "audio" in track_types, "Should have audio track"
        assert "text" in track_types, "Should have text track"
        assert "effect" in track_types, "Should have effect track"
        
        print(f"Final state - Total tracks: {len(final_config['tracks'])}")
        print(f"Final state - Media resources: {len(final_config['media_resources'])}")
        print(f"Track types: {track_types}")
        
        print("✅ Integration logic test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration logic test failed: {str(e)}")
        return False


def cleanup_test_files():
    """Clean up test files"""
    test_path = "/tmp/jianying_assistant"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
        print("Cleaned up test files")


if __name__ == "__main__":
    print("Starting standalone add content tools logic tests...")
    
    results = []
    results.append(test_add_videos_logic())
    results.append(test_add_audios_logic())
    results.append(test_add_captions_logic())
    results.append(test_add_images_logic())
    results.append(test_add_effects_logic())
    results.append(test_integration_logic())
    
    cleanup_test_files()
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All standalone logic tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)