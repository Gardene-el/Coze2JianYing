#!/usr/bin/env python3
"""
Test for export_script tool

Validates the export_script tool functionality including:
- Reading script file from /tmp/coze2jianying.py
- Optional content clearing
- Error handling for missing files
"""

import os
import sys
import tempfile


def create_test_script_file():
    """Create a test script file at /tmp/coze2jianying.py"""
    print("=== Creating test script file ===")
    
    test_script_content = """#!/usr/bin/env python3
# Test Coze to JianYing Script
# This is a test script file

def main():
    print("Hello from coze2jianying!")
    
if __name__ == "__main__":
    main()
"""
    
    script_path = "/tmp/coze2jianying.py"
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(test_script_content)
        
        print(f"✅ Created test script file: {script_path}")
        print(f"   Size: {len(test_script_content)} characters")
        return True, test_script_content
    except Exception as e:
        print(f"❌ Failed to create test script file: {e}")
        return False, ""


def test_export_script_basic():
    """Test basic export without clearing content"""
    print("\n=== Testing basic export (clear_content=False) ===")
    
    # Add the handler directory to the path
    handler_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'export_script')
    sys.path.insert(0, handler_dir)
    
    from handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test with clear_content=False
    input_data = Input(clear_content=False)
    args = MockArgs(input_data)
    
    result = handler(args)
    
    print(f"Result: {result}")
    print(f"Success: {result['success']}")
    print(f"File size: {result['file_size']}")
    print(f"Message: {result['message']}")
    print(f"Content preview: {result['script_content'][:100]}...")
    
    assert result['success'] == True, "Export should succeed"
    assert result['file_size'] > 0, "File size should be greater than 0"
    assert len(result['script_content']) > 0, "Script content should not be empty"
    assert "成功导出" in result['message'], "Message should indicate success"
    assert "已清空" not in result['message'], "Message should not mention clearing"
    
    print("✅ Basic export test passed")
    return True


def test_export_script_with_clear():
    """Test export with clearing content"""
    print("\n=== Testing export with clear (clear_content=True) ===")
    
    # Add the handler directory to the path (if not already added)
    handler_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'export_script')
    if handler_dir not in sys.path:
        sys.path.insert(0, handler_dir)
    
    from handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test with clear_content=True
    input_data = Input(clear_content=True)
    args = MockArgs(input_data)
    
    result = handler(args)
    
    print(f"Result: {result}")
    print(f"Success: {result['success']}")
    print(f"File size: {result['file_size']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == True, "Export should succeed"
    assert result['file_size'] > 0, "File size should be greater than 0"
    assert len(result['script_content']) > 0, "Script content should not be empty"
    assert "成功导出" in result['message'], "Message should indicate success"
    assert "已清空" in result['message'], "Message should mention clearing"
    
    # Check if file is actually cleared
    script_path = "/tmp/coze2jianying.py"
    with open(script_path, 'r', encoding='utf-8') as f:
        cleared_content = f.read()
    
    assert len(cleared_content) == 0, "File should be empty after clearing"
    print("✅ File content was successfully cleared")
    
    print("✅ Export with clear test passed")
    return True


def test_export_script_missing_file():
    """Test export when file doesn't exist"""
    print("\n=== Testing export with missing file ===")
    
    # Remove the test file
    script_path = "/tmp/coze2jianying.py"
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Removed test file: {script_path}")
    
    # Add the handler directory to the path (if not already added)
    handler_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'export_script')
    if handler_dir not in sys.path:
        sys.path.insert(0, handler_dir)
    
    from handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test with missing file
    input_data = Input(clear_content=False)
    args = MockArgs(input_data)
    
    result = handler(args)
    
    print(f"Result: {result}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == False, "Export should fail"
    assert result['file_size'] == 0, "File size should be 0"
    assert result['script_content'] == "", "Script content should be empty"
    assert "不存在" in result['message'], "Message should indicate file doesn't exist"
    
    print("✅ Missing file test passed")
    return True


def test_helper_functions():
    """Test helper functions directly"""
    print("\n=== Testing helper functions ===")
    
    # Add the handler directory to the path
    handler_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'export_script')
    sys.path.insert(0, handler_dir)
    
    from handler import read_script_file, clear_file_content
    
    # Create a test file
    test_file = "/tmp/test_helper_export.py"
    test_content = "# Test content\nprint('hello')\n"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Test read_script_file
    success, content, error = read_script_file(test_file)
    assert success == True, "Should successfully read file"
    assert content == test_content, "Content should match"
    assert error == "", "No error should be reported"
    print("✅ read_script_file works correctly")
    
    # Test clear_file_content
    success, error = clear_file_content(test_file)
    assert success == True, "Should successfully clear file"
    assert error == "", "No error should be reported"
    
    with open(test_file, 'r', encoding='utf-8') as f:
        cleared = f.read()
    assert len(cleared) == 0, "File should be empty"
    print("✅ clear_file_content works correctly")
    
    # Test reading non-existent file
    success, content, error = read_script_file("/tmp/nonexistent_file_12345.py")
    assert success == False, "Should fail for non-existent file"
    assert "不存在" in error, "Error should mention file doesn't exist"
    print("✅ Error handling for non-existent file works correctly")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("✅ All helper function tests passed")
    return True


def cleanup_test_files():
    """Clean up any test files created"""
    print("\n=== Cleaning up test files ===")
    
    test_files = [
        "/tmp/coze2jianying.py",
        "/tmp/test_helper_export.py"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")


if __name__ == "__main__":
    try:
        print("Starting export_script tool tests...")
        
        # Create test script file
        success, content = create_test_script_file()
        if not success:
            print("❌ Failed to create test file, aborting tests")
            sys.exit(1)
        
        # Run tests
        test_helper_functions()
        test_export_script_basic()
        
        # Recreate file for next test (it was cleared in previous test)
        create_test_script_file()
        test_export_script_with_clear()
        
        test_export_script_missing_file()
        
        # Clean up
        cleanup_test_files()
        
        print("\n=== All export_script tool tests completed successfully ===")
        
    except AssertionError as e:
        print(f"❌ Test assertion failed: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_files()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_files()
        sys.exit(1)
