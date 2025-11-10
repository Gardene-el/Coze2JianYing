#!/usr/bin/env python3
"""
Handler Generator - 主程序
使用 A-E 五个脚本模块，从 API 端点自动生成 Coze handler

模块说明:
- A 脚本 (a_api_scanner.py): 扫描 /app/api 下所有 POST API 函数
- B 脚本 (b_folder_creator.py): 创建工具文件夹，生成 handler.py 和 README.md
- C 脚本 (c_input_output_generator.py): 定义 Input/Output 类型
- D 脚本 (d_handler_function_generator.py): 生成 handler 函数
- E 脚本 (e_api_call_code_generator.py): 生成 API 调用记录代码
"""

from pathlib import Path
from handler_generator import (
    APIScanner,
    FolderCreator,
    InputOutputGenerator,
    HandlerFunctionGenerator,
    APICallCodeGenerator,
    SchemaExtractor,
)


def generate_complete_handler(endpoint, input_output_gen, api_call_gen, handler_func_gen):
    """生成完整的 handler.py 内容"""
    
    # C 脚本：生成 Input 类
    input_class = input_output_gen.generate_input_class(endpoint)
    
    # C 脚本：获取 Output 字段
    output_fields = input_output_gen.get_output_fields(endpoint)
    
    # C 脚本：生成 Output 类
    output_class = input_output_gen.generate_output_class(endpoint, output_fields)
    
    # E 脚本：生成 API 调用代码
    api_call_code = api_call_gen.generate_api_call_code(endpoint, output_fields)
    
    # D 脚本：生成 handler 函数
    handler_func = handler_func_gen.generate_handler_function(endpoint, output_fields, api_call_code)
    
    # 组合完整内容
    content = f'''"""
{endpoint.func_name} 工具处理器

自动从 API 端点生成: {endpoint.path}
源文件: {endpoint.source_file}
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args


# Input 类型定义
{input_class}


# Output 类型定义
{output_class}


def ensure_coze2jianying_file() -> str:
    """
    确保 /tmp 目录下存在 coze2jianying.py 文件
    
    Returns:
        coze2jianying.py 文件的完整路径
    """
    file_path = "/tmp/coze2jianying.py"
    
    if not os.path.exists(file_path):
        # 创建初始文件内容
        initial_content = """# Coze2JianYing API 调用记录
# 此文件由 Coze 工具自动生成和更新
# 记录所有通过 Coze 工具调用的 API 操作

import asyncio
from app.schemas.segment_schemas import *

# API 调用记录将追加在下方
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    
    return file_path


def append_api_call_to_file(file_path: str, api_call_code: str):
    """
    将 API 调用代码追加到 coze2jianying.py 文件
    
    Args:
        file_path: coze2jianying.py 文件路径
        api_call_code: 要追加的 API 调用代码
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\\n" + api_call_code + "\\n")


{handler_func}
'''
    return content


def main():
    """主函数：执行完整的生成流程"""
    print("=" * 60)
    print("Coze Handler 生成器")
    print("根据 API 端点自动生成 Coze 工具 handler.py")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 定义路径
    api_dir = project_root / 'app' / 'api'
    schema_file = project_root / 'app' / 'schemas' / 'segment_schemas.py'
    output_dir = project_root / 'coze_plugin' / 'raw_tools'
    
    print(f"项目根目录: {project_root}")
    print(f"API 目录: {api_dir}")
    print(f"Schema 文件: {schema_file}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # A 脚本：扫描 API 端点
    print("步骤 1: 扫描 API 端点 (A 脚本)...")
    scanner = APIScanner(str(api_dir))
    endpoints = scanner.scan_all()
    print()
    
    if not endpoints:
        print("未找到任何 POST API 端点")
        return
    
    # 加载 schema 信息
    print("步骤 2: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_file))
    print(f"加载了 {len(schema_extractor.schemas)} 个 schema 定义")
    print()
    
    # 初始化各个脚本模块
    print("步骤 3: 初始化生成器模块...")
    folder_creator = FolderCreator(str(output_dir))  # B 脚本
    input_output_gen = InputOutputGenerator(schema_extractor)  # C 脚本
    api_call_gen = APICallCodeGenerator(schema_extractor)  # E 脚本
    handler_func_gen = HandlerFunctionGenerator()  # D 脚本
    print()
    
    # 生成 handler 文件
    print("步骤 4: 生成 handler.py 文件 (B/C/D/E 脚本)...")
    generated_count = 0
    
    for endpoint in endpoints:
        print(f"\n处理端点: {endpoint.func_name}")
        try:
            # 生成完整的 handler 内容
            handler_content = generate_complete_handler(
                endpoint, input_output_gen, api_call_gen, handler_func_gen
            )
            
            # B 脚本：生成 README 内容
            readme_content = folder_creator.generate_readme(endpoint)
            
            # B 脚本：创建文件夹和文件
            folder_creator.create_tool_folder(endpoint, handler_content, readme_content)
            
            generated_count += 1
        except Exception as e:
            print(f"  错误: 生成失败 - {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    print(f"生成完成！")
    print(f"成功生成 {generated_count}/{len(endpoints)} 个工具")
    print(f"输出目录: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
