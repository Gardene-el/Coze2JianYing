"""
测试 APIResponseManager 与实际 API 响应格式的集成

这个测试验证响应管理器生成的响应格式是否符合 Coze 要求
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.api_response_manager import get_response_manager, ErrorCode


def test_response_format_for_coze():
    """测试响应格式是否符合 Coze 要求"""
    print("\n" + "=" * 60)
    print("测试响应格式（Coze 兼容性）")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 模拟成功的草稿创建响应
    response = manager.success(
        message="草稿创建成功",
        data={"draft_id": "test-draft-123"}
    )
    
    # 构造完整的 API 响应（模拟 create_draft 端点）
    api_response = {
        "draft_id": "test-draft-123",
        **response
    }
    
    print("\n成功响应示例:")
    for key, value in api_response.items():
        print(f"  {key}: {value}")
    
    # Coze 要求验证
    assert api_response["success"] is True, "必须返回 success=True"
    assert "message" in api_response, "必须有 message 字段"
    assert "error_code" in api_response, "必须有 error_code 字段"
    assert "draft_id" in api_response, "必须有 draft_id 字段"
    
    print("\n✅ 成功响应格式符合 Coze 要求")
    
    # 模拟错误响应
    error_response = manager.error(
        error_code=ErrorCode.DRAFT_CREATE_FAILED,
        details={"reason": "磁盘空间不足"}
    )
    
    # 构造完整的 API 错误响应
    api_error_response = {
        "draft_id": "",  # 失败时返回空字符串
        **error_response
    }
    
    print("\n错误响应示例:")
    for key, value in api_error_response.items():
        print(f"  {key}: {value}")
    
    # 关键：即使是错误，success 也是 True
    assert api_error_response["success"] is True, "即使错误，也必须返回 success=True"
    assert "message" in api_error_response, "必须有 message 字段"
    assert "error_code" in api_error_response, "必须有 error_code 字段"
    assert api_error_response["error_code"] != "SUCCESS", "错误响应的 error_code 不应该是 SUCCESS"
    assert "details" in api_error_response, "错误响应应该有 details 字段"
    
    print("\n✅ 错误响应格式符合 Coze 要求（success=True）")
    
    return True


def test_all_error_codes_return_success_true():
    """测试所有错误代码都返回 success=True"""
    print("\n" + "=" * 60)
    print("测试所有错误代码（验证 success=True）")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 测试各种错误代码
    test_cases = [
        (ErrorCode.DRAFT_NOT_FOUND, {"draft_id": "test"}),
        (ErrorCode.SEGMENT_NOT_FOUND, {"segment_id": "test"}),
        (ErrorCode.TRACK_TYPE_MISMATCH, {"segment_type": "audio", "track_type": "video"}),
        (ErrorCode.INVALID_PARAMETER, {"parameter": "fps", "reason": "无效"}),
        (ErrorCode.INTERNAL_ERROR, {"error": "测试错误"}),
    ]
    
    print("\n测试错误代码:")
    all_success = True
    for error_code, details in test_cases:
        response = manager.error(error_code=error_code, details=details)
        success_value = response["success"]
        status = "✓" if success_value is True else "✗"
        print(f"  {status} {error_code}: success={success_value}")
        
        if success_value is not True:
            all_success = False
            print(f"    ❌ 错误：{error_code} 返回 success={success_value}")
    
    assert all_success, "所有错误响应都必须返回 success=True"
    
    print("\n✅ 所有错误代码都正确返回 success=True")
    
    return True


def test_response_contains_required_fields():
    """测试响应包含所有必需字段"""
    print("\n" + "=" * 60)
    print("测试响应字段完整性")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 成功响应
    success_response = manager.success(message="测试")
    
    required_fields = ["success", "message", "error_code", "category", "level", "timestamp"]
    
    print("\n成功响应字段:")
    for field in required_fields:
        has_field = field in success_response
        status = "✓" if has_field else "✗"
        print(f"  {status} {field}: {success_response.get(field, 'MISSING')}")
        assert has_field, f"缺少字段: {field}"
    
    # 错误响应
    error_response = manager.error(
        error_code=ErrorCode.DRAFT_NOT_FOUND,
        details={"draft_id": "test"}
    )
    
    print("\n错误响应字段:")
    required_fields_with_details = required_fields + ["details"]
    for field in required_fields_with_details:
        has_field = field in error_response
        status = "✓" if has_field else "✗"
        value = error_response.get(field, 'MISSING')
        print(f"  {status} {field}: {value}")
        if field == "details":
            # details 是可选的，但在这个例子中应该存在
            assert has_field, "错误响应应该有 details 字段"
        else:
            assert has_field, f"缺少字段: {field}"
    
    print("\n✅ 响应包含所有必需字段")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("测试 APIResponseManager 与 API 响应格式集成")
    print("=" * 80)
    
    try:
        test_response_format_for_coze()
        test_all_error_codes_return_success_true()
        test_response_contains_required_fields()
        
        print("\n" + "=" * 80)
        print("✅ 所有集成测试通过！")
        print("=" * 80)
        print("\n关键验证:")
        print("  ✓ 响应格式符合 Coze 要求")
        print("  ✓ 所有错误都返回 success=True")
        print("  ✓ 包含所有必需字段（error_code, category, level 等）")
        print("  ✓ 错误详情通过 details 和 message 传递")
        print("\nAPIResponseManager 已准备好用于所有 API 端点！")
        
        return True
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
