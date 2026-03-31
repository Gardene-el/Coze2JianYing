#!/usr/bin/env python3
"""
一键生成 Coze handler 的入口脚本

功能：
- 扫描 app/backend/api 中的 POST 端点，生成对应工具到 coze_plugin/raw_tools
- 扫描 general_schemas.py 中的自定义类，生成 make_* 工具

重构说明：
  使用 Jinja2 模板引擎替代 f-string 拼接，模板与逻辑分离。
  运行时辅助函数（_to_type_constructor 等）仅在 handler 使用复杂类型时注入。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


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

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Jinja2 环境 — 禁用自动转义、保持原始缩进
_JINJA_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def _generate_complete_handler(
    endpoint,
    input_output_gen: InputOutputGenerator,
    api_call_gen: APICallCodeGenerator,
    handler_func_gen: HandlerFunctionGenerator,
    schema_extractor: SchemaExtractor,
) -> str:
    """生成完整的 handler.py 内容。"""

    # 步骤 3：生成 Input / Output 类
    input_class = input_output_gen.generate_input_class(endpoint)
    output_fields = input_output_gen.get_output_fields(endpoint)
    output_class = input_output_gen.generate_output_class(endpoint, output_fields)

    # 步骤 4：生成 API 调用代码
    api_call_code = api_call_gen.generate_api_call_code(endpoint, output_fields)

    # 步骤 5：生成 handler 函数
    handler_func = handler_func_gen.generate_handler_function(
        endpoint, output_fields, api_call_code
    )

    # 收集自定义类型依赖
    custom_types = set()
    custom_types.update(input_output_gen.get_custom_types_from_input(endpoint))
    custom_types.update(input_output_gen.get_custom_types_from_output(endpoint))

    custom_type_definitions = ""
    if custom_types:
        sorted_types = sorted(custom_types)
        type_defs = schema_extractor.get_multiple_class_sources(sorted_types)
        if type_defs:
            custom_type_definitions = type_defs

    # 判断是否需要运行时辅助函数（_to_type_constructor / _is_meaningful_object）
    # 规则：只要 Input 中存在自定义复杂类型字段就需要
    needs_runtime_helpers = bool(custom_types)

    # Windows 路径的反斜杠替换为正斜杠
    source_file_path = str(endpoint.source_file).replace("\\", "/")

    # 从模板文件读取文件工具函数
    file_utils_code = (_TEMPLATES_DIR / "file_utils.py").read_text(encoding="utf-8")

    # 运行时辅助函数（按需注入）
    runtime_helpers_code = ""
    if needs_runtime_helpers:
        runtime_helpers_code = (_TEMPLATES_DIR / "runtime_helpers.py").read_text(
            encoding="utf-8"
        )

    template = _JINJA_ENV.get_template("handler.py.j2")
    return template.render(
        endpoint=endpoint,
        source_file_path=source_file_path,
        custom_type_definitions=custom_type_definitions,
        input_class=input_class,
        output_class=output_class,
        file_utils_code=file_utils_code,
        needs_runtime_helpers=needs_runtime_helpers,
        runtime_helpers_code=runtime_helpers_code,
        handler_func=handler_func,
    )


def generate_api_handlers(api_dir: Path, schema_dir: Path, output_dir: Path) -> int:
    """生成 API handler。"""
    print("步骤 1: 扫描 API 端点...")
    scanner = APIScanner(str(api_dir))
    endpoints = scanner.scan_all()
    print()

    if not endpoints:
        print("未找到任何 POST API 端点")
        return 0

    print("步骤 2: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_dir))
    # 补充加载 common_types.py 中的自定义类型（TimeRange 等）
    common_types_file = schema_dir.parent / "core" / "common_types.py"
    schema_extractor.load_additional_file(common_types_file)
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


def generate_custom_handlers(schema_dir: Path, output_dir: Path) -> int:
    """生成自定义类 handler。"""
    print("步骤 1: 加载 Schema 信息...")
    # SchemaExtractor 需要扫描 schemas 目录以获取字段定义
    schema_extractor = SchemaExtractor(str(schema_dir))
    # 补充加载 common_types.py 中的自定义类型（TimeRange 等）
    common_types_path = schema_dir.parent / "core" / "common_types.py"
    schema_extractor.load_additional_file(common_types_path)
    print()

    print("步骤 2: 扫描自定义类...")
    # 自定义类型定义在 core/common_types.py，而非 schemas 目录
    common_types_path = schema_dir.parent / "core" / "common_types.py"
    scan_source = str(common_types_path) if common_types_path.exists() else str(schema_dir)
    generator = CustomClassHandlerGenerator(scan_source, schema_extractor)
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

    api_dir = PROJECT_ROOT / "src" / "backend" / "api"
    schema_dir = PROJECT_ROOT / "src" / "backend" / "schemas"
    output_dir = PROJECT_ROOT / "plugins" / "coze"

    print("=" * 60)
    print("Coze Handler 一键生成器")
    print("=" * 60)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"API 目录: {api_dir}")
    print(f"Schema 目录: {schema_dir}")
    print(f"输出目录: {output_dir}")
    print()

    if args.clean and output_dir.exists():
        print("清理输出目录...")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    total_generated = 0
    if not args.custom_only:
        total_generated += generate_api_handlers(api_dir, schema_dir, output_dir)

    if not args.api_only:
        total_generated += generate_custom_handlers(schema_dir, output_dir)

    print()
    print("=" * 60)
    print(f"全部完成！总共生成 {total_generated} 个工具")
    print("=" * 60)


if __name__ == "__main__":
    main()
