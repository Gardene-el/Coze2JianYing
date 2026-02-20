#!/usr/bin/env python3
"""
Test script to verify handler generator adaptation to schema refactoring

This script verifies:
1. Base model extraction (ClipSettings, CropSettings, TextStyle, TimeRange)
2. Split request/response schema recognition
3. Position class removal
4. Generated handler syntax validity
5. CustomNamespace type constructor logic
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from handler_generator import SchemaExtractor


def test_base_models():
    """Test that all base models are correctly extracted"""
    print("=" * 60)
    print("TEST 1: Base Models Extraction")
    print("=" * 60)
    
    schema_file = project_root / "app" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    
    base_models = {
        'ClipSettings': 6,  # alpha, rotation, scale_x, scale_y, transform_x, transform_y
        'CropSettings': 8,  # 8 corner coordinates
        'TextStyle': 5,     # font_size, color, bold, italic, underline
        'TimeRange': 2,     # start, duration
    }
    
    passed = 0
    failed = 0
    
    for model, expected_fields in base_models.items():
        if model in extractor.schemas:
            fields = extractor.get_schema_fields(model)
            actual_fields = len(fields)
            
            if actual_fields == expected_fields:
                print(f"✅ {model}: {actual_fields} fields")
                passed += 1
            else:
                print(f"❌ {model}: {actual_fields} fields (expected {expected_fields})")
                failed += 1
        else:
            print(f"❌ {model}: NOT FOUND")
            failed += 1
    
    print(f"\nResult: {passed}/{len(base_models)} passed")
    return failed == 0


def test_split_schemas():
    """Test that all split request schemas are recognized"""
    print("\n" + "=" * 60)
    print("TEST 2: Split Request Schemas Recognition")
    print("=" * 60)
    
    schema_file = project_root / "app" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    
    split_requests = [
        'AddAudioEffectRequest',
        'AddVideoEffectRequest',
        'AddAudioFadeRequest',
        'AddVideoFadeRequest',
        'AddAudioKeyframeRequest',
        'AddVideoKeyframeRequest',
        'AddTextKeyframeRequest',
        'AddStickerKeyframeRequest',
        'AddVideoAnimationRequest',
        'AddTextAnimationRequest',
        'AddVideoFilterRequest',
        'AddVideoMaskRequest',
        'AddVideoTransitionRequest',
        'AddVideoBackgroundFillingRequest',
        'AddTextBubbleRequest',
    ]
    
    found = 0
    missing = 0
    
    for schema in split_requests:
        if schema in extractor.schemas:
            print(f"✅ {schema}")
            found += 1
        else:
            print(f"❌ {schema}: NOT FOUND")
            missing += 1
    
    print(f"\nResult: {found}/{len(split_requests)} found")
    return missing == 0


def test_position_removal():
    """Test that Position class has been removed"""
    print("\n" + "=" * 60)
    print("TEST 3: Position Class Removal")
    print("=" * 60)
    
    schema_file = project_root / "app" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    
    if 'Position' not in extractor.schemas:
        print("✅ Position class correctly removed from schemas")
        return True
    else:
        print("❌ Position class still exists in schemas!")
        return False


def test_generated_handlers():
    """Test that generated handlers have valid syntax"""
    print("\n" + "=" * 60)
    print("TEST 4: Generated Handler Syntax Validation")
    print("=" * 60)
    
    handlers_to_check = [
        'create_text_segment',
        'create_video_segment',
        'add_audio_effect',
        'add_video_effect',
        'add_audio_keyframe',
        'add_video_keyframe',
        'add_text_keyframe',
        'add_sticker_keyframe',
    ]
    
    raw_tools_dir = project_root / "coze_plugin" / "raw_tools"
    
    passed = 0
    failed = 0
    
    for handler_name in handlers_to_check:
        handler_path = raw_tools_dir / handler_name / "handler.py"
        
        if handler_path.exists():
            try:
                with open(handler_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(handler_path), 'exec')
                print(f"✅ {handler_name}: Valid syntax")
                passed += 1
            except SyntaxError as e:
                print(f"❌ {handler_name}: Syntax error - {e}")
                failed += 1
        else:
            print(f"❌ {handler_name}: File not found")
            failed += 1
    
    print(f"\nResult: {passed}/{len(handlers_to_check)} passed")
    return failed == 0


def test_type_constructor_logic():
    """Test that type constructor logic handles new types"""
    print("\n" + "=" * 60)
    print("TEST 5: Type Constructor Logic")
    print("=" * 60)
    
    raw_tools_dir = project_root / "coze_plugin" / "raw_tools"
    handler_path = raw_tools_dir / "create_text_segment" / "handler.py"
    
    if not handler_path.exists():
        print("❌ create_text_segment handler not found")
        return False
    
    with open(handler_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'ClipSettings': 'clip_settings' in content.lower(),
        'CropSettings': 'crop_settings' in content.lower() or 'CropSettings' in content,
        'TextStyle': 'text_style' in content.lower(),
        'TimeRange': 'timerange' in content.lower(),
        'Position removed': 'Position class was removed' in content,
    }
    
    passed = 0
    failed = 0
    
    for check_name, result in checks.items():
        if result:
            print(f"✅ {check_name}")
            passed += 1
        else:
            print(f"❌ {check_name}")
            failed += 1
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return failed == 0


def main():
    """Run all tests"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Schema Adaptation Test Suite" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Base Models", test_base_models()))
    results.append(("Split Schemas", test_split_schemas()))
    results.append(("Position Removal", test_position_removal()))
    results.append(("Handler Syntax", test_generated_handlers()))
    results.append(("Type Constructor", test_type_constructor_logic()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} test suites passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Handler generator successfully adapted.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
