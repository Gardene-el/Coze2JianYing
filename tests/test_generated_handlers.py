#!/usr/bin/env python3
"""
测试自动生成的 handler.py 文件
验证生成的代码语法正确性和基本功能
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Tuple


def test_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """
    测试 Python 文件语法是否正确
    
    Returns:
        (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"解析错误: {e}"


def test_handler_structure(file_path: Path) -> Tuple[bool, str]:
    """
    测试 handler.py 是否包含必需的结构
    - Input 类
    - handler 函数
    - ensure_coze2jianying_file 函数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
        
        has_input_class = False
        has_handler_func = False
        has_ensure_func = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == 'Input':
                    has_input_class = True
            elif isinstance(node, ast.FunctionDef):
                if node.name == 'handler':
                    has_handler_func = True
                elif node.name == 'ensure_coze2jianying_file':
                    has_ensure_func = True
        
        if not has_input_class:
            return False, "缺少 Input 类定义"
        if not has_handler_func:
            return False, "缺少 handler 函数"
        if not has_ensure_func:
            return False, "缺少 ensure_coze2jianying_file 函数"
        
        return True, ""
    
    except Exception as e:
        return False, f"结构检查失败: {e}"


def test_readme_exists(tool_dir: Path) -> Tuple[bool, str]:
    """
    测试是否存在 README.md
    """
    readme_path = tool_dir / 'README.md'
    if not readme_path.exists():
        return False, "缺少 README.md 文件"
    
    # 检查 README 不是空文件
    if readme_path.stat().st_size == 0:
        return False, "README.md 是空文件"
    
    return True, ""


def test_all_handlers(raw_tools_dir: Path) -> dict:
    """
    测试所有生成的 handlers
    
    Returns:
        测试结果字典
    """
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 遍历所有工具目录
    tool_dirs = [d for d in raw_tools_dir.iterdir() if d.is_dir()]
    
    for tool_dir in sorted(tool_dirs):
        results['total'] += 1
        tool_name = tool_dir.name
        handler_path = tool_dir / 'handler.py'
        
        print(f"\n测试工具: {tool_name}")
        
        # 检查 handler.py 是否存在
        if not handler_path.exists():
            results['failed'] += 1
            results['details'].append({
                'tool': tool_name,
                'status': 'failed',
                'reason': 'handler.py 不存在'
            })
            print(f"  ❌ handler.py 不存在")
            continue
        
        # 测试语法
        is_valid, error = test_python_syntax(handler_path)
        if not is_valid:
            results['failed'] += 1
            results['details'].append({
                'tool': tool_name,
                'status': 'failed',
                'reason': error
            })
            print(f"  ❌ 语法错误: {error}")
            continue
        print(f"  ✓ 语法正确")
        
        # 测试结构
        is_valid, error = test_handler_structure(handler_path)
        if not is_valid:
            results['failed'] += 1
            results['details'].append({
                'tool': tool_name,
                'status': 'failed',
                'reason': error
            })
            print(f"  ❌ 结构错误: {error}")
            continue
        print(f"  ✓ 结构完整")
        
        # 测试 README
        is_valid, error = test_readme_exists(tool_dir)
        if not is_valid:
            results['failed'] += 1
            results['details'].append({
                'tool': tool_name,
                'status': 'failed',
                'reason': error
            })
            print(f"  ❌ README 错误: {error}")
            continue
        print(f"  ✓ README 存在")
        
        # 所有测试通过
        results['passed'] += 1
        results['details'].append({
            'tool': tool_name,
            'status': 'passed'
        })
        print(f"  ✅ 所有测试通过")
    
    return results


def print_summary(results: dict):
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总计: {results['total']} 个工具")
    print(f"通过: {results['passed']} 个")
    print(f"失败: {results['failed']} 个")
    print(f"成功率: {results['passed']/results['total']*100:.1f}%")
    
    if results['failed'] > 0:
        print("\n失败的工具:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                print(f"  - {detail['tool']}: {detail.get('reason', '未知错误')}")
    
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("测试自动生成的 Handler 文件")
    print("=" * 60)
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    raw_tools_dir = project_root / 'coze_plugin' / 'raw_tools'
    
    print(f"\n项目根目录: {project_root}")
    print(f"Raw Tools 目录: {raw_tools_dir}")
    
    # 检查目录是否存在
    if not raw_tools_dir.exists():
        print(f"\n错误: {raw_tools_dir} 目录不存在")
        print("请先运行 generate_handler_from_api.py 生成 handler 文件")
        return 1
    
    # 运行测试
    results = test_all_handlers(raw_tools_dir)
    
    # 打印总结
    print_summary(results)
    
    # 返回适当的退出代码
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
