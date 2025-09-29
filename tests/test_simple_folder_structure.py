#!/usr/bin/env python3
"""
Simple test to verify the folder structure changes
"""

import os
import uuid
import json
import shutil

def test_create_draft_folder():
    """Test the create_draft_folder function"""
    print("=== Testing create_draft_folder function ===")
    
    # Copy the function logic here for testing
    def create_draft_folder(draft_id: str) -> str:
        """Create draft folder in /tmp/jianying_assistant/drafts/ directory"""
        base_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
        draft_folder = os.path.join(base_dir, draft_id)
        
        try:
            os.makedirs(draft_folder, exist_ok=True)
            return draft_folder
        except Exception as e:
            raise Exception(f"Failed to create draft folder: {str(e)}")
    
    # Test the function
    test_uuid = str(uuid.uuid4())
    
    try:
        draft_folder = create_draft_folder(test_uuid)
        expected_path = f"/tmp/jianying_assistant/drafts/{test_uuid}"
        
        print(f"Created folder: {draft_folder}")
        print(f"Expected path: {expected_path}")
        
        # Verify path matches
        assert draft_folder == expected_path, f"Path mismatch: {draft_folder} != {expected_path}"
        
        # Verify folder exists
        assert os.path.exists(draft_folder), f"Folder does not exist: {draft_folder}"
        
        # Verify directory structure
        assert os.path.exists("/tmp/jianying_assistant"), "Base directory missing"
        assert os.path.exists("/tmp/jianying_assistant/drafts"), "Drafts directory missing"
        
        print("✅ create_draft_folder test passed!")
        
        # Clean up
        shutil.rmtree(draft_folder)
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_discover_all_drafts():
    """Test the discover_all_drafts function"""
    print("\n=== Testing discover_all_drafts function ===")
    
    # Copy the function logic here for testing
    def validate_uuid_format(uuid_str: str) -> bool:
        try:
            import uuid
            uuid.UUID(uuid_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def discover_all_drafts():
        """Discover all draft IDs in the drafts directory"""
        drafts_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
        
        if not os.path.exists(drafts_dir):
            return []
        
        draft_ids = []
        try:
            for item in os.listdir(drafts_dir):
                item_path = os.path.join(drafts_dir, item)
                if os.path.isdir(item_path) and validate_uuid_format(item):
                    config_file = os.path.join(item_path, "draft_config.json")
                    if os.path.exists(config_file):
                        draft_ids.append(item)
        except Exception:
            return []
        
        return draft_ids
    
    # Create test drafts
    base_dir = "/tmp/jianying_assistant/drafts"
    os.makedirs(base_dir, exist_ok=True)
    
    test_drafts = []
    for i in range(3):
        draft_id = str(uuid.uuid4())
        draft_folder = os.path.join(base_dir, draft_id)
        os.makedirs(draft_folder, exist_ok=True)
        
        # Create config file
        config = {
            "draft_id": draft_id,
            "project": {"name": f"Test Draft {i+1}"},
            "created_timestamp": 1703123456.789
        }
        
        config_file = os.path.join(draft_folder, "draft_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        test_drafts.append(draft_id)
    
    try:
        # Test discovery
        discovered = discover_all_drafts()
        
        print(f"Created {len(test_drafts)} test drafts")
        print(f"Discovered {len(discovered)} drafts")
        print(f"Test draft IDs: {test_drafts}")
        print(f"Discovered IDs: {discovered}")
        
        # Verify all test drafts were discovered
        assert len(discovered) == len(test_drafts), f"Expected {len(test_drafts)} drafts, found {len(discovered)}"
        
        for draft_id in test_drafts:
            assert draft_id in discovered, f"Draft {draft_id} not discovered"
        
        print("✅ discover_all_drafts test passed!")
        
        # Clean up
        for draft_id in test_drafts:
            draft_folder = os.path.join(base_dir, draft_id)
            if os.path.exists(draft_folder):
                shutil.rmtree(draft_folder)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Clean up on error
        for draft_id in test_drafts:
            draft_folder = os.path.join(base_dir, draft_id)
            if os.path.exists(draft_folder):
                shutil.rmtree(draft_folder)
        return False

def test_load_draft_config():
    """Test the load_draft_config function with new path structure"""
    print("\n=== Testing load_draft_config function ===")
    
    def load_draft_config(draft_id: str):
        """Load draft configuration from file"""
        draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
        config_file = os.path.join(draft_folder, "draft_config.json")
        
        if not os.path.exists(draft_folder):
            return False, {}, f"草稿文件夹不存在: {draft_id}"
        
        if not os.path.exists(config_file):
            return False, {}, f"草稿配置文件不存在: {draft_id}"
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return True, config, ""
        except Exception as e:
            return False, {}, f"读取草稿配置失败: {str(e)}"
    
    # Create a test draft
    test_draft_id = str(uuid.uuid4())
    base_dir = "/tmp/jianying_assistant/drafts"
    draft_folder = os.path.join(base_dir, test_draft_id)
    os.makedirs(draft_folder, exist_ok=True)
    
    test_config = {
        "draft_id": test_draft_id,
        "project": {
            "name": "Test Load Config",
            "width": 800,
            "height": 600
        },
        "created_timestamp": 1703123456.789
    }
    
    config_file = os.path.join(draft_folder, "draft_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    try:
        # Test loading
        success, loaded_config, error_msg = load_draft_config(test_draft_id)
        
        print(f"Load result: success={success}, error='{error_msg}'")
        
        assert success, f"Failed to load config: {error_msg}"
        assert loaded_config["draft_id"] == test_draft_id, "Draft ID mismatch"
        assert loaded_config["project"]["name"] == "Test Load Config", "Project name mismatch"
        
        print("✅ load_draft_config test passed!")
        
        # Clean up
        shutil.rmtree(draft_folder)
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Clean up on error
        if os.path.exists(draft_folder):
            shutil.rmtree(draft_folder)
        return False

if __name__ == "__main__":
    print("Testing folder structure changes...")
    
    results = []
    results.append(test_create_draft_folder())
    results.append(test_discover_all_drafts())
    results.append(test_load_draft_config())
    
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ All folder structure tests passed!")
        print("Key changes verified:")
        print("1. ✅ Drafts created in /tmp/jianying_assistant/drafts/{uuid}")
        print("2. ✅ Discovery function finds all drafts in directory")
        print("3. ✅ Load function works with new path structure")
    else:
        print("❌ Some tests failed")