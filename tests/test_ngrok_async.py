"""
测试 ngrok 异步停止功能

这个测试验证异步停止机制不会阻塞调用线程
"""

import sys
import os
import time
import threading

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.backend.utils.ngrok_manager import NgrokManager


def test_async_stop_non_blocking():
    """测试异步停止不会阻塞调用线程"""
    print("=== 测试异步停止不会阻塞调用线程 ===")
    
    manager = NgrokManager()
    
    # 模拟隧道运行状态
    manager.is_running = True
    manager.tunnel = type('obj', (object,), {'public_url': 'http://test.ngrok.io'})()
    manager.public_url = 'http://test.ngrok.io'
    
    # 记录开始时间
    start_time = time.time()
    
    # 调用异步停止
    stop_called = False
    
    def callback():
        nonlocal stop_called
        stop_called = True
    
    manager.stop_tunnel(async_mode=True, callback=callback)
    
    # 立即检查调用时间
    elapsed_time = time.time() - start_time
    
    # 异步调用应该几乎立即返回（小于0.1秒）
    assert elapsed_time < 0.1, f"异步停止应该立即返回，但用了 {elapsed_time:.3f} 秒"
    
    print(f"✅ 异步停止立即返回（用时 {elapsed_time:.3f} 秒）")
    
    # 等待后台线程完成
    time.sleep(2)
    
    # 验证停止操作已完成
    assert not manager.is_running, "隧道应该已停止"
    assert manager.tunnel is None, "tunnel 应该被清理"
    assert manager.public_url is None, "public_url 应该被清理"
    
    # 验证回调被调用
    assert stop_called, "回调函数应该被调用"
    
    print("✅ 异步停止成功完成，状态已清理")
    return True


def test_sync_stop_blocks():
    """测试同步停止会阻塞（对比测试）"""
    print("\n=== 测试同步停止（对比）===")
    
    manager = NgrokManager()
    
    # 模拟隧道运行状态
    manager.is_running = True
    manager.tunnel = type('obj', (object,), {'public_url': 'http://test.ngrok.io'})()
    manager.public_url = 'http://test.ngrok.io'
    
    # 记录开始时间
    start_time = time.time()
    
    # 调用同步停止
    manager.stop_tunnel(async_mode=False)
    
    # 检查调用时间
    elapsed_time = time.time() - start_time
    
    # 同步调用会等待监控线程（最多1秒）
    print(f"同步停止用时 {elapsed_time:.3f} 秒")
    
    # 验证停止操作已完成
    assert not manager.is_running, "隧道应该已停止"
    assert manager.tunnel is None, "tunnel 应该被清理"
    assert manager.public_url is None, "public_url 应该被清理"
    
    print("✅ 同步停止成功完成")
    return True


def test_async_kill_all():
    """测试异步 kill_all 不会阻塞"""
    print("\n=== 测试异步 kill_all ===")
    
    manager = NgrokManager()
    
    # 模拟隧道运行状态
    manager.is_running = True
    
    # 记录开始时间
    start_time = time.time()
    
    # 调用异步 kill_all
    manager.kill_all(async_mode=True)
    
    # 立即检查调用时间
    elapsed_time = time.time() - start_time
    
    # 异步调用应该几乎立即返回
    assert elapsed_time < 0.1, f"异步 kill_all 应该立即返回，但用了 {elapsed_time:.3f} 秒"
    
    print(f"✅ 异步 kill_all 立即返回（用时 {elapsed_time:.3f} 秒）")
    
    # 等待后台线程完成
    time.sleep(2)
    
    # 验证状态已清理
    assert not manager.is_running, "隧道应该已停止"
    
    print("✅ 异步 kill_all 成功完成")
    return True


def test_rapid_restart():
    """测试快速重启能力"""
    print("\n=== 测试快速重启能力 ===")
    
    manager = NgrokManager()
    
    # 模拟启动
    manager.is_running = True
    manager.tunnel = type('obj', (object,), {'public_url': 'http://test1.ngrok.io'})()
    manager.public_url = 'http://test1.ngrok.io'
    
    # 异步停止
    manager.stop_tunnel(async_mode=True)
    
    # 立即重新启动（模拟）
    # 由于 is_running 已经在 async 停止中被设置为 False，可以立即重启
    assert not manager.is_running, "停止后 is_running 应该立即变为 False"
    
    print("✅ 快速重启测试通过（状态立即更新）")
    return True


def test_multiple_async_stops():
    """测试多次异步停止调用不会导致问题"""
    print("\n=== 测试多次异步停止调用 ===")
    
    manager = NgrokManager()
    
    # 模拟隧道运行状态
    manager.is_running = True
    manager.tunnel = type('obj', (object,), {'public_url': 'http://test.ngrok.io'})()
    manager.public_url = 'http://test.ngrok.io'
    
    # 多次调用异步停止
    for i in range(3):
        manager.stop_tunnel(async_mode=True)
        time.sleep(0.1)
    
    print("✅ 多次异步停止调用不会崩溃")
    
    # 等待所有操作完成
    time.sleep(2)
    
    # 验证最终状态
    assert not manager.is_running, "隧道应该已停止"
    
    print("✅ 最终状态正确")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试 ngrok 异步停止功能")
    print("=" * 60)
    
    tests = [
        test_async_stop_non_blocking,
        test_sync_stop_blocks,
        test_async_kill_all,
        test_rapid_restart,
        test_multiple_async_stops,
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
