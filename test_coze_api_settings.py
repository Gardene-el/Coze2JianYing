#!/usr/bin/env python3
"""
测试 Coze API 设置功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    print("=== 测试导入 ===")
    
    try:
        from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL, COZE_COM_BASE_URL
        print(f"✅ cozepy 导入成功")
        print(f"   COZE_CN_BASE_URL: {COZE_CN_BASE_URL}")
        print(f"   COZE_COM_BASE_URL: {COZE_COM_BASE_URL}")
    except ImportError as e:
        print(f"❌ cozepy 导入失败: {e}")
        return False
    
    return True

def test_local_service_tab_structure():
    """测试 LocalServiceTab 的结构"""
    print("\n=== 测试 LocalServiceTab 结构 ===")
    
    try:
        # 读取文件内容
        with open("app/gui/local_service_tab.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否有 Coze API 相关的导入
        if "from cozepy import" in content:
            print("✅ 包含 cozepy 导入")
        else:
            print("❌ 缺少 cozepy 导入")
            return False
        
        # 检查是否有 Coze API 配置区域
        if "Coze API 配置" in content:
            print("✅ 包含 Coze API 配置区域")
        else:
            print("❌ 缺少 Coze API 配置区域")
            return False
        
        # 检查是否有相关的变量
        required_vars = [
            "self.coze_api_token",
            "self.coze_base_url",
            "self.coze_client",
            "self.token_var",
            "self.base_url_var"
        ]
        
        for var in required_vars:
            if var in content:
                print(f"✅ 包含变量: {var}")
            else:
                print(f"❌ 缺少变量: {var}")
                return False
        
        # 检查是否有相关方法
        required_methods = [
            "_toggle_token_visibility",
            "_test_coze_connection",
            "_get_coze_client"
        ]
        
        for method in required_methods:
            if f"def {method}" in content:
                print(f"✅ 包含方法: {method}")
            else:
                print(f"❌ 缺少方法: {method}")
                return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

def test_ui_components():
    """测试 UI 组件"""
    print("\n=== 测试 UI 组件 ===")
    
    try:
        with open("app/gui/local_service_tab.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查 UI 组件
        ui_components = [
            "self.coze_frame",
            "self.token_label",
            "self.token_entry",
            "self.show_token_btn",
            "self.base_url_label",
            "self.base_url_combo",
            "self.coze_status_label",
            "self.test_coze_btn"
        ]
        
        for component in ui_components:
            if component in content:
                print(f"✅ 包含 UI 组件: {component}")
            else:
                print(f"❌ 缺少 UI 组件: {component}")
                return False
        
        # 检查密码输入框配置
        if 'show="*"' in content:
            print("✅ Token 输入框配置为密码模式")
        else:
            print("❌ Token 输入框未配置为密码模式")
            return False
        
        # 检查布局配置
        if "self.coze_frame.grid" in content:
            print("✅ Coze 配置框已添加到布局")
        else:
            print("❌ Coze 配置框未添加到布局")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试 Coze API 设置功能...\n")
    
    results = []
    
    # 运行测试
    results.append(("导入测试", test_imports()))
    results.append(("结构测试", test_local_service_tab_structure()))
    results.append(("UI组件测试", test_ui_components()))
    
    # 总结
    print("\n=== 测试总结 ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
