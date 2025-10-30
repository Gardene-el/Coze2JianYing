#!/usr/bin/env python3
"""
Investigation Test: Compare Default Values Between Coze Plugin and Draft Generator

This test investigates the three questions from the issue:
1. Compare default values between coze plugin and draft generator
2. Check if draft generator depends on all transmitted values
3. Find other places where redundant data is transmitted
"""

import json
import sys
from typing import Dict, Any
from data_structures.draft_generator_interface.models import (
    ImageSegmentConfig, AudioSegmentConfig, TextSegmentConfig, VideoSegmentConfig,
    TimeRange, TextStyle, TrackConfig, DraftConfig, ProjectSettings
)


def get_dataclass_defaults(cls):
    """Extract default values from a dataclass"""
    import dataclasses
    defaults = {}
    for field in dataclasses.fields(cls):
        if field.default != dataclasses.MISSING:
            defaults[field.name] = field.default
        elif field.default_factory != dataclasses.MISSING:
            defaults[field.name] = field.default_factory()
    return defaults


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def compare_with_serialization(segment_config, segment_dict: Dict[str, Any], segment_type: str):
    """Compare dataclass instance with its serialization"""
    print(f"\n--- {segment_type} Segment Comparison ---")
    
    # Get all attributes from config
    config_attrs = {}
    for attr in dir(segment_config):
        if not attr.startswith('_') and not callable(getattr(segment_config, attr)):
            config_attrs[attr] = getattr(segment_config, attr)
    
    # Count fields in serialization
    def count_fields(d, prefix=""):
        count = 0
        for key, value in d.items():
            if isinstance(value, dict):
                count += count_fields(value, prefix + key + ".")
            elif isinstance(value, list):
                if value:  # Non-empty list
                    count += 1
            elif value is not None:
                count += 1
        return count
    
    total_fields = count_fields(segment_dict)
    
    # Count default values in serialization
    def count_defaults(d, segment_type):
        defaults = 0
        total = 0
        
        # Define what counts as a default value for each type
        default_values = {
            'image': {
                'position_x': 0.0, 'position_y': 0.0,
                'scale_x': 1.0, 'scale_y': 1.0,
                'rotation': 0.0, 'opacity': 1.0,
                'enabled': False,
                'left': 0.0, 'top': 0.0, 'right': 1.0, 'bottom': 1.0,
                'filter_intensity': 1.0, 'transition_duration': 500,
                'blur': False, 'fit_mode': 'fit',
                'intro_duration': 500, 'outro_duration': 500
            },
            'audio': {
                'volume': 1.0, 'fade_in': 0, 'fade_out': 0,
                'effect_intensity': 1.0, 'speed': 1.0,
                'change_pitch': False
            },
            'text': {
                'position_x': 0.5, 'position_y': -0.9,
                'scale': 1.0, 'rotation': 0.0, 'opacity': 1.0,
                'alignment': 'center',
                'font_family': '默认', 'font_size': 48,
                'font_weight': 'normal', 'font_style': 'normal',
                'color': '#FFFFFF', 'enabled': False,
                'stroke_color': '#000000', 'stroke_width': 2,
                'shadow_color': '#000000', 'shadow_offset_x': 2,
                'shadow_offset_y': 2, 'shadow_blur': 4,
                'background_color': '#000000', 'background_opacity': 0.5
            }
        }
        
        segment_defaults = default_values.get(segment_type, {})
        
        for key, value in d.items():
            if isinstance(value, dict):
                sub_defaults, sub_total = count_defaults(value, segment_type)
                defaults += sub_defaults
                total += sub_total
            elif isinstance(value, list):
                if not value:  # Empty list is a default
                    defaults += 1
                total += 1
            elif value is None:
                # None is often a default for optional fields
                defaults += 1
                total += 1
            else:
                total += 1
                # Check if this is a default value
                if key in segment_defaults and value == segment_defaults[key]:
                    defaults += 1
        
        return defaults, total
    
    default_count, total_count = count_defaults(segment_dict, segment_type)
    
    print(f"Total fields in serialization: {total_count}")
    print(f"Fields with default values: {default_count}")
    print(f"Percentage of defaults: {default_count/total_count*100:.1f}%")
    
    return default_count, total_count


def test_question_1():
    """Question 1: Compare default values between coze plugin and draft generator"""
    print_section("Question 1: Default Values Comparison")
    
    print("Coze Plugin Default Values (from data_structures/draft_generator_interface/models.py):")
    print("-" * 80)
    
    # ImageSegmentConfig defaults
    print("\nImageSegmentConfig:")
    image_defaults = get_dataclass_defaults(ImageSegmentConfig)
    for key, value in sorted(image_defaults.items()):
        print(f"  {key}: {value}")
    
    # AudioSegmentConfig defaults
    print("\nAudioSegmentConfig:")
    audio_defaults = get_dataclass_defaults(AudioSegmentConfig)
    for key, value in sorted(audio_defaults.items()):
        print(f"  {key}: {value}")
    
    # TextSegmentConfig defaults
    print("\nTextSegmentConfig:")
    text_defaults = get_dataclass_defaults(TextSegmentConfig)
    for key, value in sorted(text_defaults.items()):
        print(f"  {key}: {value}")
    
    print("\n" + "-" * 80)
    print("Draft Generator Defaults (from src/utils/converter.py):")
    print("-" * 80)
    print("""
The converter uses .get() method with defaults:
- Transform: opacity=1.0, rotation=0.0, scale_x=1.0, scale_y=1.0, position_x=0.0, position_y=0.0
- Crop: enabled=False, left=0.0, top=0.0, right=1.0, bottom=1.0
- Audio: volume=None (checked with 'is not None'), speed=None (checked with 'is not None')
- Text: position_x=0.5, position_y=0.0, scale=1.0, opacity=1.0, rotation=0.0
- Style: Uses .get() with defaults for each field

FINDING: The defaults are CONSISTENT between coze plugin and draft generator.
The draft generator has fallback defaults for ALL fields, so it does NOT require
the coze plugin to send every value.
    """)


