#!/usr/bin/env python3
"""
一键生成 Coze handler 的入口脚本

功能：
- 扫描 backend/api 中的 POST 端点，生成对应工具到 coze_plugin/raw_tools
- 扫描 segment_schemas.py 中的自定义类，生成 make_* 工具
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _ensure_sys_path() -> Path:
    """确保 scripts 目录在 sys.path 中，以便导入 handler_generator 包。"""
    script_dir = Path(__file__).resolve().parent
    scripts_dir = script_dir.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return scripts_dir.parent


PROJECT_ROOT = _ensure_sys_path()

from handler_generator import (  # noqa: E402
    APIScanner,
    FolderCreator,
    InputOutputGenerator,
    HandlerFunctionGenerator,
    APICallCodeGenerator,
    SchemaExtractor,
    CustomClassHandlerGenerator,
)


def _generate_complete_handler(
    endpoint,
    input_output_gen: InputOutputGenerator,
    api_call_gen: APICallCodeGenerator,
    handler_func_gen: HandlerFunctionGenerator,
    schema_extractor: SchemaExtractor,
) -> str:
    """生成完整的 handler.py 内容（与 scripts/generate_handler_from_api.py 一致）。"""

    # 步骤 3：生成 Input 类
    input_class = input_output_gen.generate_input_class(endpoint)

    # 步骤 3：获取 Output 字段
    output_fields = input_output_gen.get_output_fields(endpoint)

    # 步骤 3：生成 Output 类
    output_class = input_output_gen.generate_output_class(endpoint, output_fields)

    # 步骤 4：生成 API 调用代码
    api_call_code = api_call_gen.generate_api_call_code(endpoint, output_fields)

    # 步骤 5：生成 handler 函数
    handler_func = handler_func_gen.generate_handler_function(
        endpoint, output_fields, api_call_code
    )

    # 收集所有自定义类型依赖
    custom_types = set()
    custom_types.update(input_output_gen.get_custom_types_from_input(endpoint))
    custom_types.update(input_output_gen.get_custom_types_from_output(endpoint))

    # 生成自定义类型的定义（复制到文件中，而不是import）
    custom_type_definitions = ""
    if custom_types:
        sorted_types = sorted(custom_types)
        type_defs = schema_extractor.get_multiple_class_sources(sorted_types)
        if type_defs:
            custom_type_definitions = (
                "\n# ========== 自定义类型定义 ==========\n"
                "# 以下类型定义从 segment_schemas.py 复制而来\n"
                "# Coze 平台不支持跨文件 import，因此需要在每个工具中重复定义\n\n"
                f"{type_defs}\n\n"
            )

    # 将 Windows 路径的反斜杠替换为正斜杠，避免字符串转义问题
    source_file_path = str(endpoint.source_file).replace("\\", "/")

    content = f'''"""
{endpoint.func_name} 工具处理器

自动从 API 端点生成: {endpoint.path}
源文件: {source_file_path}
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args

{custom_type_definitions}
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
from backend.schemas.segment_schemas import *

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


def generate_api_handlers(api_dir: Path, schema_file: Path, output_dir: Path) -> int:
    """生成 API handler。"""
    print("步骤 1: 扫描 API 端点...")
    scanner = APIScanner(str(api_dir))
    endpoints = scanner.scan_all()
    print()

    if not endpoints:
        print("未找到任何 POST API 端点")
        return 0

    print("步骤 2: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_file))
    print(f"加载了 {len(schema_extractor.schemas)} 个 schema 定义")
    print()

    print("步骤 3: 初始化生成器模块...")
    folder_creator = FolderCreator(str(output_dir), schema_extractor)
    input_output_gen = InputOutputGenerator(schema_extractor)
    api_call_gen = APICallCodeGenerator(schema_extractor)
    handler_func_gen = HandlerFunctionGenerator()
    print()

    print("步骤 4: 生成 handler.py 文件...")
    generated_count = 0

    for endpoint in endpoints:
        print(f"\n处理端点: {endpoint.func_name}")
        try:
            handler_content = _generate_complete_handler(
                endpoint,
                input_output_gen,
                api_call_gen,
                handler_func_gen,
                schema_extractor,
            )
            readme_content = folder_creator.generate_readme(endpoint)
            folder_creator.create_tool_folder(endpoint, handler_content, readme_content)
            generated_count += 1
        except Exception as e:
            print(f"  错误: 生成失败 - {e}")
            import traceback

            traceback.print_exc()

    print()
    print("=" * 60)
    print("API handler 生成完成！")
    print(f"成功生成 {generated_count}/{len(endpoints)} 个工具")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    return generated_count


def generate_custom_handlers(schema_file: Path, output_dir: Path) -> int:
    """生成自定义类 handler。"""
    print("步骤 1: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_file))
    print(f"加载了 {len(schema_extractor.schemas)} 个 schema 定义")
    print()

    print("步骤 2: 扫描自定义类...")
    generator = CustomClassHandlerGenerator(str(schema_file), schema_extractor)
    custom_classes = generator.scan_custom_classes()
    print(f"找到 {len(custom_classes)} 个目标自定义类")
    print()

    if not custom_classes:
        print("未找到任何目标自定义类")
        return 0

    print("步骤 3: 生成 handler.py 和 README.md 文件...")
    generated_count = 0

    for custom_class in custom_classes:
        print(f"\n处理自定义类: {custom_class.class_name} -> {custom_class.tool_name}")
        try:
            generator.create_tool_folder(custom_class, output_dir)
            generated_count += 1
        except Exception as e:
            print(f"  错误: 生成失败 - {e}")
            import traceback

            traceback.print_exc()

    print()
    print("=" * 60)
    print("自定义类 handler 生成完成！")
    print(f"成功生成 {generated_count}/{len(custom_classes)} 个工具")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    return generated_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Coze handler 一键生成脚本",
        epilog="示例: python scripts/handler_generator/main.py --clean",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="只生成 API handler（跳过自定义类 handler）",
    )
    parser.add_argument(
        "--custom-only",
        action="store_true",
        help="只生成自定义类 handler（跳过 API handler）",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="生成前清空 coze_plugin/raw_tools 目录",
    )
    args = parser.parse_args()

    if args.api_only and args.custom_only:
        print("参数冲突：--api-only 与 --custom-only 不能同时使用")
        raise SystemExit(1)

    api_dir = PROJECT_ROOT / "backend" / "api"
    schema_file = PROJECT_ROOT / "backend" / "schemas" / "segment_schemas.py"
    output_dir = PROJECT_ROOT / "coze_plugin" / "raw_tools"

    print("=" * 60)
    print("Coze Handler 一键生成器")
    print("=" * 60)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"API 目录: {api_dir}")
    print(f"Schema 文件: {schema_file}")
    print(f"输出目录: {output_dir}")
    print()

    if args.clean and output_dir.exists():
        print("清理输出目录...")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    total_generated = 0
    if not args.custom_only:
        total_generated += generate_api_handlers(api_dir, schema_file, output_dir)

    if not args.api_only:
        total_generated += generate_custom_handlers(schema_file, output_dir)

    print()
    print("=" * 60)
    print(f"全部完成！总共生成 {total_generated} 个工具")
    print("=" * 60)


if __name__ == "__main__":
    main()
