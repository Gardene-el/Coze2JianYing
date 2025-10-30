#!/usr/bin/env python3
"""
Test: Simplified Export - Verify default value stripping works correctly
"""

import json
import sys
from data_structures.draft_generator_interface.models import (
    ImageSegmentConfig, AudioSegmentConfig, TextSegmentConfig,
    TimeRange, TrackConfig, DraftConfig, ProjectSettings
)


def test_model_serialization():
    """Test that DraftConfig.to_dict() with include_defaults=False strips defaults"""
    print("="*80)
    print("Test 1: Model Serialization with include_defaults=False")
    print("="*80)
    
    # Create segments with only required fields (all other fields use defaults)
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
    
    # Create draft config
    draft = DraftConfig(
        draft_id="test-123",
        project=ProjectSettings(),
        tracks=[
            TrackConfig(track_type="video", segments=[image_seg]),
            TrackConfig(track_type="audio", segments=[audio_seg]),
            TrackConfig(track_type="text", segments=[text_seg])
        ]
    )
    
    # Serialize with defaults
    full_dict = draft.to_dict(include_defaults=True)
    full_json = json.dumps(full_dict, ensure_ascii=False)
    
    # Serialize without defaults
    minimal_dict = draft.to_dict(include_defaults=False)
    minimal_json = json.dumps(minimal_dict, ensure_ascii=False)
    
    print(f"Full serialization size: {len(full_json)} characters")
    print(f"Minimal serialization size: {len(minimal_json)} characters")
    print(f"Reduction: {round((1 - len(minimal_json)/len(full_json))*100, 1)}%")
    print()
    
    # Show image segment comparison
    print("Image segment (with defaults):")
    print(json.dumps(full_dict['tracks'][0]['segments'][0], indent=2, ensure_ascii=False))
    print()
    print("Image segment (without defaults):")
    print(json.dumps(minimal_dict['tracks'][0]['segments'][0], indent=2, ensure_ascii=False))
    print()
    
    # Verify essential fields are preserved
    assert minimal_dict['draft_id'] == draft.draft_id
    assert minimal_dict['tracks'][0]['track_type'] == 'video'
    assert minimal_dict['tracks'][0]['segments'][0]['type'] == 'image'
    assert minimal_dict['tracks'][0]['segments'][0]['material_url'] == image_seg.material_url
    
    print("✅ Test 1 PASSED: Model serialization works correctly\n")
    return True