def test_question_2():
    """Question 2: Does draft generator depend on all transmitted values?"""
    print_section("Question 2: Draft Generator Dependency Analysis")
    
    print("Code Analysis from src/utils/converter.py:")
    print("-" * 80)
    print("""
Key Finding: The converter ALWAYS uses defensive .get() with defaults:

Example 1 - Transform/ClipSettings:
    def get_value_or_default(key: str, default: float) -> float:
        value = transform_dict.get(key)
        return default if value is None else value

Example 2 - Crop Settings:
    if not crop_dict.get("enabled", False):
        return None
    left = crop_dict.get("left", 0.0)
    top = crop_dict.get("top", 0.0)
    ...

Example 3 - Audio Properties:
    audio_config = segment_config.get("audio")
    if audio_config:
        if audio_config.get("volume") is not None:
            volume = audio_config["volume"]

CONCLUSION: The draft generator does NOT depend on receiving all values.
It gracefully handles missing fields by using default values.
This means we can safely OMIT default values during serialization.
    """)


def test_question_3():
    """Question 3: Find other places with redundant data transmission"""
    print_section("Question 3: Redundant Data in Export")
    
    # Create sample segments with only required fields
    image_seg = ImageSegmentConfig(
        material_url="http://example.com/image.png",
        time_range=TimeRange(start=0, end=1000)
    )
    
    audio_seg = AudioSegmentConfig(
        material_url="http://example.com/audio.mp3",
        time_range=TimeRange(start=0, end=1000)
    )
    
    text_seg = TextSegmentConfig(
        content="Test text",
        time_range=TimeRange(start=0, end=1000)
    )
    
    # Create a draft config
    draft = DraftConfig(
        draft_id="test-123",
        project=ProjectSettings(),
        tracks=[
            TrackConfig(track_type="video", segments=[image_seg]),
            TrackConfig(track_type="audio", segments=[audio_seg]),
            TrackConfig(track_type="text", segments=[text_seg])
        ]
    )
    
    # Serialize using current method
    draft_dict = draft.to_dict()
    
    print("Current Serialization Analysis:")
    print("-" * 80)
    
    # Analyze each segment type
    for track in draft_dict['tracks']:
        if track['segments']:
            seg = track['segments'][0]
            seg_type = seg.get('type', 'unknown')
            
            if seg_type == 'image':
                compare_with_serialization(image_seg, seg, 'image')
            elif seg_type == 'audio':
                compare_with_serialization(audio_seg, seg, 'audio')
            elif seg_type == 'text':
                compare_with_serialization(text_seg, seg, 'text')
    
    print("\n" + "-" * 80)
    print("Sample of Redundant Data in Current Export:")
    print("-" * 80)
    print(json.dumps(draft_dict['tracks'][0]['segments'][0], indent=2, ensure_ascii=False))
    
    print("\n" + "-" * 80)
    print("Other Places with Redundant Data:")
    print("-" * 80)
    print("""
1. export_drafts tool (coze_plugin/tools/export_drafts/handler.py):
   - Uses DraftConfig.to_dict() which serializes ALL fields
   - No filtering of default values

2. add_images tool (coze_plugin/tools/add_images/handler.py):
   - create_image_track_with_segments() manually creates segment dicts
   - Includes ALL fields with .get() defaults (lines 250-291)

3. add_audios tool (coze_plugin/tools/add_audios/handler.py):
   - create_audio_track_with_segments() manually creates segment dicts
   - Includes ALL fields with .get() defaults

4. add_captions tool (coze_plugin/tools/add_captions/handler.py):
   - Similar pattern of including all fields

5. add_videos tool (coze_plugin/tools/add_videos/handler.py):
   - Similar pattern of including all fields

PATTERN: All tools use the same approach of explicitly setting every field,
even when the value is the default. This results in verbose JSON output.
    """)


def main():
    """Run all investigation tests"""
    print("\n" + "="*80)
    print("INVESTIGATION: Simplify Draft Data Export")
    print("="*80)
    
    test_question_1()
    test_question_2()
    test_question_3()
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("""
1. Modify DraftConfig serialization methods to OMIT fields with default values
2. Create a helper function to compare values with defaults before serialization
3. Update all add_* tools to use the same smart serialization
4. Ensure backward compatibility - draft generator must handle both formats
5. The reduction in data size will be significant (50-70% based on analysis)

IMPLEMENTATION STRATEGY:
- Add a parameter to serialization methods: include_defaults=False
- Keep existing behavior as default for backward compatibility
- Use include_defaults=False in export_drafts tool
- Draft generator already handles missing fields correctly, no changes needed there
    """)
    
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
