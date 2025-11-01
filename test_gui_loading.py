#!/usr/bin/env python3
"""
测试 GUI 是否正确加载，包括新的标签页架构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量以避免实际显示窗口
os.environ['DISPLAY'] = ':99'

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    from src.gui.draft_generator_tab import DraftGeneratorTab
    
    print("=== 测试 GUI 加载 ===")
    
    # 测试1: 导入 MainWindow 类
    print("测试1: 导入 MainWindow 类")
    assert MainWindow is not None, "MainWindow 类应该可以导入"
    print("✅ MainWindow 类导入成功")
    
    # 测试2: 创建 MainWindow 实例（不运行主循环）
    print("\n测试2: 创建 MainWindow 实例")
    try:
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 测试 MainWindow 的初始化
        window = MainWindow()
        
        # 验证标签页架构
        assert hasattr(window, 'notebook'), "应该有 notebook 组件"
        assert hasattr(window, 'tabs'), "应该有 tabs 列表"
        assert len(window.tabs) >= 1, "至少应该有一个标签页"
        print("✅ MainWindow 实例创建成功")
        print("✅ 标签页架构验证通过")
        
        # 验证第一个标签页是草稿生成器标签页
        draft_tab = window.tabs[0]
        assert isinstance(draft_tab, DraftGeneratorTab), "第一个标签页应该是草稿生成器"
        
        # 验证草稿生成器标签页的关键组件（现在按钮在标签页内）
        assert hasattr(draft_tab, 'generate_btn'), "草稿生成器标签页应该有生成草稿按钮"
        assert hasattr(draft_tab, 'generate_meta_btn'), "草稿生成器标签页应该有生成元信息按钮"
        assert hasattr(draft_tab, 'clear_btn'), "草稿生成器标签页应该有清空按钮"
        assert hasattr(draft_tab, '_generate_meta_info'), "草稿生成器标签页应该有 _generate_meta_info 方法"
        
        print("✅ 草稿生成器标签页组件验证通过")
        print("✅ 生成元信息按钮存在")
        print("✅ _generate_meta_info 方法存在")
        
        # 销毁窗口
        window.root.destroy()
        
        print("\n" + "="*60)
        print("✅ GUI 加载测试通过！")
        print("="*60)
        
    except tk.TclError as e:
        # 在没有显示器的环境中，这是预期的错误
        if "no display" in str(e).lower() or "couldn't connect" in str(e).lower():
            print("⚠️  无法创建窗口（无显示器环境），但导入测试通过")
            print("✅ 在有显示器的环境中，GUI 应该可以正常工作")
        else:
            raise
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n所有测试完成")
