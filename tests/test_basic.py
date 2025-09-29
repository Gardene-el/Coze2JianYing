#!/usr/bin/env python3
"""
Basic test to verify data structures and file creation
"""

import sys
import os
import json
import uuid
import time

# Test the data structures
def test_data_structures():
    """Test the draft generator interface data structures"""
    print("=== Testing data structures ===")
    
    sys.path.insert(0, '.')
    from data_structures.draft_generator_interface.models import (
        DraftConfig, ProjectSettings, MediaResource, TrackConfig,
        VideoSegmentConfig, TimeRange, TextSegmentConfig, TextStyle
    )
    
    # Create a test draft configuration
    project = ProjectSettings(
        name="测试项目",
        width=1920,
        height=1080,
        fps=30
    )
    
    # Create media resources
    media_resources = [
        MediaResource(
            url="https://example.com/video1.mp4",
            resource_type="video",
            duration_ms=30000,
            format="mp4"
        ),
        MediaResource(
            url="https://example.com/audio1.mp3",
            resource_type="audio",
            duration_ms=45000,
            format="mp3"
        )
    ]
    
    # Create video segment
    video_segment = VideoSegmentConfig(
        material_url="https://example.com/video1.mp4",
        time_range=TimeRange(start=0, end=30000),
        filter_type="暖冬",
        filter_intensity=0.8
    )
    
    # Create text segment
    text_style = TextStyle(
        font_family="思源黑体",
        font_size=48,
        color="#FFFFFF"
    )
    
    text_segment = TextSegmentConfig(
        content="测试字幕",
        time_range=TimeRange(start=5000, end=10000),
        style=text_style
    )
    
    # Create tracks
    video_track = TrackConfig(
        track_type="video",
        segments=[video_segment]
    )
    
    text_track = TrackConfig(
        track_type="text",
        segments=[text_segment]
    )
    
    # Create complete draft config
    draft_config = DraftConfig(
        project=project,
        media_resources=media_resources,
        tracks=[video_track, text_track],
        total_duration_ms=30000,
        created_timestamp=time.time(),
        last_modified=time.time()
    )
    
    # Test serialization
    draft_dict = draft_config.to_dict()
    json_str = json.dumps(draft_dict, ensure_ascii=False, indent=2)
    
    print(f"Draft config created successfully!")
    print(f"Draft ID: {draft_config.draft_id}")
    print(f"JSON size: {len(json_str)} characters")
    print(f"JSON preview:\n{json_str[:500]}...")
    
    return draft_config, json_str

def test_file_operations():
    """Test basic file operations similar to the tools"""
    print("\n=== Testing file operations ===")
    
    # Create a test draft ID
    test_draft_id = str(uuid.uuid4())
    draft_folder = f"/tmp/{test_draft_id}"
    
    try:
        # Create draft folder
        os.makedirs(draft_folder, exist_ok=True)
        print(f"Created draft folder: {draft_folder}")
        
        # Create test config
        test_config = {
            "draft_id": test_draft_id,
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
        
        # Save config to file
        config_file = os.path.join(draft_folder, "draft_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        
        print(f"Created config file: {config_file}")
        
        # Read config back
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        print(f"Config loaded successfully!")
        print(f"Loaded draft ID: {loaded_config['draft_id']}")
        print(f"Project name: {loaded_config['project']['name']}")
        
        # Test export format
        export_data = {
            "format_version": "1.0",
            "export_type": "single_draft",
            "draft_count": 1,
            "drafts": [loaded_config]
        }
        
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
        print(f"Export JSON created, size: {len(export_json)} characters")
        
        # Clean up
        import shutil
        shutil.rmtree(draft_folder)
        print(f"Cleaned up test files")
        
        return test_draft_id, export_json
        
    except Exception as e:
        print(f"File operation error: {e}")
        # Try to clean up on error
        if os.path.exists(draft_folder):
            import shutil
            shutil.rmtree(draft_folder)
        return None, None

def test_validation():
    """Test validation functions"""
    print("\n=== Testing validation ===")
    
    # Test UUID validation
    valid_uuid = str(uuid.uuid4())
    invalid_uuid = "not-a-uuid"
    
    def validate_uuid_format(uuid_str):
        try:
            uuid.UUID(uuid_str)
            return True
        except (ValueError, TypeError):
            return False
    
    print(f"Valid UUID '{valid_uuid}': {validate_uuid_format(valid_uuid)}")
    print(f"Invalid UUID '{invalid_uuid}': {validate_uuid_format(invalid_uuid)}")
    
    # Test parameter validation
    def validate_dimensions(width, height):
        return width > 0 and height > 0
    
    def validate_fps(fps):
        return 0 < fps <= 120
    
    def validate_color(color):
        return color.startswith('#') and len(color) == 7
    
    test_cases = [
        ("dimensions", (1920, 1080), validate_dimensions),
        ("dimensions", (-1, 1080), validate_dimensions),
        ("fps", (30,), validate_fps),
        ("fps", (150,), validate_fps),
        ("color", ("#000000",), validate_color),
        ("color", ("black",), validate_color),
    ]
    
    for name, args, validator in test_cases:
        result = validator(*args)
        print(f"Validate {name} {args}: {result}")

if __name__ == "__main__":
    try:
        print("Starting basic tests...")
        
        # Test data structures
        draft_config, json_str = test_data_structures()
        
        # Test file operations
        draft_id, export_json = test_file_operations()
        
        # Test validation
        test_validation()
        
        print("\n=== All basic tests completed successfully ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()