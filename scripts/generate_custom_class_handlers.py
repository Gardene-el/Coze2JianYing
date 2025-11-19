#!/usr/bin/env python3
"""
Custom Class Handler Generator - 主程序
为 segment_schemas.py 中的自定义类生成 Coze handler

此脚本专门用于生成自定义类（TimeRange, ClipSettings, TextStyle, CropSettings）的 handler。
这些 handler 与 API handler 不同，它们只是简单的对象构造器。

使用方法:
    python scripts/generate_custom_class_handlers.py
"""

from pathlib import Path
import sys

# 添加项目根目录到路径，以便导入 handler_generator 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from handler_generator import (
    CustomClassHandlerGenerator,
    SchemaExtractor,
)


def main():
    """主函数：执行完整的生成流程"""
    print("=" * 60)
    print("自定义类 Handler 生成器")
    print("为 segment_schemas.py 中的自定义类生成 Coze 工具")
    print("=" * 60)
    print()

    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # 定义路径
    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    output_dir = project_root / "coze_plugin" / "raw_tools"

    print(f"项目根目录: {project_root}")
    print(f"Schema 文件: {schema_file}")
    print(f"输出目录: {output_dir}")
    print()

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载 schema 信息
    print("步骤 1: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_file))
    print(f"加载了 {len(schema_extractor.schemas)} 个 schema 定义")
    print()

    # 初始化自定义类生成器
    print("步骤 2: 扫描自定义类...")
    generator = CustomClassHandlerGenerator(str(schema_file), schema_extractor)
    custom_classes = generator.scan_custom_classes()
    print(f"找到 {len(custom_classes)} 个目标自定义类")
    print()

    if not custom_classes:
        print("未找到任何目标自定义类")
        return

    # 生成 handler 文件
    print("步骤 3: 生成 handler.py 和 README.md 文件...")
    generated_count = 0

    for custom_class in custom_classes:
        print(f"\n处理自定义类: {custom_class.class_name} -> {custom_class.tool_name}")
        try:
            # 创建工具文件夹和文件
            generator.create_tool_folder(custom_class, output_dir)
            generated_count += 1
        except Exception as e:
            print(f"  错误: 生成失败 - {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print(f"生成完成！")
    print(f"成功生成 {generated_count}/{len(custom_classes)} 个工具")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    print()
    print("生成的工具:")
    for custom_class in custom_classes:
        tool_path = output_dir / custom_class.tool_name
        print(f"  - {custom_class.tool_name:20s} -> {tool_path}")


if __name__ == "__main__":
    main()
