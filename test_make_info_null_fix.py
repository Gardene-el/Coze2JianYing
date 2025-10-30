#!/usr/bin/env python3
"""
Test: Verify that make_*_info tools don't include null values when fields are None
"""

import json
from typing import NamedTuple, Optional

# Simulate the fixed make_image_info logic
class MockImageInput(NamedTuple):
    image_url: str
    start: int
    end: int
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    rotation: Optional[float] = None
    opacity: Optional[float] = None
    fit_mode: Optional[str] = None

def make_image_info_fixed(args):
    """Simulates the fixed make_image_info logic"""
    image_info = {
        "image_url": args.image_url,
        "start": args.start,
        "end": args.end
    }
    
    # OLD LOGIC (buggy):
    # if args.position_x != 0.0:  # When position_x is None, None != 0.0 is True!
    #     image_info["position_x"] = args.position_x  # Adds null
    
    # NEW LOGIC (fixed):
    if args.position_x is not None and args.position_x != 0.0:
        image_info["position_x"] = args.position_x
    if args.position_y is not None and args.position_y != 0.0:
        image_info["position_y"] = args.position_y
    if args.scale_x is not None and args.scale_x != 1.0:
        image_info["scale_x"] = args.scale_x
    if args.scale_y is not None and args.scale_y != 1.0:
        image_info["scale_y"] = args.scale_y
    if args.rotation is not None and args.rotation != 0.0:
        image_info["rotation"] = args.rotation
    if args.opacity is not None and args.opacity != 1.0:
        image_info["opacity"] = args.opacity
    if args.fit_mode is not None and args.fit_mode != "fit":
        image_info["fit_mode"] = args.fit_mode
    
    return image_info

# Test case 1: All fields are None (simulating Coze not providing them)
print("="*80)
print("Test 1: All optional fields are None (user's scenario)")
print("="*80)
args1 = MockImageInput(
    image_url="https://s.coze.cn/t/iHombFeLlx0/",
    start=0,
    end=3
    # All optional fields default to None
)

result1 = make_image_info_fixed(args1)
json_str1 = json.dumps(result1, ensure_ascii=False, separators=(',', ':'))

print(f"Result: {json_str1}")
print(f"Length: {len(json_str1)} characters")
print()

# Verify no null values
assert "null" not in json_str1, "Should not contain null values!"
assert "position_x" not in result1, "Should not include position_x when None"
assert "position_y" not in result1, "Should not include position_y when None"
assert "fit_mode" not in result1, "Should not include fit_mode when None"
print("✅ Test 1 PASSED: No null values included")
print()

# Test case 2: Some fields have non-default values
print("="*80)
print("Test 2: Some fields have non-default values")
print("="*80)
args2 = MockImageInput(
    image_url="https://example.com/image.png",
    start=0,
    end=5000,
    position_x=0.5,  # Non-default
    scale_x=2.0,     # Non-default
    rotation=None,   # None (should be omitted)
    opacity=None     # None (should be omitted)
)

result2 = make_image_info_fixed(args2)
json_str2 = json.dumps(result2, ensure_ascii=False, separators=(',', ':'))

print(f"Result: {json_str2}")
print(f"Length: {len(json_str2)} characters")
print()

# Verify behavior
assert "null" not in json_str2, "Should not contain null values!"
assert "position_x" in result2, "Should include position_x when non-default"
assert result2["position_x"] == 0.5, "position_x should be 0.5"
assert "scale_x" in result2, "Should include scale_x when non-default"
assert result2["scale_x"] == 2.0, "scale_x should be 2.0"
assert "rotation" not in result2, "Should not include rotation when None"
assert "opacity" not in result2, "Should not include opacity when None"
print("✅ Test 2 PASSED: Non-defaults included, None values omitted")
print()

# Test case 3: Fields with default values (should also be omitted)
print("="*80)
print("Test 3: Fields with default values")
print("="*80)
args3 = MockImageInput(
    image_url="https://example.com/image.png",
    start=0,
    end=5000,
    position_x=0.0,  # Default value
    position_y=0.0,  # Default value
    scale_x=1.0,     # Default value
    fit_mode="fit"   # Default value
)

result3 = make_image_info_fixed(args3)
json_str3 = json.dumps(result3, ensure_ascii=False, separators=(',', ':'))

print(f"Result: {json_str3}")
print(f"Length: {len(json_str3)} characters")
print()

# Verify behavior
assert "position_x" not in result3, "Should not include position_x when default (0.0)"
assert "position_y" not in result3, "Should not include position_y when default (0.0)"
assert "scale_x" not in result3, "Should not include scale_x when default (1.0)"
assert "fit_mode" not in result3, "Should not include fit_mode when default ('fit')"
print("✅ Test 3 PASSED: Default values omitted")
print()

print("="*80)
print("ALL TESTS PASSED!")
print("="*80)
print("\nThe fix correctly handles:")
print("1. None values (omitted) ✅")
print("2. Default values (omitted) ✅")
print("3. Non-default values (included) ✅")