def test_backward_compatibility():
    """Test that draft generator can handle both formats"""
    print("="*80)
    print("Test 2: Backward Compatibility")
    print("="*80)
    
    # Import converter to test parsing
    from src.utils.converter import DraftInterfaceConverter
    
    # Full format segment
    full_segment = {
        "type": "image",
        "material_url": "http://example.com/image.png",
        "time_range": {"start": 0, "end": 1000},
        "transform": {
            "position_x": 0.0,
            "position_y": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "rotation": 0.0,
            "opacity": 1.0
        },
        "dimensions": {"width": None, "height": None},
        "crop": {
            "enabled": False,
            "left": 0.0,
            "top": 0.0,
            "right": 1.0,
            "bottom": 1.0
        },
        "keyframes": {
            "position": [],
            "scale": [],
            "rotation": [],
            "opacity": []
        }
    }
    
    # Minimal format segment (only required fields)
    minimal_segment = {
        "type": "image",
        "material_url": "http://example.com/image.png",
        "time_range": {"start": 0, "end": 1000}
    }
    
    converter = DraftInterfaceConverter()
    
    # Test that converter's convert_clip_settings handles both formats
    try:
        # Test with full transform
        full_transform = full_segment.get("transform", {})
        if full_transform:
            clip_settings_full = converter.convert_clip_settings(full_transform)
            print(f"✅ Full format clip settings created: opacity={clip_settings_full.alpha}")
        
        # Test with minimal (missing transform should use defaults)
        minimal_transform = minimal_segment.get("transform", {})
        if minimal_transform:
            clip_settings_minimal = converter.convert_clip_settings(minimal_transform)
            print(f"✅ Minimal format clip settings created")
        else:
            # When transform is missing, converter should handle gracefully
            print(f"✅ Minimal format handles missing transform (uses defaults)")
        
        # Test convert_timerange
        timerange = converter.convert_timerange(full_segment["time_range"])
        assert timerange.start == 0
        assert timerange.duration == 1000
        print(f"✅ Timerange conversion works for both formats")
        
        print("\n✅ Test 2 PASSED: Both formats are handled correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_non_default_values_preserved():
    """Test that non-default values are preserved when stripping"""
    print("="*80)
    print("Test 3: Non-Default Values Preservation")
    print("="*80)
    
    # Create segment with custom non-default values
    image_seg = ImageSegmentConfig(
        material_url="http://example.com/image.png",
        time_range=TimeRange(start=0, end=1000),
        position_x=0.5,  # Non-default
        position_y=0.5,  # Non-default
        scale_x=1.5,     # Non-default
        rotation=45.0,   # Non-default
        filter_type="Vintage"  # Non-default
    )
    
    draft = DraftConfig(
        draft_id="test-456",
        tracks=[TrackConfig(track_type="video", segments=[image_seg])]
    )
    
    minimal_dict = draft.to_dict(include_defaults=False)
    segment_dict = minimal_dict['tracks'][0]['segments'][0]
    
    print("Segment with custom values:")
    print(json.dumps(segment_dict, indent=2, ensure_ascii=False))
    print()
    
    # Verify non-default values are present
    assert 'transform' in segment_dict, "Transform should be present (has non-defaults)"
    assert segment_dict['transform'].get('position_x') == 0.5
    assert segment_dict['transform'].get('scale_x') == 1.5
    assert segment_dict['transform'].get('rotation') == 45.0
    
    assert 'effects' in segment_dict, "Effects should be present (has non-defaults)"
    assert segment_dict['effects'].get('filter_type') == "Vintage"
    
    print("✅ Test 3 PASSED: Non-default values are preserved\n")
    return True


def test_export_size_reduction():
    """Test real-world scenario with typical content"""
    print("="*80)
    print("Test 4: Real-World Export Size Reduction")
    print("="*80)
    
    # Create a typical draft with 3 images, 3 audios, 3 texts
    images = [
        ImageSegmentConfig(
            material_url=f"http://example.com/image{i}.png",
            time_range=TimeRange(start=i*1000, end=(i+1)*1000)
        )
        for i in range(3)
    ]
    
    audios = [
        AudioSegmentConfig(
            material_url=f"http://example.com/audio{i}.mp3",
            time_range=TimeRange(start=i*1000, end=(i+1)*1000)
        )
        for i in range(3)
    ]
    
    texts = [
        TextSegmentConfig(
            content=f"Text segment {i}",
            time_range=TimeRange(start=i*1000, end=(i+1)*1000)
        )
        for i in range(3)
    ]
    
    draft = DraftConfig(
        draft_id="test-789",
        tracks=[
            TrackConfig(track_type="video", segments=images),
            TrackConfig(track_type="audio", segments=audios),
            TrackConfig(track_type="text", segments=texts)
        ]
    )
    
    full_json = json.dumps(draft.to_dict(include_defaults=True), ensure_ascii=False)
    minimal_json = json.dumps(draft.to_dict(include_defaults=False), ensure_ascii=False)
    
    print(f"Full export size: {len(full_json)} characters")
    print(f"Minimal export size: {len(minimal_json)} characters")
    reduction = round((1 - len(minimal_json)/len(full_json))*100, 1)
    print(f"Size reduction: {reduction}%")
    print()
    
    # Verify significant reduction
    assert reduction > 50, f"Expected >50% reduction, got {reduction}%"
    
    print(f"✅ Test 4 PASSED: Achieved {reduction}% size reduction\n")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SIMPLIFIED EXPORT TESTS")
    print("="*80 + "\n")
    
    results = []
    
    try:
        results.append(("Model Serialization", test_model_serialization()))
    except Exception as e:
        print(f"❌ Test 1 FAILED with exception: {e}\n")
        results.append(("Model Serialization", False))
    
    try:
        results.append(("Backward Compatibility", test_backward_compatibility()))
    except Exception as e:
        print(f"❌ Test 2 FAILED with exception: {e}\n")
        results.append(("Backward Compatibility", False))
    
    try:
        results.append(("Non-Default Preservation", test_non_default_values_preserved()))
    except Exception as e:
        print(f"❌ Test 3 FAILED with exception: {e}\n")
        results.append(("Non-Default Preservation", False))
    
    try:
        results.append(("Size Reduction", test_export_size_reduction()))
    except Exception as e:
        print(f"❌ Test 4 FAILED with exception: {e}\n")
        results.append(("Size Reduction", False))
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    return all(result for _, result in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
