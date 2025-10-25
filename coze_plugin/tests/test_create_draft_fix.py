#!/usr/bin/env python3
"""
Test script to verify the create_draft fix for None parameters
"""

import sys
import os
from typing import NamedTuple

# Add current directory to path
sys.path.insert(0, '.')

# Mock runtime module
class MockArgs:
    def __init__(self, input_params):
        # Create a simple object that has the input_params as attributes
        self.input = type('Input', (), input_params)()
        self.logger = MockLogger()

class MockLogger:
    def info(self, msg): print(f'INFO: {msg}')
    def error(self, msg): print(f'ERROR: {msg}')

def test_with_partial_params():
    """Test create_draft with only width and height provided"""
    print("=== Testing create_draft with partial parameters ===")
    
    # Import directly to avoid conflicts
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_draft_handler", "./tools/create_draft/handler.py")
    create_draft_module = importlib.util.module_from_spec(spec)
    
    # Mock the runtime import
    import types
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = lambda x: x
    sys.modules['runtime'] = runtime_mock
    
    try:
        spec.loader.exec_module(create_draft_module)
        
        # Test with only width and height (mimicking Coze behavior)
        input_params = {
            'width': 800,
            'height': 600,
            'project_name': None,
            'fps': None
        }
        
        mock_args = MockArgs(input_params)
        
        # Call the handler
        result = create_draft_module.handler(mock_args)
        print(f"Result: {result}")
        
        if result.success:
            print("✅ Test passed! Draft created successfully with partial parameters")
            
            # Check if the draft folder was created
            draft_folder = f'/tmp/{result.draft_id}'
            config_file = f'{draft_folder}/draft_config.json'
            
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                print(f"Draft config preview:")
                print(f"  Project name: {config['project']['name']}")
                print(f"  Dimensions: {config['project']['width']}x{config['project']['height']}")
                print(f"  FPS: {config['project']['fps']}")
                
                # Clean up
                import shutil
                shutil.rmtree(draft_folder)
                print("Cleaned up test files")
            else:
                print("❌ Config file not found")
        else:
            print(f"❌ Test failed: {result.message}")
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_with_all_params():
    """Test create_draft with all parameters provided"""
    print("\n=== Testing create_draft with all parameters ===")
    
    # Import directly to avoid conflicts
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_draft_handler", "./tools/create_draft/handler.py")
    create_draft_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(create_draft_module)
        
        # Test with all parameters
        input_params = {
            'width': 1920,
            'height': 1080,
            'project_name': "Complete Test Project",
            'fps': 30
        }
        
        mock_args = MockArgs(input_params)
        
        # Call the handler
        result = create_draft_module.handler(mock_args)
        print(f"Result: {result}")
        
        if result.success:
            print("✅ Test passed! Draft created successfully with all parameters")
            
            # Clean up
            draft_folder = f'/tmp/{result.draft_id}'
            if os.path.exists(draft_folder):
                import shutil
                shutil.rmtree(draft_folder)
                print("Cleaned up test files")
        else:
            print(f"❌ Test failed: {result.message}")
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_partial_params()
    test_with_all_params()
    print("\n=== Tests completed ===")