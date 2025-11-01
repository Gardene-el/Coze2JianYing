#!/usr/bin/env python3
"""
Tool Documentation Scanner and Generator

This script scans the coze_plugin/tools/ directory for all handler.py files
and generates documentation for each tool using the generate_tool_doc module.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Import the generate_tool_doc module
# Add current directory to path to import the module
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from generate_tool_doc import generate_documentation, get_tool_name_from_path


def find_handler_files(tools_dir: str) -> List[str]:
    """
    Find all handler.py files in the tools directory
    
    Args:
        tools_dir: Path to coze_plugin/tools directory
        
    Returns:
        List of paths to handler.py files
    """
    handler_files = []
    
    try:
        # Walk through the tools directory
        for root, dirs, files in os.walk(tools_dir):
            if 'handler.py' in files:
                handler_path = os.path.join(root, 'handler.py')
                handler_files.append(handler_path)
        
        # Sort for consistent output
        handler_files.sort()
        
    except Exception as e:
        print(f"Error scanning tools directory: {e}")
        return []
    
    return handler_files


def generate_docs_for_tools(handler_files: List[str], output_dir: str = None) -> List[Tuple[str, str, bool]]:
    """
    Generate documentation for all tools
    
    Args:
        handler_files: List of handler.py file paths
        output_dir: Optional output directory for generated docs
        
    Returns:
        List of tuples (tool_name, output_file, success)
    """
    results = []
    
    for handler_path in handler_files:
        tool_name = get_tool_name_from_path(handler_path)
        
        try:
            # Generate documentation
            doc_content = generate_documentation(handler_path)
            
            # Determine output file
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{tool_name}_generated.md")
            else:
                # Default: create in the same directory as handler.py
                output_file = os.path.join(os.path.dirname(handler_path), f"{tool_name}_generated.md")
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            results.append((tool_name, output_file, True))
            print(f"✅ {tool_name:20s} -> {output_file}")
            
        except Exception as e:
            results.append((tool_name, "", False))
            print(f"❌ {tool_name:20s} -> Error: {e}")
    
    return results


def main():
    """Main function to scan and generate documentation for all tools"""
    # Determine the project root directory
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    # Default tools directory
    tools_dir = project_root / "coze_plugin" / "tools"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python scan_and_generate_docs.py [tools_dir] [output_dir]")
            print("\nArguments:")
            print("  tools_dir  : Path to coze_plugin/tools directory (default: auto-detect)")
            print("  output_dir : Optional output directory for generated docs (default: same as handler.py)")
            print("\nExamples:")
            print("  python scripts/scan_and_generate_docs.py")
            print("  python scripts/scan_and_generate_docs.py coze_plugin/tools")
            print("  python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/docs")
            sys.exit(0)
        
        tools_dir = Path(sys.argv[1])
    
    output_dir = None
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Validate tools directory
    if not tools_dir.exists():
        print(f"Error: Tools directory not found: {tools_dir}")
        sys.exit(1)
    
    print(f"🔍 Scanning for handler.py files in: {tools_dir}")
    print("=" * 80)
    
    # Find all handler.py files
    handler_files = find_handler_files(str(tools_dir))
    
    if not handler_files:
        print("No handler.py files found!")
        sys.exit(1)
    
    print(f"\n📋 Found {len(handler_files)} handler.py files")
    print("=" * 80)
    
    # Generate documentation for all tools
    print("\n📝 Generating documentation...")
    print("=" * 80)
    
    results = generate_docs_for_tools(handler_files, output_dir)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)
    
    success_count = sum(1 for _, _, success in results if success)
    failed_count = len(results) - success_count
    
    print(f"✅ Successfully generated: {success_count}")
    print(f"❌ Failed: {failed_count}")
    
    if failed_count > 0:
        print("\nFailed tools:")
        for tool_name, _, success in results:
            if not success:
                print(f"  - {tool_name}")
    
    print("\n✨ Documentation generation complete!")


if __name__ == "__main__":
    main()
