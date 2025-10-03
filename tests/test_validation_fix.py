#!/usr/bin/env python3
"""
Simple test to verify the validation logic handles None values correctly
"""

import sys
import os

# Mock Input class to test validation
class MockInput:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Copy the validation function logic here for testing
def validate_input_parameters_fixed(input_data) -> tuple:
    """
    Validate input parameters for create_draft (fixed version)
    """
    # Validate dimensions (handle None values)
    width = getattr(input_data, 'width', None) or 1920
    height = getattr(input_data, 'height', None) or 1080
    if width <= 0 or height <= 0:
        return False, f"Invalid dimensions: {width}x{height}"
    
    # Validate fps (handle None values)
    fps = getattr(input_data, 'fps', None) or 30
    if fps <= 0 or fps > 120:
        return False, f"Invalid fps: {fps}"
    
    return True, ""

def validate_input_parameters_original(input_data) -> tuple:
    """
    Original validation function (without None handling) - for comparison
    """
    width = input_data.width
    height = input_data.height
    if width <= 0 or height <= 0:
        return False, f"Invalid dimensions: {width}x{height}"
    
    fps = input_data.fps
    if fps <= 0 or fps > 120:
        return False, f"Invalid fps: {fps}"
    
    return True, ""
    """
    Original validation function (that would fail)
    """
    # Validate dimensions
    if input_data.width <= 0 or input_data.height <= 0:
        return False, f"Invalid dimensions: {input_data.width}x{input_data.height}"
    
    # Validate fps
    if input_data.fps <= 0 or input_data.fps > 120:
        return False, f"Invalid fps: {input_data.fps}"
    
    return True, ""

def test_validation_functions():
    """Test both validation functions"""
    print("=== Testing validation functions ===")
    
    # Test case 1: Partial parameters (like the user's input)
    print("\n--- Test 1: Partial parameters (width=800, height=600, others=None) ---")
    
    input_partial = MockInput(
        width=800,
        height=600,
        project_name=None,
        fps=None
    )
    
    # Test original function (should fail)
    try:
        is_valid, error_msg = validate_input_parameters_original(input_partial)
        print(f"Original function result: valid={is_valid}, error='{error_msg}'")
    except Exception as e:
        print(f"Original function failed with error: {e}")
    
    # Test fixed function (should succeed)
    try:
        is_valid, error_msg = validate_input_parameters_fixed(input_partial)
        print(f"Fixed function result: valid={is_valid}, error='{error_msg}'")
    except Exception as e:
        print(f"Fixed function failed with error: {e}")
    
    # Test case 2: All parameters provided
    print("\n--- Test 2: All parameters provided ---")
    
    input_complete = MockInput(
        width=1920,
        height=1080,
        project_name="Test Project",
        fps=30
    )
    
    # Test both functions (should both succeed)
    try:
        is_valid, error_msg = validate_input_parameters_original(input_complete)
        print(f"Original function result: valid={is_valid}, error='{error_msg}'")
    except Exception as e:
        print(f"Original function failed with error: {e}")
    
    try:
        is_valid, error_msg = validate_input_parameters_fixed(input_complete)
        print(f"Fixed function result: valid={is_valid}, error='{error_msg}'")
    except Exception as e:
        print(f"Fixed function failed with error: {e}")
    
    # Test case 3: Invalid parameters
    print("\n--- Test 3: Invalid parameters ---")
    
    input_invalid = MockInput(
        width=-100,  # Invalid
        height=600,
        project_name=None,
        fps=None
    )
    
    # Test fixed function with invalid data
    try:
        is_valid, error_msg = validate_input_parameters_fixed(input_invalid)
        print(f"Fixed function with invalid width: valid={is_valid}, error='{error_msg}'")
    except Exception as e:
        print(f"Fixed function failed with error: {e}")

def test_config_creation():
    """Test config creation with None values"""
    print("\n=== Testing config creation logic ===")
    
    input_partial = MockInput(
        width=800,
        height=600,
        project_name=None,
        fps=None
    )
    
    # Simulate the fixed config creation logic
    project_name = getattr(input_partial, 'project_name', None) or "Coze剪映项目"
    width = getattr(input_partial, 'width', None) or 1920
    height = getattr(input_partial, 'height', None) or 1080
    fps = getattr(input_partial, 'fps', None) or 30
    
    config = {
        "project": {
            "name": project_name,
            "width": width,
            "height": height,
            "fps": fps
        }
    }
    
    print("Generated config:")
    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_validation_functions()
    test_config_creation()
    print("\n=== Tests completed ===")
    print("\nThe fix should resolve the 'NoneType' comparison error by providing default values")
    print("when parameters are None instead of trying to compare None with integers.")