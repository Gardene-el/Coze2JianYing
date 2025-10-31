#!/usr/bin/env python3
"""
Tool Documentation Generator for Coze Plugin

This script generates documentation for a Coze plugin tool by parsing its handler.py file.
It extracts:
1. Tool name from the folder name
2. Tool description from the module-level docstring
3. Input parameters from the Input class definition
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


def extract_module_docstring(handler_path: str) -> str:
    """
    Extract the module-level docstring from handler.py
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        The module docstring content, or empty string if not found
    """
    try:
        with open(handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to get the AST
        tree = ast.parse(content)
        
        # Get the module docstring (first string literal in the module)
        docstring = ast.get_docstring(tree)
        
        if docstring:
            # Clean up the docstring - remove extra whitespace and newlines
            # Keep the basic structure but make it more readable
            lines = docstring.strip().split('\n')
            # Remove empty lines at start and end, but keep internal structure
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            return '\n'.join(line.strip() for line in lines if line.strip())
        
        return ""
    except Exception as e:
        print(f"Error extracting docstring: {e}")
        return ""


def extract_class_parameters(handler_path: str, class_name: str) -> List[Dict[str, Any]]:
    """
    Extract parameters from a NamedTuple class (Input or Output) in handler.py
    
    Args:
        handler_path: Path to handler.py file
        class_name: Name of the class to extract ('Input' or 'Output')
        
    Returns:
        List of parameter dictionaries with keys: name, type, default, comment
    """
    try:
        with open(handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to get the AST
        tree = ast.parse(content)
        
        # Find the specified class
        target_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                target_class = node
                break
        
        if not target_class:
            return []
        
        parameters = []
        
        # Extract from NamedTuple style class definition
        # Look for annotated assignments (field: type = default)
        for item in target_class.body:
            if isinstance(item, ast.AnnAssign):
                param_info = {}
                
                # Get parameter name
                if isinstance(item.target, ast.Name):
                    param_info['name'] = item.target.id
                
                # Get parameter type
                param_info['type'] = ast.unparse(item.annotation)
                
                # Get default value if exists
                if item.value:
                    try:
                        param_info['default'] = ast.unparse(item.value)
                    except:
                        param_info['default'] = 'N/A'
                else:
                    param_info['default'] = 'N/A'
                
                # Try to get inline comment (if any)
                # This requires parsing comments from the source
                param_info['comment'] = ''
                
                parameters.append(param_info)
        
        # Try to extract comments from source code
        lines = content.split('\n')
        for param in parameters:
            param_name = param['name']
            # Find lines with the parameter name
            for line in lines:
                if f"{param_name}:" in line and "#" in line:
                    # Extract comment after #
                    comment_match = re.search(r'#\s*(.+)$', line)
                    if comment_match:
                        param['comment'] = comment_match.group(1).strip()
                        break
        
        return parameters
        
    except Exception as e:
        print(f"Error extracting {class_name} parameters: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_input_parameters(handler_path: str) -> List[Dict[str, Any]]:
    """
    Extract Input class parameters from handler.py
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        List of parameter dictionaries with keys: name, type, default, comment
    """
    return extract_class_parameters(handler_path, 'Input')


def extract_output_parameters(handler_path: str) -> List[Dict[str, Any]]:
    """
    Extract Output class parameters from handler.py
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        List of parameter dictionaries with keys: name, type, default, comment
    """
    return extract_class_parameters(handler_path, 'Output')


def check_output_type(handler_path: str) -> str:
    """
    Check if Output is defined as NamedTuple or Dict[str, Any]
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        'NamedTuple' if Output class exists, 'Dict' if using Dict[str, Any], or 'Unknown'
    """
    try:
        with open(handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Output class definition
        if 'class Output(NamedTuple):' in content or 'class Output(NamedTuple)' in content:
            return 'NamedTuple'
        
        # Check for Dict[str, Any] pattern in comments or return type
        if 'Output is now returned as Dict[str, Any]' in content or \
           'returned as Dict[str, Any]' in content or \
           '-> Dict[str, Any]' in content:
            return 'Dict'
        
        return 'Unknown'
        
    except Exception as e:
        print(f"Error checking output type: {e}")
        return 'Unknown'


def get_tool_name_from_path(handler_path: str) -> str:
    """
    Extract tool name from the handler.py file path
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        Tool name (folder name containing handler.py)
    """
    # Get the parent directory name
    path = Path(handler_path)
    return path.parent.name


def format_tool_name_display(tool_name: str) -> str:
    """
    Format tool name for display (convert snake_case to Title Case)
    
    Args:
        tool_name: Tool name in snake_case
        
    Returns:
        Formatted tool name for display
    """
    # Split by underscore and capitalize each word
    words = tool_name.split('_')
    return ' '.join(word.capitalize() for word in words)


def generate_documentation(handler_path: str) -> str:
    """
    Generate documentation for a tool from its handler.py file
    
    Args:
        handler_path: Path to handler.py file
        
    Returns:
        Generated documentation as a string
    """
    # Extract information
    tool_name = get_tool_name_from_path(handler_path)
    tool_display_name = format_tool_name_display(tool_name)
    description = extract_module_docstring(handler_path)
    input_parameters = extract_input_parameters(handler_path)
    output_parameters = extract_output_parameters(handler_path)
    output_type = check_output_type(handler_path)
    
    # Build documentation
    doc_lines = []
    
    # Title
    doc_lines.append(f"# 工具函数 {tool_display_name}")
    doc_lines.append("")
    
    # Tool name and description
    doc_lines.append(f"工具名称：{tool_name}")
    doc_lines.append(f"工具描述：{description}")
    doc_lines.append("")
    
    # Input parameters section
    if input_parameters:
        doc_lines.append("## 输入参数")
        doc_lines.append("")
        doc_lines.append("```python")
        doc_lines.append("class Input(NamedTuple):")
        for param in input_parameters:
            # Format parameter line
            param_line = f"    {param['name']}: {param['type']}"
            if param['default'] != 'N/A':
                param_line += f" = {param['default']}"
            if param['comment']:
                param_line += f"  # {param['comment']}"
            doc_lines.append(param_line)
        doc_lines.append("```")
        doc_lines.append("")
    
    # Output parameters section
    if output_parameters and output_type == 'NamedTuple':
        doc_lines.append("## 输出参数")
        doc_lines.append("")
        doc_lines.append("```python")
        doc_lines.append("class Output(NamedTuple):")
        for param in output_parameters:
            # Format parameter line
            param_line = f"    {param['name']}: {param['type']}"
            if param['default'] != 'N/A':
                param_line += f" = {param['default']}"
            if param['comment']:
                param_line += f"  # {param['comment']}"
            doc_lines.append(param_line)
        doc_lines.append("```")
        doc_lines.append("")
    elif output_type == 'Dict':
        doc_lines.append("## 输出参数")
        doc_lines.append("")
        doc_lines.append("```python")
        doc_lines.append("# Output is returned as Dict[str, Any]")
        doc_lines.append("# Common fields:")
        doc_lines.append("#   success: bool    # Operation success status")
        doc_lines.append("#   message: str     # Status message")
        doc_lines.append("#   [other fields]   # Tool-specific return data")
        doc_lines.append("```")
        doc_lines.append("")
    
    return '\n'.join(doc_lines)


def main():
    """Main function to generate documentation"""
    if len(sys.argv) < 2:
        print("Usage: python generate_tool_doc.py <path_to_handler.py> [output_file]")
        print("\nExample:")
        print("  python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py")
        print("  python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py output.md")
        sys.exit(1)
    
    handler_path = sys.argv[1]
    
    # Validate handler path
    if not os.path.exists(handler_path):
        print(f"Error: File not found: {handler_path}")
        sys.exit(1)
    
    if not handler_path.endswith('handler.py'):
        print(f"Warning: File does not end with 'handler.py': {handler_path}")
    
    # Generate documentation
    doc_content = generate_documentation(handler_path)
    
    # Determine output file
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default: create in the same directory as handler.py with _generated.md suffix
        tool_name = get_tool_name_from_path(handler_path)
        output_file = os.path.join(os.path.dirname(handler_path), f"{tool_name}_generated.md")
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        print(f"✅ Documentation generated successfully!")
        print(f"📄 Output file: {output_file}")
        print(f"\n{'='*60}")
        print("Preview:")
        print('='*60)
        print(doc_content)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
