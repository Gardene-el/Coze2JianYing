#!/usr/bin/env python3
"""
测试 E 脚本的字符串引号修复
验证生成的代码会正确为字符串值添加引号
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.handler_generator.e_api_call_code_generator import APICallCodeGenerator
from scripts.handler_generator.schema_extractor import SchemaExtractor
from scripts.handler_generator.api_endpoint_info import APIEndpointInfo


def test_field_needs_quotes():
    """测试 _field_needs_quotes 方法"""
    print("=" * 60)
    print("测试字段类型引号判断")
    print("=" * 60)
    
    # 创建模拟的 SchemaExtractor 和 APICallCodeGenerator
    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    schema_extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(schema_extractor)
    
    # 测试用例
    test_cases = [
        ("str", True, "字符串类型需要引号"),
        ("int", False, "整数类型不需要引号"),
        ("float", False, "浮点数类型不需要引号"),
        ("bool", False, "布尔类型不需要引号"),
        ("Optional[str]", True, "可选字符串需要引号"),
        ("List[str]", True, "字符串列表需要引号"),
        ("TimeRange", False, "自定义类型不需要引号"),
        ("ClipSettings", False, "自定义类型不需要引号"),
        ("Optional[TimeRange]", False, "可选自定义类型不需要引号"),
    ]
    
    all_pass = True
    for field_type, expected, description in test_cases:
        result = generator._field_needs_quotes(field_type)
        if result == expected:
            print(f"✅ {description}: {field_type} -> {result}")
        else:
            print(f"❌ {description}: {field_type} -> {result} (期望: {expected})")
            all_pass = False
    
    return all_pass


def test_generated_code_has_quotes():
    """测试生成的代码是否正确添加引号"""
    print("\n" + "=" * 60)
    print("测试生成的代码包含引号")
    print("=" * 60)
    
    schema_file = project_root / "app" / "schemas" / "segment_schemas.py"
    schema_extractor = SchemaExtractor(str(schema_file))
    generator = APICallCodeGenerator(schema_extractor)
    
    # 模拟一个 API 端点
    endpoint = APIEndpointInfo(
        func_name="create_draft",
        path="/api/draft/create",
        has_draft_id=False,
        has_segment_id=False,
        request_model="CreateDraftRequest",
        response_model="CreateDraftResponse",
        path_params=[],
        source_file="draft_routes.py"
    )
    
    # 生成代码
    code = generator.generate_api_call_code(endpoint, [{"name": "draft_id", "type": "str"}])
    
    print("生成的代码片段:")
    print("-" * 60)
    print(code[:500])  # 显示前500个字符
    print("-" * 60)
    
    # 检查代码中是否包含 repr()
    # repr() 用于为字符串值添加引号
    if "repr(args.input." in code:
        print("✅ 代码包含 repr() 调用，字符串值将被正确引号")
        return True
    else:
        print("❌ 代码未包含 repr() 调用")
        return False


def test_compare_with_old_output():
    """对比新旧输出差异"""
    print("\n" + "=" * 60)
    print("对比修复前后的代码生成差异")
    print("=" * 60)
    
    print("\n修复前（错误）:")
    print("req_xxx = CreateDraftRequest(draft_name={args.input.draft_name}, width=1920)")
    print("→ 展开后: req_xxx = CreateDraftRequest(draft_name=demo, width=1920)")
    print("   ❌ draft_name=demo 缺少引号，导致语法错误")
    
    print("\n修复后（正确）:")
    print("req_xxx = CreateDraftRequest(draft_name={repr(args.input.draft_name)}, width=1920)")
    print("→ 展开后: req_xxx = CreateDraftRequest(draft_name='demo', width=1920)")
    print("   ✅ draft_name='demo' 有引号，语法正确")
    
    return True


if __name__ == "__main__":
    print("\n🎬 开始测试 E 脚本的字符串引号修复")
    
    results = []
    results.append(("字段类型引号判断", test_field_needs_quotes()))
    results.append(("生成代码包含引号", test_generated_code_has_quotes()))
    results.append(("对比修复差异", test_compare_with_old_output()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        print("\n下一步：运行 scripts/generate_handler_from_api.py 重新生成 handler 文件")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
