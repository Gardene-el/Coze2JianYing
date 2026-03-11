#!/usr/bin/env python3
"""
测试可选参数处理逻辑
验证 E 脚本生成的代码能够正确处理可选参数（跳过 None 值）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.handler_generator.api_endpoint_info import APIEndpointInfo
from scripts.handler_generator.generate_api_call_code import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor


def test_optional_params_detection():
    """测试可选参数检测逻辑"""
    print("=== 测试可选参数检测 ===\n")

    # 初始化 SchemaExtractor
    schema_file = project_root / "src" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))

    # 测试 CreateAudioSegmentRequest
    print("测试 CreateAudioSegmentRequest:")
    fields = extractor.get_schema_fields("CreateAudioSegmentRequest")

    generator = APICallCodeGenerator(extractor)

    for field in fields:
        is_optional = generator._is_optional_field(field)
        print(f"  {field['name']}: {field['type']}")
        print(f"    默认值: {field['default']}")
        print(f"    可选: {is_optional}")
        print()

    return True


def test_generated_request_construction():
    """测试生成的 request 构造代码"""
    print("\n=== 测试生成的 Request 构造代码 ===\n")

    # 初始化
    schema_file = project_root / "src" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    # 模拟 create_audio_segment API 端点
    endpoint = APIEndpointInfo(
        func_name="create_audio_segment",
        path="/audio_segments",
        has_draft_id=False,
        has_segment_id=False,
        request_model="CreateAudioSegmentRequest",
        response_model="CreateSegmentResponse",
        path_params=[],
        source_file="app/backend/api/router.py",
    )

    # 获取 output 字段（假设返回 segment_id）
    output_fields = [
        {"name": "segment_id", "type": "str"},
        {"name": "message", "type": "str"},
    ]

    # 生成 API 调用代码
    api_call_code = generator.generate_api_call_code(endpoint, output_fields)

    print("生成的代码:")
    print("-" * 60)
    print(api_call_code)
    print("-" * 60)

    # 检查关键特征
    checks = [
        (
            "包含 req_params 字典初始化（空字典使用双大括号）",
            "req_params_{generated_uuid} = {{}}" in api_call_code,
        ),
        ("包含可选参数检查", "is not None:" in api_call_code),
        (
            "使用字典解包（插值表达式使用单大括号）",
            "**req_params_{generated_uuid}" in api_call_code,
        ),
        (
            "插值表达式使用单大括号",
            "{generated_uuid}" in api_call_code
            and "{{generated_uuid}}" not in api_call_code,
        ),
    ]

    print("\n代码检查:")
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed


def test_field_type_formatting():
    """测试字段类型格式化"""
    print("\n=== 测试字段类型格式化 ===\n")

    schema_file = project_root / "src" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    test_cases = [
        ("material_url", "str", True),  # 字符串需要引号
        ("speed", "float", False),  # 数字不需要引号
        ("volume", "float", False),
        ("change_pitch", "bool", False),
        ("track_name", "Optional[str]", True),  # 可选字符串需要引号
        ("width", "int", False),
    ]

    print("注意：格式化的值包含 f-string 插值表达式（单大括号）")

    print("类型格式化测试:")
    all_passed = True
    for field_name, field_type, should_quote in test_cases:
        formatted = generator._format_param_value(field_name, field_type)
        has_quotes = formatted.startswith('"')

        status = "✅" if (has_quotes == should_quote) else "❌"
        print(f"  {status} {field_name} ({field_type}): {formatted}")

        if has_quotes != should_quote:
            all_passed = False
            expected = "有引号" if should_quote else "无引号"
            actual = "有引号" if has_quotes else "无引号"
            print(f"      期望: {expected}, 实际: {actual}")

    return all_passed


def test_runtime_behavior_simulation():
    """测试运行时行为模拟（检查生成的代码逻辑）"""
    print("\n=== 测试运行时行为模拟 ===\n")

    schema_file = project_root / "src" / "schemas" / "general_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    # 模拟端点
    endpoint = APIEndpointInfo(
        func_name="create_audio_segment",
        path="/audio_segments",
        has_draft_id=False,
        has_segment_id=False,
        request_model="CreateAudioSegmentRequest",
        response_model="CreateSegmentResponse",
        path_params=[],
        source_file="app/backend/api/router.py",
    )

    output_fields = [
        {"name": "segment_id", "type": "str"},
        {"name": "message", "type": "str"},
    ]

    # 生成代码
    api_call_code = generator.generate_api_call_code(endpoint, output_fields)

    # 检查关键特性
    checks = [
        (
            "必需字段直接赋值",
            "req_params_{generated_uuid}['material_url']" in api_call_code,
        ),
        (
            "可选字段有 None 检查或 _is_meaningful_object 检查",
            "if {args.input.source_timerange} is not None:" in api_call_code
            or "if {_is_meaningful_object(args.input.source_timerange)}:" in api_call_code,
        ),
        ("使用字典解包", "**req_params_{generated_uuid}" in api_call_code),
        ("字符串类型有引号", '"{args.input.material_url}"' in api_call_code),
        (
            "数字类型无引号",
            "{args.input.speed}" in api_call_code
            and '"{args.input.speed}"' not in api_call_code,
        ),
        ("插值表达式使用单大括号", "{generated_uuid}" in api_call_code),
        ("空字典使用双大括号转义", "= {{}}" in api_call_code),
    ]

    print("运行时行为检查:")
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed


def main():
    """运行所有测试"""
    print("=" * 60)
    print("可选参数处理逻辑测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("可选参数检测", test_optional_params_detection()))
    results.append(("Request 构造代码生成", test_generated_request_construction()))
    results.append(("字段类型格式化", test_field_type_formatting()))
    results.append(("运行时行为模拟", test_runtime_behavior_simulation()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查实现")
        return 1


if __name__ == "__main__":
    sys.exit(main())
