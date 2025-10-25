#!/usr/bin/env python3
"""
Test script for create_draft and export_drafts tools
"""

import sys
import os
import json
import types
from typing import NamedTuple, Generic, TypeVar

# Add current directory to path
sys.path.insert(0, '.')

# Mock the runtime module for testing
T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = MockLogger()

class MockLogger:
    def info(self, msg): 
        print(f'INFO: {msg}')
    def error(self, msg): 
        print(f'ERROR: {msg}')
    def warning(self, msg):
        print(f'WARNING: {msg}')

def test_create_draft():
    """Test create_draft tool"""
    print("=== Testing create_draft tool ===")
    
    # Import create_draft components directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_draft_handler", "./coze_plugin/tools/create_draft/handler.py")
    create_draft_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(create_draft_module)
    
    create_handler = create_draft_module.handler
    CreateInput = create_draft_module.Input
    
    # Test with default parameters
    mock_args = MockArgs(CreateInput(
        draft_name="测试项目",
        width=1920,
        height=1080,
        fps=30
    ))
    
    result = create_handler(mock_args)
    print(f"Create draft result: {result}")
    
    if result['success']:
        # Check if files were created
        draft_id = result['draft_id']
        draft_folder = f'/tmp/jianying_assistant/drafts/{draft_id}'
        config_file = f'{draft_folder}/draft_config.json'
        
        print(f"Draft folder exists: {os.path.exists(draft_folder)}")
        print(f"Config file exists: {os.path.exists(config_file)}")
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Config preview:\n{json.dumps(config, indent=2, ensure_ascii=False)}")
        
        return draft_id
    else:
        print("Failed to create draft")
        return None

def test_export_drafts(draft_id):
    """Test export_drafts tool"""
    print("\n=== Testing export_drafts tool ===")
    
    if not draft_id:
        print("No draft ID to test export")
        return
    
    # Import export_drafts components directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("export_drafts_handler", "./coze_plugin/tools/export_drafts/handler.py")
    export_drafts_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export_drafts_module)
    
    export_handler = export_drafts_module.handler
    ExportInput = export_drafts_module.Input
    
    # Test single draft export
    mock_args = MockArgs(ExportInput(
        draft_ids=draft_id,
        remove_temp_files=False
    ))
    
    result = export_handler(mock_args)
    print(f"Export draft result success: {result['success']}")
    print(f"Exported count: {result['exported_count']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        # Parse and display draft data preview
        try:
            draft_data = json.loads(result['draft_data'])
            print(f"Draft data preview:\n{json.dumps(draft_data, indent=2, ensure_ascii=False)[:500]}...")
        except json.JSONDecodeError as e:
            print(f"Failed to parse draft data: {e}")
    
    # Test with cleanup
    print("\n--- Testing with cleanup ---")
    mock_args_cleanup = MockArgs(ExportInput(
        draft_ids=draft_id,
        remove_temp_files=True
    ))
    
    result_cleanup = export_handler(mock_args_cleanup)
    print(f"Export with cleanup result: {result_cleanup['success']}")
    print(f"Message: {result_cleanup['message']}")
    
    # Check if files were cleaned up
    draft_folder = f'/tmp/jianying_assistant/drafts/{draft_id}'
    print(f"Draft folder still exists: {os.path.exists(draft_folder)}")

def test_error_cases():
    """Test error handling"""
    print("\n=== Testing error cases ===")
    
    # Import handlers directly
    import importlib.util
    
    spec1 = importlib.util.spec_from_file_location("create_draft_handler", "./coze_plugin/tools/create_draft/handler.py")
    create_draft_module = importlib.util.module_from_spec(spec1)
    spec1.loader.exec_module(create_draft_module)
    
    spec2 = importlib.util.spec_from_file_location("export_drafts_handler", "./coze_plugin/tools/export_drafts/handler.py")
    export_drafts_module = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(export_drafts_module)
    
    create_handler = create_draft_module.handler
    CreateInput = create_draft_module.Input
    export_handler = export_drafts_module.handler
    ExportInput = export_drafts_module.Input
    
    # Test invalid create_draft parameters
    print("--- Testing invalid create_draft parameters ---")
    mock_args = MockArgs(CreateInput(
        draft_name="错误测试",
        width=-1,  # Invalid width
        height=1080,
        fps=30
    ))
    
    result = create_handler(mock_args)
    print(f"Invalid width result: {result}")
    
    # Test invalid UUID for export
    print("--- Testing invalid UUID for export ---")
    mock_args = MockArgs(ExportInput(
        draft_ids="invalid-uuid",
        remove_temp_files=False
    ))
    
    result = export_handler(mock_args)
    print(f"Invalid UUID result: {result}")
    
    # Test non-existent draft
    print("--- Testing non-existent draft ---")
    mock_args = MockArgs(ExportInput(
        draft_ids="123e4567-e89b-12d3-a456-426614174000",  # Valid UUID format but doesn't exist
        remove_temp_files=False
    ))
    
    result = export_handler(mock_args)
    print(f"Non-existent draft result: {result}")

if __name__ == "__main__":
    try:
        # Test create_draft
        draft_id = test_create_draft()
        
        # Test export_drafts
        test_export_drafts(draft_id)
        
        # Test error cases
        test_error_cases()
        
        print("\n=== All tests completed ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()