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
from scripts.handler_generator.e_api_call_code_generator import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor


def test_string_condition_formatting():
    """测试字符串类型参数在条件中的格式化"""
    print("=== 测试字符串条件格式化 ===\n")

    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(extractor)

    # 测试不同类型的条件格式化
    # 使用 repr() 来正确处理各种类型的值
    # repr() 会：
    #   - 将 None 转换为 None（字面量）
    #   - 将字符串转换为带引号的字符串（如 'demo'）
    #   - 将数字转换为数字字面量（如 1080）
    test_cases = [
        ("draft_name", "str", "{repr(args.input.draft_name)}"),  # 字符串使用 repr()
        ("track_name", "Optional[str]", "{repr(args.input.track_name)}"),  # 可选字符串使用 repr()
        ("width", "int", "{repr(args.input.width)}"),  # 数字使用 repr()
        ("volume", "float", "{repr(args.input.volume)}"),  # 浮点数使用 repr()
        ("change_pitch", "bool", "{repr(args.input.change_pitch)}"),  # 布尔值使用 repr()
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
        source_file="app/api/draft_routes.py",
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
    # 修正后的期望：条件检查使用 repr()，赋值时字符串需要引号
    checks = [
        (
            "字符串类型参数在条件中使用 repr()",
            "{repr(args.input.draft_name)} is not None:" in api_call_code,
        ),
        (
            "字符串类型参数在赋值中有引号",
            '= "{args.input.draft_name}"' in api_call_code,
        ),
        (
            "数字类型参数在条件中使用 repr()",
            "{repr(args.input.width)} is not None:" in api_call_code,
        ),
        (
            "数字类型参数在赋值中无引号",
            "= {args.input.width}" in api_call_code,
        ),
        (
            "布尔类型参数在条件中使用 repr()",
            "{repr(args.input.allow_replace)} is not None:" in api_call_code,
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
    print("说明：这个测试模拟 handler 在 Coze 中运行时生成 API 调用脚本的过程\n")

    # 测试用例 1: 所有参数有值
    print("测试用例 1: 所有参数有值")
    print("-" * 60)
    
    # 模拟 handler 运行时的环境
    class MockInput1:
        draft_name = "demo_coze"
        width = 1080
        height = 1920
        fps = 30
        allow_replace = True

    class MockArgs1:
        input = MockInput1()

    args = MockArgs1()
    generated_uuid = "test123"

    # Handler 中的 f-string 会生成这样的代码（修复后）
    # 关键：使用 repr() 来正确转换各种类型的值
    generated_script = f"""
# 构造 request 对象
req_params_{generated_uuid} = {{}}
if {repr(args.input.draft_name)} is not None:
    req_params_{generated_uuid}['draft_name'] = "{args.input.draft_name}"
if {repr(args.input.width)} is not None:
    req_params_{generated_uuid}['width'] = {args.input.width}
if {repr(args.input.height)} is not None:
    req_params_{generated_uuid}['height'] = {args.input.height}
if {repr(args.input.fps)} is not None:
    req_params_{generated_uuid}['fps'] = {args.input.fps}
if {repr(args.input.allow_replace)} is not None:
    req_params_{generated_uuid}['allow_replace'] = {args.input.allow_replace}
"""

    print("生成的脚本内容:")
    print(generated_script)

    # 验证生成的脚本语法正确
    try:
        exec(generated_script)
        req_params = locals()[f"req_params_{generated_uuid}"]
        print("✅ 脚本执行成功！")
        print(f"生成的参数字典: {req_params}")
        
        expected = {
            'draft_name': 'demo_coze',
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'allow_replace': True,
        }
        
        if req_params != expected:
            print("❌ 参数值不正确")
            print(f"期望: {expected}")
            print(f"实际: {req_params}")
            return False
        print("✅ 参数值正确！\n")
            
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试用例 2: 部分参数为 None（这是关键测试！）
    print("测试用例 2: 部分参数为 None（验证修复）")
    print("-" * 60)
    
    class MockInput2:
        draft_name = None  # None 值应该被跳过
        width = 1080
        height = None  # None 值应该被跳过
        fps = 30
        allow_replace = True

    class MockArgs2:
        input = MockInput2()

    args2 = MockArgs2()
    generated_uuid2 = "test456"
    
    # Handler 中的 f-string 会生成这样的代码
    # 关键：repr(None) 生成 None（不是 "None"）
    generated_script2 = f"""
# 构造 request 对象
req_params_{generated_uuid2} = {{}}
if {repr(args2.input.draft_name)} is not None:
    req_params_{generated_uuid2}['draft_name'] = "{args2.input.draft_name}"
if {repr(args2.input.width)} is not None:
    req_params_{generated_uuid2}['width'] = {args2.input.width}
if {repr(args2.input.height)} is not None:
    req_params_{generated_uuid2}['height'] = {args2.input.height}
if {repr(args2.input.fps)} is not None:
    req_params_{generated_uuid2}['fps'] = {args2.input.fps}
if {repr(args2.input.allow_replace)} is not None:
    req_params_{generated_uuid2}['allow_replace'] = {args2.input.allow_replace}
"""
    
    print("生成的脚本内容:")
    print(generated_script2)
    print("\n关键：注意 draft_name 和 height 的条件是 'if None is not None:'")
    print("这会正确评估为 False，跳过这些参数\n")
    
    try:
        exec(generated_script2)
        req_params2 = locals()[f"req_params_{generated_uuid2}"]
        print("✅ 脚本执行成功！")
        print(f"生成的参数字典: {req_params2}")
        
        # 验证 None 值被正确跳过
        expected2 = {
            # draft_name 不应该在这里（值为 None，条件为 False）
            'width': 1080,
            # height 不应该在这里（值为 None，条件为 False）
            'fps': 30,
            'allow_replace': True,
        }
        
        if req_params2 != expected2:
            print("❌ 参数值不正确（None 值未被正确跳过）")
            print(f"期望: {expected2}")
            print(f"实际: {req_params2}")
            return False
        print("✅ None 值被正确跳过！")
        print("✅ 修复验证成功：None 值不再被错误地添加到参数中\n")
        return True
            
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
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
