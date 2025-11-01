#!/usr/bin/env python3
"""
Test script for documentation generation tools

This script tests both generate_tool_doc.py and scan_and_generate_docs.py
to ensure they work correctly without modifying the original handler.py files.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))

from generate_tool_doc import (
    extract_module_docstring,
    extract_input_parameters,
    extract_output_parameters,
    check_output_type,
    get_tool_name_from_path,
    format_tool_name_display,
    generate_documentation
)


def test_create_draft_tool():
    """Test documentation generation for create_draft tool"""
    print("=" * 80)
    print("Test 1: Testing create_draft tool documentation generation")
    print("=" * 80)
    
    # Path to create_draft handler.py
    handler_path = "coze_plugin/tools/create_draft/handler.py"
    
    if not os.path.exists(handler_path):
        print(f"❌ Error: {handler_path} not found")
        return False
    
    print(f"\n📁 Handler path: {handler_path}")
    
    # Test 1: Extract tool name
    print("\n1️⃣ Testing tool name extraction...")
    tool_name = get_tool_name_from_path(handler_path)
    print(f"   Tool name: {tool_name}")
    expected_tool_name = "create_draft"
    if tool_name == expected_tool_name:
        print(f"   ✅ Correct! Expected: {expected_tool_name}")
    else:
        print(f"   ❌ Error! Expected: {expected_tool_name}, Got: {tool_name}")
        return False
    
    # Test 2: Extract docstring
    print("\n2️⃣ Testing docstring extraction...")
    docstring = extract_module_docstring(handler_path)
    print(f"   Docstring: {docstring[:100]}...")
    if docstring and len(docstring) > 0:
        print("   ✅ Docstring extracted successfully")
    else:
        print("   ❌ Error: No docstring found")
        return False
    
    # Test 3: Extract input parameters
    print("\n3️⃣ Testing input parameters extraction...")
    parameters = extract_input_parameters(handler_path)
    print(f"   Found {len(parameters)} parameters:")
    for param in parameters:
        print(f"     - {param['name']}: {param['type']} = {param['default']}")
        if param['comment']:
            print(f"       Comment: {param['comment']}")
    
    expected_params = ['draft_name', 'width', 'height', 'fps']
    found_params = [p['name'] for p in parameters]
    if all(ep in found_params for ep in expected_params):
        print("   ✅ All expected parameters found")
    else:
        print(f"   ❌ Error! Expected parameters: {expected_params}, Found: {found_params}")
        return False
    
    # Test 4: Generate full documentation
    print("\n4️⃣ Testing full documentation generation...")
    doc_content = generate_documentation(handler_path)
    
    # Check if key elements are present
    checks = [
        ("工具函数 Create Draft" in doc_content, "Title with 'Create Draft'"),
        ("工具名称：create_draft" in doc_content, "Tool name line"),
        ("工具描述：" in doc_content, "Tool description"),
        ("## 输入参数" in doc_content, "Input parameters section"),
        ("class Input(NamedTuple):" in doc_content, "Input class definition"),
        ("draft_name" in doc_content, "draft_name parameter"),
        ("width" in doc_content, "width parameter"),
        ("height" in doc_content, "height parameter"),
        ("fps" in doc_content, "fps parameter"),
    ]
    
    all_passed = True
    for check, description in checks:
        if check:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ Missing: {description}")
            all_passed = False
    
    if not all_passed:
        print("\n   Generated documentation preview:")
        print("   " + "-" * 76)
        for line in doc_content.split('\n')[:20]:
            print(f"   {line}")
        print("   " + "-" * 76)
        return False
    
    # Test 5: Write to temporary file
    print("\n5️⃣ Testing file writing...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        temp_file = f.name
        f.write(doc_content)
    
    print(f"   Temporary file created: {temp_file}")
    
    # Verify file can be read back
    with open(temp_file, 'r', encoding='utf-8') as f:
        read_content = f.read()
    
    if read_content == doc_content:
        print("   ✅ File write/read successful")
        os.unlink(temp_file)  # Clean up
    else:
        print("   ❌ Error: File content mismatch")
        os.unlink(temp_file)
        return False
    
    print("\n✅ All tests passed for create_draft tool!")
    return True


def test_export_drafts_tool():
    """Test documentation generation for export_drafts tool"""
    print("\n" + "=" * 80)
    print("Test 2: Testing export_drafts tool documentation generation")
    print("=" * 80)
    
    handler_path = "coze_plugin/tools/export_drafts/handler.py"
    
    if not os.path.exists(handler_path):
        print(f"❌ Error: {handler_path} not found")
        return False
    
    print(f"\n📁 Handler path: {handler_path}")
    
    # Quick test - just generate and check
    print("\n📝 Generating documentation...")
    try:
        doc_content = generate_documentation(handler_path)
        
        # Basic checks
        if "工具函数 Export Drafts" in doc_content and "工具名称：export_drafts" in doc_content:
            print("   ✅ Documentation generated successfully")
            print("\n   Preview (first 20 lines):")
            print("   " + "-" * 76)
            for line in doc_content.split('\n')[:20]:
                print(f"   {line}")
            print("   " + "-" * 76)
            return True
        else:
            print("   ❌ Error: Generated documentation missing key elements")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_add_videos_tool():
    """Test documentation generation for add_videos tool with Output extraction"""
    print("\n" + "=" * 80)
    print("Test 3: Testing add_videos tool with Output extraction")
    print("=" * 80)
    
    handler_path = "coze_plugin/tools/add_videos/handler.py"
    
    if not os.path.exists(handler_path):
        print(f"❌ Error: {handler_path} not found")
        return False
    
    print(f"\n📁 Handler path: {handler_path}")
    
    # Test 1: Extract output parameters
    print("\n1️⃣ Testing output parameters extraction...")
    output_params = extract_output_parameters(handler_path)
    print(f"   Found {len(output_params)} output parameters:")
    for param in output_params:
        print(f"     - {param['name']}: {param['type']}")
        if param['default'] != 'N/A':
            print(f"       Default: {param['default']}")
        if param['comment']:
            print(f"       Comment: {param['comment']}")
    
    # Check for key output parameters
    found_output_params = [p['name'] for p in output_params]
    if 'segment_ids' in found_output_params and 'success' in found_output_params and 'message' in found_output_params:
        print("   ✅ Key output parameters found (segment_ids, success, message)")
    else:
        print(f"   ❌ Error! Expected segment_ids, success, message. Found: {found_output_params}")
        return False
    
    # Test 2: Check output type
    print("\n2️⃣ Testing output type detection...")
    output_type = check_output_type(handler_path)
    print(f"   Output type: {output_type}")
    if output_type == 'NamedTuple':
        print("   ✅ Correctly detected NamedTuple output")
    else:
        print(f"   ❌ Error! Expected: NamedTuple, Got: {output_type}")
        return False
    
    # Test 3: Generate full documentation with Output section and field explanations
    print("\n3️⃣ Testing full documentation generation with Output and field explanations...")
    try:
        doc_content = generate_documentation(handler_path)
        
        # Check for Output section and non-common field explanations
        checks = [
            ("## 输出参数" in doc_content, "Output parameters section"),
            ("class Output(NamedTuple):" in doc_content, "Output class definition"),
            ("segment_ids" in doc_content, "segment_ids field"),
            ("success" in doc_content, "success field"),
            ("message" in doc_content, "message field"),
            ("### 字段说明" in doc_content, "Field explanation section"),
            ("`segment_ids`:" in doc_content, "segment_ids field explanation"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ Missing: {description}")
                all_passed = False
        
        if not all_passed:
            print("\n   Generated documentation preview:")
            print("   " + "-" * 76)
            for line in doc_content.split('\n')[:40]:
                print(f"   {line}")
            print("   " + "-" * 76)
            return False
        
        print("\n✅ All tests passed for add_videos tool with Output!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage_instructions():
    """Print usage instructions for the scripts"""
    print("\n" + "=" * 80)
    print("📚 Usage Instructions")
    print("=" * 80)
    
    print("\n1️⃣ Generate documentation for a single tool:")
    print("   python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py")
    print()
    print("   With custom output file:")
    print("   python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py output.md")
    
    print("\n2️⃣ Scan and generate documentation for all tools:")
    print("   python scripts/scan_and_generate_docs.py")
    print()
    print("   With custom output directory:")
    print("   python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/docs")
    
    print("\n3️⃣ View generated documentation:")
    print("   After running the scripts, check the _generated.md files:")
    print("   cat coze_plugin/tools/create_draft/create_draft_generated.md")
    
    print("\n" + "=" * 80)


def main():
    """Main test function"""
    print("🧪 Testing Documentation Generation Scripts")
    print("=" * 80)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Run tests
    results = []
    
    try:
        results.append(("create_draft tool", test_create_draft_tool()))
    except Exception as e:
        print(f"\n❌ Exception in create_draft test: {e}")
        import traceback
        traceback.print_exc()
        results.append(("create_draft tool", False))
    
    try:
        results.append(("export_drafts tool", test_export_drafts_tool()))
    except Exception as e:
        print(f"\n❌ Exception in export_drafts test: {e}")
        import traceback
        traceback.print_exc()
        results.append(("export_drafts tool", False))
    
    try:
        results.append(("add_videos tool (with Output)", test_add_videos_tool()))
    except Exception as e:
        print(f"\n❌ Exception in add_videos test: {e}")
        import traceback
        traceback.print_exc()
        results.append(("add_videos tool (with Output)", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12s} {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print_usage_instructions()
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
