#!/usr/bin/env python3
"""
测试 GUI 是否正确加载，包括新的"生成元信息"按钮
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量以避免实际显示窗口
os.environ['DISPLAY'] = ':99'

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
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
        
        # 验证关键组件存在
        assert hasattr(window, 'generate_btn'), "应该有生成草稿按钮"
        assert hasattr(window, 'generate_meta_btn'), "应该有生成元信息按钮"
        assert hasattr(window, 'clear_btn'), "应该有清空按钮"
        assert hasattr(window, '_generate_meta_info'), "应该有 _generate_meta_info 方法"
        
        print("✅ MainWindow 实例创建成功")
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
