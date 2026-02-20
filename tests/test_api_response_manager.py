"""
测试 API 响应管理器

验证 APIResponseManager 的各项功能，确保：
1. 所有响应都返回 success=True
2. 错误信息正确格式化
3. 错误代码和类别正确分类
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.api_response_manager import (
    APIResponseManager,
    ErrorCode,
    ErrorCategory,
    ResponseLevel,
    get_response_manager
)


def test_success_response():
    """测试成功响应"""
    print("\n" + "=" * 60)
    print("测试成功响应")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 基本成功响应
    response = manager.success(message="测试成功")
    print(f"\n基本成功响应:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    print(f"  error_code: {response['error_code']}")
    print(f"  category: {response['category']}")
    
    assert response["success"] is True
    assert response["error_code"] == ErrorCode.SUCCESS
    assert response["category"] == ErrorCategory.SUCCESS
    assert response["message"] == "测试成功"
    assert "timestamp" in response
    
    # 带数据的成功响应
    data = {"draft_id": "test-123", "name": "测试草稿"}
    response = manager.success(message="草稿创建成功", data=data)
    print(f"\n带数据的成功响应:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    print(f"  data: {response['data']}")
    
    assert response["success"] is True
    assert response["data"] == data
    assert response["message"] == "草稿创建成功"
    
    print("\n✅ 成功响应测试通过")


def test_error_response_always_success():
    """测试错误响应也返回 success=True"""
    print("\n" + "=" * 60)
    print("测试错误响应（关键：依然返回 success=True）")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 草稿不存在错误
    response = manager.error(
        error_code=ErrorCode.DRAFT_NOT_FOUND,
        details={"draft_id": "non-existent-123"}
    )
    
    print(f"\n草稿不存在错误响应:")
    print(f"  success: {response['success']}")  # 关键：应该是 True
    print(f"  error_code: {response['error_code']}")
    print(f"  category: {response['category']}")
    print(f"  message: {response['message']}")
    print(f"  details: {response.get('details')}")
    
    # 关键断言：即使是错误，success 也应该是 True
    assert response["success"] is True, "错误响应必须返回 success=True 以通过 Coze 测试"
    assert response["error_code"] == ErrorCode.DRAFT_NOT_FOUND
    assert response["category"] == ErrorCategory.NOT_FOUND
    assert "non-existent-123" in response["message"]
    
    print("\n✅ 错误响应测试通过（success=True 确认）")


def test_draft_errors():
    """测试草稿相关错误"""
    print("\n" + "=" * 60)
    print("测试草稿相关错误")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 草稿不存在
    response = manager.error(
        error_code=ErrorCode.DRAFT_NOT_FOUND,
        details={"draft_id": "abc-123"}
    )
    print(f"\n草稿不存在:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "abc-123" in response["message"]
    
    # 草稿已存在
    response = manager.error(
        error_code=ErrorCode.DRAFT_ALREADY_EXISTS,
        details={"draft_name": "我的草稿"}
    )
    print(f"\n草稿已存在:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "我的草稿" in response["message"]
    
    # 草稿创建失败
    response = manager.error(
        error_code=ErrorCode.DRAFT_CREATE_FAILED,
        details={"reason": "磁盘空间不足"}
    )
    print(f"\n草稿创建失败:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "磁盘空间不足" in response["message"]
    
    print("\n✅ 草稿错误测试通过")


def test_segment_errors():
    """测试片段相关错误"""
    print("\n" + "=" * 60)
    print("测试片段相关错误")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 片段不存在
    response = manager.error(
        error_code=ErrorCode.SEGMENT_NOT_FOUND,
        details={"segment_id": "seg-123"}
    )
    print(f"\n片段不存在:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "seg-123" in response["message"]
    
    # 片段类型不匹配
    response = manager.error(
        error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
        details={"expected": "audio", "actual": "video"}
    )
    print(f"\n片段类型不匹配:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "audio" in response["message"]
    assert "video" in response["message"]
    
    print("\n✅ 片段错误测试通过")


def test_track_errors():
    """测试轨道相关错误"""
    print("\n" + "=" * 60)
    print("测试轨道相关错误")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 轨道索引无效
    response = manager.error(
        error_code=ErrorCode.TRACK_INDEX_INVALID,
        details={"track_index": 99}
    )
    print(f"\n轨道索引无效:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "99" in response["message"]
    
    # 轨道类型不匹配
    response = manager.error(
        error_code=ErrorCode.TRACK_TYPE_MISMATCH,
        details={"segment_type": "audio", "track_type": "video"}
    )
    print(f"\n轨道类型不匹配:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "audio" in response["message"]
    assert "video" in response["message"]
    
    print("\n✅ 轨道错误测试通过")


def test_validation_errors():
    """测试参数验证错误"""
    print("\n" + "=" * 60)
    print("测试参数验证错误")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 参数无效
    response = manager.format_validation_error(
        field="volume",
        value=3.0,
        reason="音量必须在 0-2 之间"
    )
    print(f"\n参数无效:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    print(f"  details: {response.get('details')}")
    assert response["success"] is True
    assert "volume" in response["message"]
    
    # 缺少必需参数
    response = manager.error(
        error_code=ErrorCode.MISSING_REQUIRED_PARAMETER,
        details={"parameter": "draft_name"}
    )
    print(f"\n缺少必需参数:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "draft_name" in response["message"]
    
    # 参数超出范围
    response = manager.error(
        error_code=ErrorCode.PARAMETER_OUT_OF_RANGE,
        details={"parameter": "fps", "min": 1, "max": 120, "value": 200}
    )
    print(f"\n参数超出范围:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert "fps" in response["message"]
    assert "200" in response["message"]
    
    print("\n✅ 参数验证错误测试通过")


def test_helper_methods():
    """测试辅助方法"""
    print("\n" + "=" * 60)
    print("测试辅助方法")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 包装数据
    data = {"id": "123", "name": "测试"}
    response = manager.wrap_data(data, message="数据获取成功")
    print(f"\n包装数据:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    print(f"  data: {response['data']}")
    assert response["success"] is True
    assert response["data"] == data
    
    # 资源不存在错误
    response = manager.format_not_found_error("draft", "draft-123")
    print(f"\n资源不存在:")
    print(f"  success: {response['success']}")
    print(f"  error_code: {response['error_code']}")
    print(f"  message: {response['message']}")
    assert response["success"] is True
    assert response["error_code"] == ErrorCode.DRAFT_NOT_FOUND
    
    # 操作失败错误
    response = manager.format_operation_error("保存草稿", "权限不足")
    print(f"\n操作失败:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    print(f"  details: {response.get('details')}")
    assert response["success"] is True
    # The message template uses "reason" field, operation is in details
    assert "权限不足" in response["message"]
    assert response["details"]["operation"] == "保存草稿"
    
    # 内部错误
    try:
        raise ValueError("测试异常")
    except Exception as e:
        response = manager.format_internal_error(e)
        print(f"\n内部错误:")
        print(f"  success: {response['success']}")
        print(f"  error_code: {response['error_code']}")
        print(f"  message: {response['message']}")
        print(f"  details: {response.get('details')}")
        assert response["success"] is True
        assert response["error_code"] == ErrorCode.INTERNAL_ERROR
        # Check if error details contain the exception info
        assert response.get('details') is not None
        assert "测试异常" in str(response.get('details'))
    
    print("\n✅ 辅助方法测试通过")


def test_custom_message():
    """测试自定义消息"""
    print("\n" + "=" * 60)
    print("测试自定义消息")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 使用自定义消息覆盖默认模板
    custom_message = "这是一条自定义的错误消息，包含特殊信息"
    response = manager.error(
        error_code=ErrorCode.DRAFT_NOT_FOUND,
        message=custom_message
    )
    
    print(f"\n自定义消息:")
    print(f"  success: {response['success']}")
    print(f"  message: {response['message']}")
    
    assert response["success"] is True
    assert response["message"] == custom_message
    
    print("\n✅ 自定义消息测试通过")


def test_error_categories():
    """测试错误分类正确性"""
    print("\n" + "=" * 60)
    print("测试错误分类")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 验证错误
    response = manager.error(ErrorCode.INVALID_PARAMETER, details={"parameter": "test", "reason": "test"})
    print(f"\n验证错误类别: {response['category']}")
    assert response["category"] == ErrorCategory.VALIDATION_ERROR
    
    # 不存在错误
    response = manager.error(ErrorCode.DRAFT_NOT_FOUND, details={"draft_id": "test"})
    print(f"不存在错误类别: {response['category']}")
    assert response["category"] == ErrorCategory.NOT_FOUND
    
    # 已存在错误
    response = manager.error(ErrorCode.DRAFT_ALREADY_EXISTS, details={"draft_name": "test"})
    print(f"已存在错误类别: {response['category']}")
    assert response["category"] == ErrorCategory.ALREADY_EXISTS
    
    # 类型不匹配错误
    response = manager.error(ErrorCode.SEGMENT_TYPE_MISMATCH, details={"expected": "a", "actual": "b"})
    print(f"类型不匹配类别: {response['category']}")
    assert response["category"] == ErrorCategory.TYPE_MISMATCH
    
    # 操作失败错误
    response = manager.error(ErrorCode.OPERATION_FAILED, details={"reason": "test"})
    print(f"操作失败类别: {response['category']}")
    assert response["category"] == ErrorCategory.OPERATION_FAILED
    
    # 内部错误
    response = manager.error(ErrorCode.INTERNAL_ERROR, details={"error": "test"})
    print(f"内部错误类别: {response['category']}")
    assert response["category"] == ErrorCategory.INTERNAL_ERROR
    
    print("\n✅ 错误分类测试通过")


def test_response_levels():
    """测试响应级别"""
    print("\n" + "=" * 60)
    print("测试响应级别")
    print("=" * 60)
    
    manager = get_response_manager()
    
    # 信息级别
    response = manager.success()
    print(f"\n信息级别: {response['level']}")
    assert response["level"] == ResponseLevel.INFO
    
    # 错误级别
    response = manager.error(ErrorCode.DRAFT_NOT_FOUND, details={"draft_id": "test"})
    print(f"错误级别: {response['level']}")
    assert response["level"] == ResponseLevel.ERROR
    
    # 严重错误级别
    response = manager.error(ErrorCode.INTERNAL_ERROR, details={"error": "test"})
    print(f"严重错误级别: {response['level']}")
    assert response["level"] == ResponseLevel.CRITICAL
    
    print("\n✅ 响应级别测试通过")


def test_singleton():
    """测试单例模式"""
    print("\n" + "=" * 60)
    print("测试单例模式")
    print("=" * 60)
    
    manager1 = get_response_manager()
    manager2 = get_response_manager()
    
    print(f"\nmanager1 id: {id(manager1)}")
    print(f"manager2 id: {id(manager2)}")
    
    assert manager1 is manager2, "应该返回同一个实例"
    
    print("\n✅ 单例模式测试通过")


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始测试 API 响应管理器")
    print("=" * 80)
    
    try:
        test_success_response()
        test_error_response_always_success()
        test_draft_errors()
        test_segment_errors()
        test_track_errors()
        test_validation_errors()
        test_helper_methods()
        test_custom_message()
        test_error_categories()
        test_response_levels()
        test_singleton()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        print("\n关键特性验证:")
        print("  ✓ 所有响应（包括错误）都返回 success=True")
        print("  ✓ 错误信息包含详细的代码、类别和消息")
        print("  ✓ 错误消息模板正确工作")
        print("  ✓ 辅助方法提供便捷的响应创建")
        print("  ✓ 错误分类和级别正确设置")
        print("  ✓ 单例模式正常工作")
        print("\n这个响应管理器已准备好用于 Coze 插件测试！")
        
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
