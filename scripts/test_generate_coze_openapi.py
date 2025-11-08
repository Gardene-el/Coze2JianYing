#!/usr/bin/env python3
"""
测试 generate_coze_openapi.py 脚本的功能
验证生成的 OpenAPI 文件是否符合预期格式
"""

import os
import sys
import json
import yaml
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入生成脚本
from scripts.generate_coze_openapi import create_coze_openapi_spec


def test_yaml_generation():
    """测试生成 YAML 格式"""
    print("=" * 60)
    print("测试 1: 生成 YAML 格式")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_file = f.name
    
    try:
        # 生成 OpenAPI schema
        schema = create_coze_openapi_spec("http://localhost:8000")
        
        # 保存为 YAML
        with open(temp_file, 'w', encoding='utf-8') as f:
            yaml.dump(schema, f, allow_unicode=True, sort_keys=False)
        
        # 验证文件可以读取
        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded_schema = yaml.safe_load(f)
        
        # 验证关键字段
        assert loaded_schema['openapi'] == '3.0.1', "OpenAPI 版本应该是 3.0.1"
        assert 'info' in loaded_schema, "应该包含 info 字段"
        assert 'paths' in loaded_schema, "应该包含 paths 字段"
        assert 'components' in loaded_schema, "应该包含 components 字段"
        assert 'examples' in loaded_schema['components'], "components 应该包含 examples"
        
        print("✅ YAML 生成测试通过")
        print(f"   - OpenAPI 版本: {loaded_schema['openapi']}")
        print(f"   - 端点数量: {len(loaded_schema['paths'])}")
        print(f"   - 示例数量: {len(loaded_schema['components']['examples'])}")
        return True
        
    except Exception as e:
        print(f"❌ YAML 生成测试失败: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_json_generation():
    """测试生成 JSON 格式"""
    print("\n" + "=" * 60)
    print("测试 2: 生成 JSON 格式")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # 生成 OpenAPI schema
        schema = create_coze_openapi_spec("http://localhost:8000")
        
        # 保存为 JSON
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        # 验证文件可以读取
        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded_schema = json.load(f)
        
        # 验证关键字段
        assert loaded_schema['openapi'] == '3.0.1', "OpenAPI 版本应该是 3.0.1"
        assert 'info' in loaded_schema, "应该包含 info 字段"
        assert 'paths' in loaded_schema, "应该包含 paths 字段"
        
        print("✅ JSON 生成测试通过")
        print(f"   - OpenAPI 版本: {loaded_schema['openapi']}")
        print(f"   - 端点数量: {len(loaded_schema['paths'])}")
        return True
        
    except Exception as e:
        print(f"❌ JSON 生成测试失败: {e}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_schema_structure():
    """测试 Schema 结构"""
    print("\n" + "=" * 60)
    print("测试 3: 验证 Schema 结构")
    print("=" * 60)
    
    try:
        schema = create_coze_openapi_spec("https://example.com")
        
        # 验证必需的端点存在
        required_paths = [
            '/api/draft/create',
            '/api/segment/audio/create',
        ]
        
        for path in required_paths:
            assert path in schema['paths'], f"缺少端点: {path}"
            print(f"   ✓ 端点存在: {path}")
        
        # 验证每个路径有对应的示例
        for path, methods in schema['paths'].items():
            for method, operation in methods.items():
                op_id = operation.get('operationId')
                if op_id:
                    assert op_id in schema['components']['examples'], \
                        f"缺少示例: {op_id}"
                    
                    example = schema['components']['examples'][op_id]
                    assert 'value' in example, f"{op_id} 示例应该有 value"
                    assert 'ReqExample' in example['value'], \
                        f"{op_id} 应该有 ReqExample"
                    assert 'RespExample' in example['value'], \
                        f"{op_id} 应该有 RespExample"
                    
                    print(f"   ✓ 示例完整: {op_id}")
        
        print("✅ Schema 结构测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Schema 结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_url_customization():
    """测试服务器 URL 自定义"""
    print("\n" + "=" * 60)
    print("测试 4: 服务器 URL 自定义")
    print("=" * 60)
    
    try:
        test_url = "https://my-custom-url.ngrok-free.app"
        schema = create_coze_openapi_spec(test_url)
        
        assert 'servers' in schema, "应该包含 servers 字段"
        assert len(schema['servers']) > 0, "servers 应该至少有一个服务器"
        assert schema['servers'][0]['url'] == test_url, \
            f"服务器 URL 应该是 {test_url}"
        
        print(f"✅ 服务器 URL 自定义测试通过")
        print(f"   - 配置的 URL: {schema['servers'][0]['url']}")
        return True
        
    except Exception as e:
        print(f"❌ 服务器 URL 自定义测试失败: {e}")
        return False


def test_openapi_3_0_compatibility():
    """测试 OpenAPI 3.0.1 兼容性（exclusiveMinimum/Maximum 转换）"""
    print("\n" + "=" * 60)
    print("测试 5: OpenAPI 3.0.1 兼容性")
    print("=" * 60)
    
    try:
        schema = create_coze_openapi_spec("https://example.com")
        
        # 检查 schemas 中是否有 exclusiveMinimum 字段，并验证其为布尔值
        schemas = schema.get('components', {}).get('schemas', {})
        
        def check_exclusive_fields(obj, path=""):
            """递归检查 exclusiveMinimum 和 exclusiveMaximum 字段"""
            issues = []
            if isinstance(obj, dict):
                # 检查 exclusiveMinimum
                if 'exclusiveMinimum' in obj:
                    value = obj['exclusiveMinimum']
                    if not isinstance(value, bool):
                        issues.append(f"在 {path}: exclusiveMinimum 应该是布尔值，实际是 {type(value).__name__}")
                    else:
                        # 如果是布尔值，应该有对应的 minimum 字段
                        if value and 'minimum' not in obj:
                            issues.append(f"在 {path}: exclusiveMinimum 为 true 但缺少 minimum 字段")
                
                # 检查 exclusiveMaximum
                if 'exclusiveMaximum' in obj:
                    value = obj['exclusiveMaximum']
                    if not isinstance(value, bool):
                        issues.append(f"在 {path}: exclusiveMaximum 应该是布尔值，实际是 {type(value).__name__}")
                    else:
                        # 如果是布尔值，应该有对应的 maximum 字段
                        if value and 'maximum' not in obj:
                            issues.append(f"在 {path}: exclusiveMaximum 为 true 但缺少 maximum 字段")
                
                # 递归检查子对象
                for key, value in obj.items():
                    check_exclusive_fields(value, f"{path}.{key}" if path else key)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_exclusive_fields(item, f"{path}[{i}]")
            
            return issues
        
        issues = check_exclusive_fields(schemas, "schemas")
        
        if issues:
            print("❌ 发现 OpenAPI 3.0.1 兼容性问题:")
            for issue in issues[:5]:  # 只显示前5个问题
                print(f"   - {issue}")
            return False
        
        print("✅ OpenAPI 3.0.1 兼容性测试通过")
        print("   - 所有 exclusiveMinimum/exclusiveMaximum 字段均为布尔值")
        print("   - 数值限制正确使用 minimum/maximum 字段")
        return True
        
    except Exception as e:
        print(f"❌ OpenAPI 3.0.1 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试 generate_coze_openapi.py")
    print("=" * 60)
    
    tests = [
        test_yaml_generation,
        test_json_generation,
        test_schema_structure,
        test_server_url_customization,
        test_openapi_3_0_compatibility,  # 新增的测试
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
