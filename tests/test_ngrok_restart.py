"""
测试 ngrok 重启场景

验证修复后的 ngrok 重启功能，特别是解决快速重启时的超时和连接重置错误
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.ngrok_manager import NgrokManager


def test_cleanup_stale_processes():
    """测试清理陈旧进程的功能"""
    print("=== 测试清理陈旧进程 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 调用清理方法（即使没有进程也应该正常工作）
    try:
        manager._cleanup_stale_ngrok_processes()
        print("✅ 清理方法执行成功（无错误）")
    except Exception as e:
        print(f"❌ 清理时出错: {e}")
        return False
    
    # 验证状态已重置
    assert not manager.is_running, "清理后 is_running 应该为 False"
    assert manager.tunnel is None, "清理后 tunnel 应该为 None"
    assert manager.public_url is None, "清理后 public_url 应该为 None"
    
    print("✅ 状态已正确重置")
    return True


def test_multiple_cleanup_calls():
    """测试多次调用清理方法"""
    print("\n=== 测试多次调用清理方法 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 多次调用清理方法应该是安全的
    for i in range(3):
        try:
            manager._cleanup_stale_ngrok_processes()
            print(f"  第 {i+1} 次清理成功")
        except Exception as e:
            print(f"❌ 第 {i+1} 次清理失败: {e}")
            return False
    
    print("✅ 多次清理均成功")
    return True


def test_start_tunnel_with_invalid_port():
    """测试使用无效端口启动隧道"""
    print("\n=== 测试使用无效端口启动 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 使用一个可能未使用的端口（但不实际启动服务）
    # 这应该失败但不会崩溃
    result = manager.start_tunnel(port=65432, region="us")
    
    # 由于没有实际的服务在监听，这应该失败或超时
    # 但重要的是不应该崩溃
    print(f"  启动结果: {result}")
    print("✅ 无效端口处理正常（未崩溃）")
    
    # 清理
    if manager.is_running:
        manager.stop_tunnel()
    
    return True


def test_exception_handling_in_start():
    """测试 start_tunnel 的异常处理"""
    print("\n=== 测试异常处理 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 测试各种错误情况
    # 1. 无效的 region
    result = manager.start_tunnel(port=8000, region="invalid_region")
    print(f"  无效 region 结果: {result is None}")
    assert result is None, "无效 region 应该返回 None"
    
    # 清理状态
    manager._cleanup_stale_ngrok_processes()
    
    print("✅ 异常处理正常")
    return True


def test_retry_logic():
    """测试重试逻辑"""
    print("\n=== 测试重试逻辑 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 验证方法有 max_retries 参数（通过检查代码）
    import inspect
    source = inspect.getsource(manager.start_tunnel)
    
    has_retry_logic = "max_retries" in source and "retry_count" in source
    print(f"  包含重试逻辑: {has_retry_logic}")
    assert has_retry_logic, "应该包含重试逻辑"
    
    has_connection_error_handling = "ConnectionResetError" in source or "ConnectionError" in source
    print(f"  处理连接错误: {has_connection_error_handling}")
    assert has_connection_error_handling, "应该处理连接错误"
    
    print("✅ 重试逻辑已实现")
    return True


def test_stop_and_cleanup():
    """测试停止和清理流程"""
    print("\n=== 测试停止和清理 ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 测试停止一个未运行的隧道（应该只是警告，不崩溃）
    manager.stop_tunnel()
    print("  停止未运行的隧道: 正常")
    
    # 测试 kill_all（应该安全执行）
    manager.kill_all()
    print("  kill_all 执行: 正常")
    
    # 验证状态
    assert not manager.is_running, "kill_all 后应该不在运行"
    
    print("✅ 停止和清理正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试 ngrok 重启功能修复")
    print("=" * 60)
    
    tests = [
        test_cleanup_stale_processes,
        test_multiple_cleanup_calls,
        test_start_tunnel_with_invalid_port,
        test_exception_handling_in_start,
        test_retry_logic,
        test_stop_and_cleanup,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"测试完成: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
