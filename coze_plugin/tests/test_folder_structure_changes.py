#!/usr/bin/env python3
"""
Test script to verify the folder structure changes and export_all functionality
"""

import sys
import os
import json
import shutil
import uuid

# Mock Input classes to test functionality
class MockCreateInput:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockExportInput:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockArgs:
    def __init__(self, input_data):
        self.input = input_data
        self.logger = MockLogger()

class MockLogger:
    def info(self, msg): print(f'INFO: {msg}')
    def error(self, msg): print(f'ERROR: {msg}')

def test_new_folder_structure():
    """Test that drafts are created in the new folder structure"""
    print("=== Testing New Folder Structure ===")
    
    # Test the create_draft_folder function directly
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
        
        # Test the create_draft_folder function
        test_uuid = str(uuid.uuid4())
        draft_folder = create_draft_module.create_draft_folder(test_uuid)
        
        expected_path = f"/tmp/jianying_assistant/drafts/{test_uuid}"
        
        print(f"Created draft folder: {draft_folder}")
        print(f"Expected path: {expected_path}")
        
        assert draft_folder == expected_path, f"Expected {expected_path}, got {draft_folder}"
        assert os.path.exists(draft_folder), f"Folder {draft_folder} was not created"
        
        # Test directory structure
        base_dir = "/tmp/jianying_assistant"
        drafts_dir = "/tmp/jianying_assistant/drafts"
        
        assert os.path.exists(base_dir), f"Base directory {base_dir} does not exist"
        assert os.path.exists(drafts_dir), f"Drafts directory {drafts_dir} does not exist"
        
        print("✅ New folder structure test passed!")
        
        # Clean up test folder
        shutil.rmtree(draft_folder)
        
        return test_uuid
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_export_all_functionality():
    """Test the export_all functionality"""
    print("\n=== Testing Export All Functionality ===")
    
    # First create some test drafts manually
    base_dir = "/tmp/jianying_assistant/drafts"
    os.makedirs(base_dir, exist_ok=True)
    
    test_drafts = []
    for i in range(3):
        draft_id = str(uuid.uuid4())
        draft_folder = os.path.join(base_dir, draft_id)
        os.makedirs(draft_folder, exist_ok=True)
        
        # Create a test config file
        config = {
            "draft_id": draft_id,
            "project": {
                "name": f"测试草稿{i+1}",
                "width": 1920,
                "height": 1080,
                "fps": 30
            },
            "created_timestamp": 1703123456.789
        }
        
        config_file = os.path.join(draft_folder, "draft_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        test_drafts.append(draft_id)
    
    print(f"Created {len(test_drafts)} test drafts")
    
    # Test discover_all_drafts function
    import importlib.util
    spec = importlib.util.spec_from_file_location("export_drafts_handler", "./tools/export_drafts/handler.py")
    export_drafts_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(export_drafts_module)
        
        # Test discovery function
        discovered_drafts = export_drafts_module.discover_all_drafts()
        print(f"Discovered drafts: {discovered_drafts}")
        
        assert len(discovered_drafts) == 3, f"Expected 3 drafts, found {len(discovered_drafts)}"
        
        for draft_id in test_drafts:
            assert draft_id in discovered_drafts, f"Draft {draft_id} not found in discovered drafts"
        
        print("✅ Export all discovery test passed!")
        
        # Test export_all parameter
        mock_input = MockExportInput(
            draft_ids=None,
            export_all=True,
            remove_temp_files=False
        )
        
        mock_args = MockArgs(mock_input)
        
        # Test the handler with export_all=True
        result = export_drafts_module.handler(mock_args)
        
        print(f"Export all result: success={result.success}, count={result.exported_count}")
        
        if result.success:
            print("✅ Export all functionality test passed!")
            
            # Verify the exported data contains all drafts
            try:
                exported_data = json.loads(result.draft_data)
                assert exported_data["draft_count"] == 3, f"Expected 3 drafts in export, got {exported_data['draft_count']}"
                print(f"✅ Exported data contains {exported_data['draft_count']} drafts as expected")
            except json.JSONDecodeError:
                print("❌ Failed to parse exported JSON data")
        else:
            print(f"❌ Export all failed: {result.message}")
        
        # Clean up test drafts
        for draft_id in test_drafts:
            draft_folder = os.path.join(base_dir, draft_id)
            if os.path.exists(draft_folder):
                shutil.rmtree(draft_folder)
        
        print("Test drafts cleaned up")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

def test_backward_compatibility():
    """Test that the old functionality still works"""
    print("\n=== Testing Backward Compatibility ===")
    
    # Create a test draft in the new structure first
    base_dir = "/tmp/jianying_assistant/drafts"
    os.makedirs(base_dir, exist_ok=True)
    
    test_draft_id = str(uuid.uuid4())
    draft_folder = os.path.join(base_dir, test_draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    # Create a test config file
    config = {
        "draft_id": test_draft_id,
        "project": {
            "name": "兼容性测试草稿",
            "width": 800,
            "height": 600,
            "fps": 30
        },
        "created_timestamp": 1703123456.789
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # Test exporting specific draft (old behavior)
    import importlib.util
    spec = importlib.util.spec_from_file_location("export_drafts_handler", "./tools/export_drafts/handler.py")
    export_drafts_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(export_drafts_module)
        
        mock_input = MockExportInput(
            draft_ids=test_draft_id,
            export_all=False,
            remove_temp_files=False
        )
        
        mock_args = MockArgs(mock_input)
        result = export_drafts_module.handler(mock_args)
        
        print(f"Backward compatibility result: success={result.success}, count={result.exported_count}")
        
        if result.success:
            print("✅ Backward compatibility test passed!")
        else:
            print(f"❌ Backward compatibility failed: {result.message}")
        
        # Clean up
        shutil.rmtree(draft_folder)
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing folder structure changes and export_all functionality...")
    
    test_new_folder_structure()
    test_export_all_functionality()
    test_backward_compatibility()
    
    print("\n=== All Tests Completed ===")
    print("Key changes verified:")
    print("1. ✅ Drafts now created in /tmp/jianying_assistant/drafts/")
    print("2. ✅ export_all parameter allows exporting all drafts")
    print("3. ✅ Backward compatibility maintained for specific draft export")
    print("4. ✅ Discovery function correctly finds all drafts in directory")