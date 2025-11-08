#!/usr/bin/env python3
"""
测试 ngrok 可选 authtoken 功能

验证 ngrok 可以在不提供 authtoken 的情况下正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.ngrok_manager import NgrokManager


def test_ngrok_manager_without_authtoken():
    """测试 NgrokManager 可以不使用 authtoken 初始化"""
    print("=== 测试 NgrokManager 无 authtoken 初始化 ===")
    
    try:
        manager = NgrokManager()
        assert manager is not None, "NgrokManager 实例应该成功创建"
        print("✅ NgrokManager 成功创建（无 authtoken）")
        
        # 验证 is_ngrok_available 方法可以正常调用
        available = manager.is_ngrok_available()
        print(f"   ngrok 可用性: {available}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_start_tunnel_signature():
    """测试 start_tunnel 方法签名支持可选的 authtoken"""
    print("\n=== 测试 start_tunnel 方法签名 ===")
    
    try:
        import inspect
        from app.utils.ngrok_manager import NgrokManager
        
        sig = inspect.signature(NgrokManager.start_tunnel)
        params = sig.parameters
        
        # 检查 authtoken 参数是否存在且为可选
        assert 'authtoken' in params, "start_tunnel 应该有 authtoken 参数"
        
        authtoken_param = params['authtoken']
        
        # 检查是否有默认值（None）
        has_default = authtoken_param.default != inspect.Parameter.empty
        assert has_default, "authtoken 参数应该有默认值"
        
        default_value = authtoken_param.default
        assert default_value is None, f"authtoken 默认值应该是 None，实际是 {default_value}"
        
        print(f"✅ authtoken 参数配置正确:")
        print(f"   - 参数类型: {authtoken_param.annotation}")
        print(f"   - 默认值: {default_value}")
        print(f"   - 是可选的: True")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_labels():
    """测试 GUI 标签是否正确显示 authtoken 为可选"""
    print("\n=== 测试 GUI 标签文本 ===")
    
    try:
        # 读取 cloud_service_tab.py 文件内容
        tab_file = os.path.join(os.path.dirname(__file__), '..', 'app', 'gui', 'cloud_service_tab.py')
        
        with open(tab_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含 "Authtoken (可选)" 标签
        assert 'text="Authtoken (可选):"' in content, "GUI 应该显示 'Authtoken (可选):'"
        print("✅ GUI 标签正确显示 'Authtoken (可选):'")
        
        # 检查是否有帮助方法
        assert '_show_authtoken_help' in content, "GUI 应该有 _show_authtoken_help 方法"
        print("✅ GUI 包含帮助方法 _show_authtoken_help")
        
        # 检查是否有提示信息
        assert '无需注册即可使用' in content or '免费使用' in content, "GUI 应该包含免费使用的提示"
        print("✅ GUI 包含免费使用的提示信息")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_documentation():
    """测试文档是否明确说明 authtoken 为可选"""
    print("\n=== 测试文档内容 ===")
    
    try:
        doc_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'guides', 'NGROK_USAGE_GUIDE.md')
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否强调了无需注册
        checks = [
            ('无需注册' in content, "文档应该说明'无需注册'"),
            ('免费使用' in content, "文档应该说明'免费使用'"),
            ('可选' in content, "文档应该说明 authtoken '可选'"),
            ('完全可选' in content or '可以留空' in content, "文档应该明确说明可以留空"),
        ]
        
        passed = 0
        for check, msg in checks:
            if check:
                print(f"✅ {msg}")
                passed += 1
            else:
                print(f"⚠️  {msg}")
        
        assert passed >= 3, f"至少应该通过 3/4 的文档检查，实际通过 {passed}/4"
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试 ngrok 可选 authtoken 功能")
    print("=" * 60)
    
    tests = [
        test_ngrok_manager_without_authtoken,
        test_start_tunnel_signature,
        test_gui_labels,
        test_documentation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试异常: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"测试总结: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
