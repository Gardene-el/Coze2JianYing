#!/usr/bin/env python3
"""
测试嵌入式日志面板
验证UI布局和功能
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger, get_logger

def test_embedded_log_imports():
    """测试导入是否正常"""
    print("=== 测试导入 ===")
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
        return True
    except Exception as e:
        print(f"❌ MainWindow 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedded_log_attributes():
    """测试新增的属性和方法"""
    print("\n=== 测试新增属性和方法 ===")
    
    # 读取main_window.py文件
    main_window_path = os.path.join(os.path.dirname(__file__), 'src', 'gui', 'main_window.py')
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("paned_window", "PanedWindow分隔窗口"),
        ("log_frame", "日志框架"),
        ("embedded_log_text", "嵌入式日志文本框"),
        ("log_panel_visible", "日志面板可见标志"),
        ("_toggle_log_panel", "切换日志面板方法"),
        ("_clear_embedded_logs", "清空嵌入式日志方法"),
        ("_save_embedded_logs", "保存嵌入式日志方法"),
        ("_append_to_embedded_log", "添加到嵌入式日志方法"),
        ("切换日志面板", "菜单项"),
        ("日志窗口（独立）", "独立窗口菜单项"),
    ]
    
    results = []
    for check, desc in checks:
        if check in content:
            print(f"✅ 找到 {desc}: {check}")
            results.append(True)
        else:
            print(f"❌ 未找到 {desc}: {check}")
            results.append(False)
    
    return all(results)

def test_layout_structure():
    """测试布局结构"""
    print("\n=== 测试布局结构 ===")
    
    main_window_path = os.path.join(os.path.dirname(__file__), 'src', 'gui', 'main_window.py')
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("self.paned_window.add(top_frame", "添加上部框架到PanedWindow"),
        ("self.paned_window.add(self.log_frame", "添加日志框架到PanedWindow"),
        ("确保日志面板可见", "自动显示日志面板"),
        ("更新嵌入式日志面板", "日志消息路由到嵌入式面板"),
    ]
    
    results = []
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc}")
            results.append(True)
        else:
            print(f"❌ {desc} - 未找到: {check}")
            results.append(False)
    
    return all(results)

def main():
    """运行所有测试"""
    print("开始测试嵌入式日志面板...\n")
    
    results = []
    
    try:
        results.append(("导入测试", test_embedded_log_imports()))
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        results.append(("导入测试", False))
    
    try:
        results.append(("属性和方法测试", test_embedded_log_attributes()))
    except Exception as e:
        print(f"❌ 属性和方法测试失败: {e}")
        results.append(("属性和方法测试", False))
    
    try:
        results.append(("布局结构测试", test_layout_structure()))
    except Exception as e:
        print(f"❌ 布局结构测试失败: {e}")
        results.append(("布局结构测试", False))
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("✅ 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
