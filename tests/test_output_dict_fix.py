#!/usr/bin/env python3
"""
Test script to verify the Output type fix for create_draft and export_drafts

This test verifies that:
1. create_draft returns a dict instead of NamedTuple
2. export_drafts returns a dict instead of NamedTuple
3. The returned dicts have the correct structure and can be serialized to JSON properly
"""

import sys
import os
import json
from typing import NamedTuple

# Add current directory to path
sys.path.insert(0, '.')

# Mock runtime module
class MockArgs:
    def __init__(self, input_params):
        # Create a simple object that has the input_params as attributes
        if isinstance(input_params, dict):
            self.input = type('Input', (), input_params)()
        else:
            self.input = input_params
        self.logger = MockLogger()

class MockLogger:
    def info(self, msg): pass  # Suppress logs for cleaner test output
    def error(self, msg): pass

def test_create_draft_returns_dict():
    """Test that create_draft returns a dict instead of NamedTuple"""
    print("=== Testing create_draft returns dict ===")
    
    # Import directly to avoid conflicts
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_draft_handler", "./tools/create_draft/handler.py")
    create_draft_module = importlib.util.module_from_spec(spec)
    
    # Mock the runtime import - need to create a generic class that supports subscripting
    import types
    runtime_mock = types.ModuleType('runtime')
    
    # Create a generic Args class that supports type hints
    class Args:
        def __class_getitem__(cls, item):
            return cls
    
    runtime_mock.Args = Args
    sys.modules['runtime'] = runtime_mock
    
    try:
        spec.loader.exec_module(create_draft_module)
        
        # Test with normal parameters
        input_params = {
            'draft_name': '测试项目',
            'width': 1920,
            'height': 1080,
            'fps': 30
        }
        
        mock_args = MockArgs(input_params)
        
        # Call the handler
        result = create_draft_module.handler(mock_args)
        
        # Verify result is a dict, not a NamedTuple
        print(f"Result type: {type(result)}")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        print("✅ Result is a dict")
        
        # Verify structure
        assert 'draft_id' in result, "Missing 'draft_id' key"
        assert 'success' in result, "Missing 'success' key"
        assert 'message' in result, "Missing 'message' key"
        print("✅ Dict has correct keys: draft_id, success, message")
        
        # Verify JSON serialization works correctly
        json_str = json.dumps(result, ensure_ascii=False)
        json_obj = json.loads(json_str)
        
        # Verify it's an object, not an array
        assert isinstance(json_obj, dict), "JSON should serialize to object, not array"
        print("✅ JSON serialization produces object (not array)")
        
        # Verify object properties are accessible
        assert json_obj['draft_id'] == result['draft_id']
        assert json_obj['success'] == result['success']
        assert json_obj['message'] == result['message']
        print("✅ JSON object properties are accessible by name")
        
        print(f"\nJSON output structure:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Clean up the test draft
        if result['success'] and result['draft_id']:
            import shutil
            draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", result['draft_id'])
            if os.path.exists(draft_folder):
                shutil.rmtree(draft_folder)
        
        return True, result['draft_id'] if result['success'] else None
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_export_drafts_returns_dict(draft_id=None):
    """Test that export_drafts returns a dict instead of NamedTuple"""
    print("\n=== Testing export_drafts returns dict ===")
    
    # First create a draft if none provided
    if not draft_id:
        print("Creating a test draft first...")
        success, draft_id = test_create_draft_returns_dict()
        if not success or not draft_id:
            print("❌ Failed to create test draft")
            return False
        print(f"Created test draft: {draft_id}")
    
    # Import directly to avoid conflicts
    import importlib.util
    spec = importlib.util.spec_from_file_location("export_drafts_handler", "./tools/export_drafts/handler.py")
    export_drafts_module = importlib.util.module_from_spec(spec)
    
    # Mock the runtime import - need to create a generic class that supports subscripting
    import types
    runtime_mock = types.ModuleType('runtime')
    
    # Create a generic Args class that supports type hints
    class Args:
        def __class_getitem__(cls, item):
            return cls
    
    runtime_mock.Args = Args
    sys.modules['runtime'] = runtime_mock
    
    try:
        spec.loader.exec_module(export_drafts_module)
        
        # Create input using the module's Input class
        ExportInput = export_drafts_module.Input
        input_data = ExportInput(
            draft_ids=draft_id,
            remove_temp_files=True,  # Clean up after test
            export_all=False
        )
        
        mock_args = MockArgs(input_data)
        
        # Call the handler
        result = export_drafts_module.handler(mock_args)
        
        # Verify result is a dict, not a NamedTuple
        print(f"Result type: {type(result)}")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        print("✅ Result is a dict")
        
        # Verify structure
        assert 'draft_data' in result, "Missing 'draft_data' key"
        assert 'exported_count' in result, "Missing 'exported_count' key"
        assert 'success' in result, "Missing 'success' key"
        assert 'message' in result, "Missing 'message' key"
        print("✅ Dict has correct keys: draft_data, exported_count, success, message")
        
        # Verify JSON serialization works correctly
        json_str = json.dumps(result, ensure_ascii=False)
        json_obj = json.loads(json_str)
        
        # Verify it's an object, not an array
        assert isinstance(json_obj, dict), "JSON should serialize to object, not array"
        print("✅ JSON serialization produces object (not array)")
        
        # Verify object properties are accessible
        assert json_obj['draft_data'] == result['draft_data']
        assert json_obj['exported_count'] == result['exported_count']
        assert json_obj['success'] == result['success']
        assert json_obj['message'] == result['message']
        print("✅ JSON object properties are accessible by name")
        
        print(f"\nJSON output structure (truncated):")
        result_preview = {
            'draft_data': result['draft_data'][:200] + '...' if len(result['draft_data']) > 200 else result['draft_data'],
            'exported_count': result['exported_count'],
            'success': result['success'],
            'message': result['message']
        }
        print(json.dumps(result_preview, ensure_ascii=False, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Output type fix for create_draft and export_drafts\n")
    print("=" * 60)
    
    results = []
    
    # Test create_draft
    success, draft_id = test_create_draft_returns_dict()
    results.append(success)
    
    # Test export_drafts with the created draft
    if success and draft_id:
        success = test_export_drafts_returns_dict(draft_id)
        results.append(success)
    
    print("\n" + "=" * 60)
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
