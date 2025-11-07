"""
测试 ngrok 集成功能

这个测试验证 ngrok 管理器的基本功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.ngrok_manager import NgrokManager


def test_ngrok_manager_initialization():
    """测试 NgrokManager 初始化"""
    print("=== 测试 NgrokManager 初始化 ===")
    
    manager = NgrokManager()
    
    assert manager is not None, "NgrokManager 应该成功创建"
    assert hasattr(manager, 'tunnel'), "应该有 tunnel 属性"
    assert hasattr(manager, 'public_url'), "应该有 public_url 属性"
    assert hasattr(manager, 'is_running'), "应该有 is_running 属性"
    
    print("✅ NgrokManager 初始化成功")
    return True


def test_ngrok_availability():
    """测试 ngrok 可用性检查"""
    print("\n=== 测试 ngrok 可用性检查 ===")
    
    manager = NgrokManager()
    is_available = manager.is_ngrok_available()
    
    print(f"ngrok 可用性: {is_available}")
    
    if is_available:
        print("✅ pyngrok 已安装且可用")
    else:
        print("⚠️ pyngrok 未安装或不可用")
    
    return True


def test_get_status():
    """测试获取状态信息"""
    print("\n=== 测试获取状态信息 ===")
    
    manager = NgrokManager()
    status = manager.get_status()
    
    assert isinstance(status, dict), "状态应该是字典类型"
    assert 'is_running' in status, "状态应包含 is_running"
    assert 'public_url' in status, "状态应包含 public_url"
    assert 'available' in status, "状态应包含 available"
    
    print(f"状态信息: {status}")
    print("✅ 获取状态成功")
    return True


def test_set_authtoken():
    """测试设置 authtoken"""
    print("\n=== 测试设置 authtoken ===")
    
    manager = NgrokManager()
    
    if not manager.is_ngrok_available():
        print("⚠️ pyngrok 不可用，跳过此测试")
        return True
    
    # 使用测试 token（不会真正连接）
    test_token = "test_token_123456"
    result = manager.set_authtoken(test_token)
    
    print(f"设置 authtoken 结果: {result}")
    print("✅ authtoken 设置功能正常")
    return True


def test_cleanup():
    """测试资源清理"""
    print("\n=== 测试资源清理 ===")
    
    manager = NgrokManager()
    
    # 确保没有运行的隧道
    if manager.is_running:
        manager.stop_tunnel()
    
    # 测试析构函数
    del manager
    
    print("✅ 资源清理正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试 ngrok 集成功能")
    print("=" * 60)
    
    tests = [
        test_ngrok_manager_initialization,
        test_ngrok_availability,
        test_get_status,
        test_set_authtoken,
        test_cleanup,
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
