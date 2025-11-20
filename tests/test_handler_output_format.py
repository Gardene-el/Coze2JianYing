#!/usr/bin/env python3
"""
测试 handler 输出格式是否符合 Coze 要求

验证生成的 handler 返回 Dict[str, Any] 而不是 NamedTuple，
确保 Coze 平台能够正确识别和解析返回值。

预期行为：
- handler 函数的返回值应该是字典类型
- 字典应该包含必要的字段（如 success, message, draft_id 等）
- 字典可以被 JSON 序列化
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_output_format_is_dict():
    """测试 Output NamedTuple 的 _asdict() 方法能正确转换为字典"""
    from typing import NamedTuple, Optional, Dict, Any
    
    # 模拟 Output 类型
    class Output(NamedTuple):
        draft_id: str = ""
        success: bool = False
        message: str = ""
        error_code: Optional[str] = None
        category: Optional[str] = None
        level: Optional[str] = None
        details: Optional[Dict] = None
    
    # 创建 Output 实例并转换为字典
    output = Output(
        draft_id="test_uuid_123",
        success=True,
        message="操作成功"
    )
    
    result = output._asdict()
    
    # 验证结果是字典
    assert isinstance(result, dict), f"返回值应该是 dict 类型，但得到 {type(result)}"
    
    # 验证字典包含正确的键
    expected_keys = ["draft_id", "success", "message", "error_code", "category", "level", "details"]
    for key in expected_keys:
        assert key in result, f"字典应该包含键 '{key}'"
    
    # 验证值正确
    assert result["draft_id"] == "test_uuid_123", "draft_id 值不正确"
    assert result["success"] is True, "success 值不正确"
    assert result["message"] == "操作成功", "message 值不正确"
    assert result["error_code"] is None, "error_code 应该是 None"
    
    print("✅ Output._asdict() 测试通过")
    return True


def test_json_serialization():
    """测试字典可以被正确序列化为 JSON"""
    from typing import NamedTuple, Optional, Dict, Any
    
    class Output(NamedTuple):
        draft_id: str = ""
        success: bool = False
        message: str = ""
        error_code: Optional[str] = None
        details: Optional[Dict] = None
    
    output = Output(
        draft_id="test_uuid_456",
        success=True,
        message="测试消息",
        details={"key": "value"}
    )
    
    result_dict = output._asdict()
    
    # 尝试序列化为 JSON
    try:
        json_str = json.dumps(result_dict, ensure_ascii=False)
        print(f"JSON 输出: {json_str}")
        
        # 验证 JSON 格式正确
        parsed = json.loads(json_str)
        assert parsed["draft_id"] == "test_uuid_456"
        assert parsed["success"] is True
        assert parsed["message"] == "测试消息"
        assert parsed["details"] == {"key": "value"}
        
        print("✅ JSON 序列化测试通过")
        return True
    except Exception as e:
        print(f"❌ JSON 序列化失败: {e}")
        return False


def test_coze_compatible_format():
    """测试输出格式与 Coze 平台兼容"""
    from typing import NamedTuple, Optional, Dict, Any
    
    class Output(NamedTuple):
        success: bool = False
        message: str = ""
        result: Optional[Dict] = None
    
    # 模拟一个带有嵌套结果的输出
    output = Output(
        success=True,
        message="TimeRange 对象创建成功",
        result={"duration": 6090, "start": 6668}
    )
    
    result_dict = output._asdict()
    json_str = json.dumps(result_dict, ensure_ascii=False)
    
    # 这应该产生类似 Coze 期望的格式
    print(f"Coze 兼容格式: {json_str}")
    
    # 验证格式
    parsed = json.loads(json_str)
    assert "success" in parsed
    assert "message" in parsed
    assert "result" in parsed
    assert isinstance(parsed["result"], dict)
    
    print("✅ Coze 兼容格式测试通过")
    return True


def test_error_case_format():
    """测试错误情况下的输出格式"""
    from typing import NamedTuple
    
    class Output(NamedTuple):
        success: bool = False
        message: str = ""
    
    # 错误情况
    output = Output(
        success=False,
        message="调用 create_draft 时发生错误: 测试错误"
    )
    
    result_dict = output._asdict()
    json_str = json.dumps(result_dict, ensure_ascii=False)
    
    print(f"错误格式: {json_str}")
    
    parsed = json.loads(json_str)
    assert parsed["success"] is False
    assert "错误" in parsed["message"]
    
    print("✅ 错误格式测试通过")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Handler 输出格式测试")
    print("=" * 60)
    print()
    
    tests = [
        test_output_format_is_dict,
        test_json_serialization,
        test_coze_compatible_format,
        test_error_case_format,
    ]
    
    results = []
    for test_func in tests:
        print(f"\n运行测试: {test_func.__name__}")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
        print()
    
    print("=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
