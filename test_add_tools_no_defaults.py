#!/usr/bin/env python3
"""
Test: Verify that add_* tools don't add back defaults that make_*_info omitted
"""

import json
import sys
sys.path.insert(0, '/home/runner/work/Coze2JianYing/Coze2JianYing')

from coze_plugin.tools.add_audios.handler import create_audio_track_with_segments
from coze_plugin.tools.add_images.handler import create_image_track_with_segments
from coze_plugin.tools.add_captions.handler import create_caption_track_with_segments


def test_audio_no_defaults():
    """Test that audio segments don't include defaults"""
    print("\n=== Test 1: Audio Segments (Minimal) ===")
    
    # This is what make_audio_info would produce (only required fields)
    audio_infos = [{
        "audio_url": "http://example.com/audio.mp3",
        "start": 0,
        "end": 10000
    }]
    
    _, _, track = create_audio_track_with_segments(audio_infos)
    segment = track['segments'][0]
    
    # Should only have base fields
    expected_keys = {'id', 'type', 'material_url', 'time_range'}
    actual_keys = set(segment.keys())
    
    print(f"Expected keys: {expected_keys}")
    print(f"Actual keys: {actual_keys}")
    print(f"Segment JSON: {json.dumps(segment, indent=2, ensure_ascii=False)}")
    
    # Should NOT have audio, keyframes, or material_range if not specified
    assert 'audio' not in segment, "Should not include 'audio' dict with defaults"
    assert 'keyframes' not in segment, "Should not include empty 'keyframes'"
    assert 'material_range' not in segment, "Should not include null 'material_range'"
    
    # Track should not have muted/volume defaults
    assert 'muted' not in track, "Track should not include 'muted' default"
    assert 'volume' not in track, "Track should not include 'volume' default"
    
    print("✅ Audio test passed - no defaults added")
    return True


def test_audio_with_custom_values():
    """Test that audio segments include non-default values"""
    print("\n=== Test 2: Audio Segments (With Custom Values) ===")
    
    # This is what make_audio_info would produce with custom values
    audio_infos = [{
        "audio_url": "http://example.com/audio.mp3",
        "start": 0,
        "end": 10000,
        "volume": 0.5,  # Non-default
        "fade_in": 500  # Non-default
    }]
    
    _, _, track = create_audio_track_with_segments(audio_infos)
    segment = track['segments'][0]
    
    print(f"Segment JSON: {json.dumps(segment, indent=2, ensure_ascii=False)}")
    
    # Should have audio dict with specified values
    assert 'audio' in segment, "Should include 'audio' dict when values specified"
    assert segment['audio']['volume'] == 0.5, "Should preserve custom volume"
    assert segment['audio']['fade_in'] == 500, "Should preserve custom fade_in"
    
    # But should not include other defaults
    assert 'fade_out' not in segment['audio'], "Should not include fade_out default (0)"
    assert 'speed' not in segment['audio'], "Should not include speed default (1.0)"
    
    print("✅ Audio custom values test passed")
    return True


def test_image_no_defaults():
    """Test that image segments don't include defaults"""
    print("\n=== Test 3: Image Segments (Minimal) ===")
    
    # This is what make_image_info would produce (only required fields)
    image_infos = [{
        "image_url": "http://example.com/image.png",
        "start": 0,
        "end": 10000
    }]
    
    _, _, track = create_image_track_with_segments(image_infos)
    segment = track['segments'][0]
    
    print(f"Segment JSON: {json.dumps(segment, indent=2, ensure_ascii=False)}")
    
    # Should only have base fields
    expected_keys = {'id', 'type', 'material_url', 'time_range'}
    actual_keys = set(segment.keys())
    
    # Should NOT have transform, dimensions, crop, effects, etc. if not specified
    assert 'transform' not in segment, "Should not include 'transform' with defaults"
    assert 'dimensions' not in segment, "Should not include 'dimensions' with nulls"
    assert 'crop' not in segment, "Should not include 'crop' when not enabled"
    assert 'effects' not in segment, "Should not include 'effects' with defaults"
    assert 'background' not in segment, "Should not include 'background' with defaults"
    assert 'animations' not in segment, "Should not include 'animations' with defaults"
    assert 'keyframes' not in segment, "Should not include empty 'keyframes'"
    
    print("✅ Image test passed - no defaults added")
    return True


def test_caption_no_defaults():
    """Test that caption segments don't include defaults"""
    print("\n=== Test 4: Caption Segments (Minimal) ===")
    
    # This is what make_caption_info would produce (only required fields)
    caption_infos = [{
        "content": "Test caption",
        "start": 0,
        "end": 10000
    }]
    
    _, _, track = create_caption_track_with_segments(caption_infos)
    segment = track['segments'][0]
    
    print(f"Segment JSON: {json.dumps(segment, indent=2, ensure_ascii=False)}")
    
    # Should only have base fields
    expected_keys = {'id', 'type', 'content', 'time_range'}
    actual_keys = set(segment.keys())
    
    # Should NOT have transform, style, alignment, animations, keyframes if not specified
    assert 'transform' not in segment, "Should not include 'transform' with defaults"
    assert 'style' not in segment, "Should not include 'style' with defaults"
    assert 'alignment' not in segment, "Should not include 'alignment' default"
    assert 'animations' not in segment, "Should not include 'animations' with nulls"
    assert 'keyframes' not in segment, "Should not include empty 'keyframes'"
    
    print("✅ Caption test passed - no defaults added")
    return True


def main():
    print("\n" + "="*80)
    print("Testing: add_* tools respect make_*_info default omission")
    print("="*80)
    
    results = []
    
    try:
        results.append(test_audio_no_defaults())
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        results.append(False)
    
    try:
        results.append(test_audio_with_custom_values())
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        results.append(False)
    
    try:
        results.append(test_image_no_defaults())
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        results.append(False)
    
    try:
        results.append(test_caption_no_defaults())
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        results.append(False)
    
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {sum(results)}/{len(results)} passed")
    print("="*80 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
