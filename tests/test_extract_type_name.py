#!/usr/bin/env python3
"""
测试类型名提取功能

验证 E 脚本中的 _extract_type_name 方法能够正确从各种类型字符串中提取核心类型名
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.handler_generator.generate_api_call_code import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor


def test_extract_type_name():
    """测试 _extract_type_name 方法"""
    print("=== 测试 _extract_type_name 方法 ===\n")

    # 创建一个测试用的 schema extractor（不需要实际文件）
    # 我们只需要测试 APICallCodeGenerator 的方法
    class MockSchemaExtractor:
        pass

    generator = APICallCodeGenerator(MockSchemaExtractor())

    test_cases = [
        # (输入类型字符串, 期望输出类型名)
        # 注意：List[str], Dict[str, int] 等基本类型容器不会调用 _extract_type_name
        # 因为它们在 _is_complex_type 中就被判定为非复杂类型
        # 这里测试的是当需要提取类型名时的行为
        ("TimeRange", "TimeRange"),
        ("Optional[TimeRange]", "TimeRange"),
        ("Optional[ClipSettings]", "ClipSettings"),
        ("List[ClipSettings]", "ClipSettings"),
        ("Optional[List[ClipSettings]]", "ClipSettings"),
        ("Optional[Dict[str, TimeRange]]", "TimeRange"),
        ("str", "str"),
        ("int", "int"),
        ("float", "float"),
        ("bool", "bool"),
        ("TextStyle", "TextStyle"),
        ("Optional[TextStyle]", "TextStyle"),
        ("Position", "Position"),
        ("Optional[Position]", "Position"),
    ]

    all_passed = True

    for type_string, expected in test_cases:
        result = generator._extract_type_name(type_string)
        passed = result == expected

        status = "✅" if passed else "❌"
        print(f"{status} {type_string:35} -> {result:20} (期望: {expected})")

        if not passed:
            all_passed = False

    print()
    return all_passed


def test_is_complex_type():
    """测试 _is_complex_type 方法"""
    print("=== 测试 _is_complex_type 方法 ===\n")

    class MockSchemaExtractor:
        pass

    generator = APICallCodeGenerator(MockSchemaExtractor())

    test_cases = [
        # (类型字符串, 是否为复杂类型)
        ("str", False),
        ("int", False),
        ("float", False),
        ("bool", False),
        ("List[str]", False),
        ("Dict[str, int]", False),
        ("Optional[int]", False),
        ("Optional[str]", False),
        ("TimeRange", True),
        ("Optional[TimeRange]", True),
        ("ClipSettings", True),
        ("Optional[ClipSettings]", True),
        ("TextStyle", True),
        ("Position", True),
        ("List[ClipSettings]", True),  # 虽然是 List，但内部是复杂类型
        ("Optional[List[TimeRange]]", True),
    ]

    all_passed = True

    for type_string, expected in test_cases:
        result = generator._is_complex_type(type_string)
        passed = result == expected

        status = "✅" if passed else "❌"
        result_str = "复杂类型" if result else "基本类型"
        expected_str = "复杂类型" if expected else "基本类型"
        print(f"{status} {type_string:35} -> {result_str:10} (期望: {expected_str})")

        if not passed:
            all_passed = False

    print()
    return all_passed


def test_format_param_value():
    """测试 _format_param_value 方法"""
    print("=== 测试 _format_param_value 方法 ===\n")

    class MockSchemaExtractor:
        pass

    generator = APICallCodeGenerator(MockSchemaExtractor())

    test_cases = [
        # (字段名, 字段类型, 期望输出模式)
        ("material_url", "str", '"{args.input.material_url}"'),
        ("speed", "float", "{args.input.speed}"),
        ("volume", "int", "{args.input.volume}"),
        ("change_pitch", "bool", "{args.input.change_pitch}"),
        (
            "target_timerange",
            "TimeRange",
            "{_to_type_constructor(args.input.target_timerange, 'TimeRange')}",
        ),
        (
            "clip_settings",
            "Optional[ClipSettings]",
            "{_to_type_constructor(args.input.clip_settings, 'ClipSettings')}",
        ),
        (
            "text_style",
            "Optional[TextStyle]",
            "{_to_type_constructor(args.input.text_style, 'TextStyle')}",
        ),
    ]

    all_passed = True

    for field_name, field_type, expected in test_cases:
        result = generator._format_param_value(field_name, field_type)
        passed = result == expected

        status = "✅" if passed else "❌"
        print(f"{status} {field_name} ({field_type})")
        print(f"   输出: {result}")
        if not passed:
            print(f"   期望: {expected}")
            all_passed = False
        print()

    return all_passed


def main():
    """运行所有测试"""
    print("=" * 70)
    print("类型名提取功能测试")
    print("=" * 70)
    print()

    results = []

    try:
        results.append(("类型名提取", test_extract_type_name()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("类型名提取", False))

    try:
        results.append(("复杂类型判断", test_is_complex_type()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("复杂类型判断", False))

    try:
        results.append(("参数值格式化", test_format_param_value()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("参数值格式化", False))

    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 测试通过")

    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
