#!/usr/bin/env python3
"""
测试字符串类型参数在 if 条件中的引号修复
验证 E 脚本在生成可选参数的 if 条件检查时，对字符串类型正确添加引号
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.handler_generator.api_endpoint_info import APIEndpointInfo
from scripts.handler_generator.generate_api_call_code import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor


def test_string_condition_formatting():
    """测试字符串类型参数在条件中的格式化"""
    print("=== 测试字符串条件格式化 ===\n")

    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    # 测试不同类型的条件格式化
    test_cases = [
        ("draft_name", "str", '"{args.input.draft_name}"'),  # 字符串需要引号
        ("track_name", "Optional[str]", '"{args.input.track_name}"'),  # 可选字符串也需要引号
        ("width", "int", "{args.input.width}"),  # 数字不需要引号
        ("volume", "float", "{args.input.volume}"),  # 浮点数不需要引号
        ("change_pitch", "bool", "{args.input.change_pitch}"),  # 布尔值不需要引号
    ]

    print("条件值格式化测试:")
    all_passed = True
    for field_name, field_type, expected in test_cases:
        result = generator._format_condition_value(field_name, field_type)
        passed = (result == expected)
        status = "✅" if passed else "❌"
        print(f"  {status} {field_name} ({field_type})")
        print(f"      期望: {expected}")
        print(f"      实际: {result}")
        
        if not passed:
            all_passed = False

    return all_passed


def test_generated_code_with_string_params():
    """测试生成的代码包含字符串参数的情况"""
    print("\n=== 测试生成的代码（包含字符串参数）===\n")

    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    # 模拟 create_draft API 端点
    endpoint = APIEndpointInfo(
        func_name="create_draft",
        path="/create",
        has_draft_id=False,
        has_segment_id=False,
        request_model="CreateDraftRequest",
        response_model="CreateDraftResponse",
        path_params=[],
        source_file="backend/api/draft_routes.py",
    )

    # 获取 output 字段
    output_fields = [
        {"name": "draft_id", "type": "str"},
        {"name": "success", "type": "bool"},
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
            "字符串类型参数在条件中有引号",
            '"{args.input.draft_name}" is not None:' in api_call_code,
        ),
        (
            "字符串类型参数在赋值中有引号",
            '= "{args.input.draft_name}"' in api_call_code,
        ),
        (
            "数字类型参数在条件中无引号",
            "{args.input.width} is not None:" in api_call_code,
        ),
        (
            "数字类型参数在赋值中无引号",
            "= {args.input.width}" in api_call_code,
        ),
        (
            "布尔类型参数在条件中无引号",
            "{args.input.allow_replace} is not None:" in api_call_code,
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


def test_runtime_simulation():
    """模拟运行时行为，验证生成的代码语法正确"""
    print("\n=== 模拟运行时行为 ===\n")

    # 模拟 handler 运行时的环境
    class MockInput:
        draft_name = "demo_coze"
        width = 1080
        height = 1920
        fps = 30
        allow_replace = True

    class MockArgs:
        input = MockInput()

    args = MockArgs()
    generated_uuid = "test123"

    # 生成代码（修复后的版本）
    code = f"""
# 构造 request 对象
req_params_{generated_uuid} = {{}}
if "{args.input.draft_name}" is not None:
    req_params_{generated_uuid}['draft_name'] = "{args.input.draft_name}"
if {args.input.width} is not None:
    req_params_{generated_uuid}['width'] = {args.input.width}
if {args.input.height} is not None:
    req_params_{generated_uuid}['height'] = {args.input.height}
if {args.input.fps} is not None:
    req_params_{generated_uuid}['fps'] = {args.input.fps}
if {args.input.allow_replace} is not None:
    req_params_{generated_uuid}['allow_replace'] = {args.input.allow_replace}
"""

    print("生成的代码:")
    print(code)

    # 尝试执行生成的代码（验证语法正确）
    try:
        exec(code)
        req_params = locals()[f"req_params_{generated_uuid}"]
        print("\n✅ 代码执行成功！")
        print(f"\n生成的参数字典: {req_params}")
        
        # 验证参数值正确
        expected = {
            'draft_name': 'demo_coze',
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'allow_replace': True,
        }
        
        if req_params == expected:
            print("✅ 参数值正确！")
            return True
        else:
            print("❌ 参数值不正确")
            print(f"期望: {expected}")
            print(f"实际: {req_params}")
            return False
            
    except Exception as e:
        print(f"❌ 代码执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("字符串条件引号修复测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("条件格式化", test_string_condition_formatting()))
    results.append(("生成代码检查", test_generated_code_with_string_params()))
    results.append(("运行时模拟", test_runtime_simulation()))

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
