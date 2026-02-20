#!/usr/bin/env python3
"""
测试大括号转义是否正确
"""

import re
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.handler_generator.api_endpoint_info import APIEndpointInfo
from scripts.handler_generator.generate_api_call_code import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor


def check_brace_escaping():
    """检查生成的代码中的大括号转义"""
    print("=== 检查大括号转义 ===\n")

    # 初始化
    schema_file = project_root / "app" / "schemas" / "general_schemas.py"
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
    code = generator.generate_api_call_code(endpoint, output_fields)

    print("生成的代码片段:")
    print("-" * 60)
    # 只显示前30行
    lines = code.split("\n")
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:2d}: {line}")
    print("-" * 60)
    print()

    # 查找所有大括号
    single_braces = []
    double_braces = []

    # 查找双大括号 {{...}}
    double_pattern = r"\{\{[^}]+\}\}"
    double_matches = re.findall(double_pattern, code)

    # 查找单大括号 {...} (排除双大括号的情况)
    # 这个正则更简单：找所有 { 和 }，检查是否成对
    for i, char in enumerate(code):
        if char == "{":
            # 检查下一个字符是否也是 {
            if i + 1 < len(code) and code[i + 1] == "{":
                continue  # 这是双大括号的开始
            # 检查上一个字符是否也是 {
            if i > 0 and code[i - 1] == "{":
                continue  # 这是双大括号的第二个 {
            # 这是单个 {
            context_start = max(0, i - 20)
            context_end = min(len(code), i + 30)
            context = code[context_start:context_end]
            single_braces.append((i, context))

    print(f"统计:")
    print(f"  双大括号 {{{{}}: {len(double_matches)} 个")
    print(f"  单大括号 {{: {len(single_braces)} 个")
    print()

    if single_braces:
        print("⚠️ 发现未转义的单大括号:")
        for pos, context in single_braces[:5]:  # 只显示前5个
            print(f"  位置 {pos}: ...{context}...")
        print()
        return False
    else:
        print("✅ 所有大括号都已正确转义为双大括号")
        print()
        return True


def test_runtime_behavior():
    """测试运行时行为：模拟 handler 中的 f-string 求值"""
    print("=== 测试运行时 f-string 求值 ===\n")

    # 模拟生成的代码
    test_code = '''api_call = f"""
# API 调用: test
# 时间: {{time.strftime('%Y-%m-%d %H:%M:%S')}}

# 构造 request 对象
req_params_{{generated_uuid}} = {{}}
req_params_{{generated_uuid}}['field'] = "{{args.input.field}}"
"""'''

    print("测试代码:")
    print(test_code)
    print()

    # 模拟运行时变量
    class MockArgs:
        class Input:
            field = "test_value"

        input = Input()

    import time

    generated_uuid = "abc123"
    args = MockArgs()

    # 尝试执行 f-string
    try:
        exec(test_code)
        result = locals()["api_call"]
        print("✅ f-string 求值成功！")
        print()
        print("生成的内容:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        print()

        # 验证结果包含预期内容
        checks = [
            ("包含 UUID", "abc123" in result),
            ("包含字段值", "test_value" in result),
            ("包含空字典字面量", "{}" in result),
            ("不包含双大括号", "{{" not in result),
        ]

        print("结果验证:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ f-string 求值失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("大括号转义测试")
    print("=" * 60)
    print()

    results = []
    results.append(("大括号转义检查", check_brace_escaping()))
    results.append(("运行时 f-string 求值", test_runtime_behavior()))

    # 汇总
    print()
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
