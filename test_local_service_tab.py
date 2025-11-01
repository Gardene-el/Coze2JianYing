#!/usr/bin/env python3
"""
测试本地服务标签页的基本功能
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from gui.local_service_tab import LocalServiceTab
        print("✅ LocalServiceTab 导入成功")
    except Exception as e:
        print(f"❌ LocalServiceTab 导入失败: {e}")
        return False
    
    try:
        from gui.draft_generator_tab import DraftGeneratorTab
        print("✅ DraftGeneratorTab 导入成功")
    except Exception as e:
        print(f"❌ DraftGeneratorTab 导入失败: {e}")
        return False
    
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
    except Exception as e:
        print(f"❌ MainWindow 导入失败: {e}")
        return False
    
    return True

def test_class_structure():
    """测试类结构"""
    print("\n=== 测试类结构 ===")
    
    try:
        from gui.local_service_tab import LocalServiceTab
        from gui.base_tab import BaseTab
        
        # 检查继承关系
        if issubclass(LocalServiceTab, BaseTab):
            print("✅ LocalServiceTab 正确继承自 BaseTab")
        else:
            print("❌ LocalServiceTab 未继承自 BaseTab")
            return False
        
        # 检查必要的方法
        required_methods = ['_create_widgets', '_setup_layout', 'cleanup']
        for method in required_methods:
            if hasattr(LocalServiceTab, method):
                print(f"✅ LocalServiceTab 有方法: {method}")
            else:
                print(f"❌ LocalServiceTab 缺少方法: {method}")
                return False
        
        # 检查特定方法
        service_methods = ['_start_service', '_stop_service', '_run_service']
        for method in service_methods:
            if hasattr(LocalServiceTab, method):
                print(f"✅ LocalServiceTab 有服务管理方法: {method}")
            else:
                print(f"❌ LocalServiceTab 缺少服务管理方法: {method}")
                return False
        
    except Exception as e:
        print(f"❌ 类结构测试失败: {e}")
        return False
    
    return True

def test_tab_names():
    """测试标签页名称"""
    print("\n=== 测试标签页名称 ===")
    
    try:
        # 检查源代码中的标签名称
        with open(Path(__file__).parent / "src" / "gui" / "draft_generator_tab.py", "r", encoding="utf-8") as f:
            draft_content = f.read()
            if '"手动草稿生成"' in draft_content:
                print('✅ DraftGeneratorTab 使用名称 "手动草稿生成"')
            else:
                print('❌ DraftGeneratorTab 未使用名称 "手动草稿生成"')
                return False
        
        with open(Path(__file__).parent / "src" / "gui" / "local_service_tab.py", "r", encoding="utf-8") as f:
            service_content = f.read()
            if '"本地服务"' in service_content:
                print('✅ LocalServiceTab 使用名称 "本地服务"')
            else:
                print('❌ LocalServiceTab 未使用名称 "本地服务"')
                return False
        
    except Exception as e:
        print(f"❌ 标签名称测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试本地服务标签页功能...\n")
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("类结构", test_class_structure()))
    results.append(("标签名称", test_tab_names()))
    
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
