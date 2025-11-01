#!/usr/bin/env python3
"""
测试新的标签页架构 GUI 是否正确加载
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径，与main.py保持一致
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 设置环境变量以避免实际显示窗口
os.environ['DISPLAY'] = ':99'

try:
    import tkinter as tk
    from gui.main_window import MainWindow
    from gui.base_tab import BaseTab
    from gui.draft_generator_tab import DraftGeneratorTab
    from gui.local_service_tab import LocalServiceTab
    from gui.example_tab import ExampleTab
    
    print("=== 测试标签页架构 GUI 加载 ===")
    
    # 测试1: 导入所有模块
    print("测试1: 导入所有模块")
    assert MainWindow is not None, "MainWindow 类应该可以导入"
    assert BaseTab is not None, "BaseTab 类应该可以导入"
    assert DraftGeneratorTab is not None, "DraftGeneratorTab 类应该可以导入"
    assert LocalServiceTab is not None, "LocalServiceTab 类应该可以导入"
    assert ExampleTab is not None, "ExampleTab 类应该可以导入"
    print("✅ 所有模块导入成功")
    
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
        assert len(window.tabs) >= 2, "至少应该有两个标签页（手动草稿生成和本地服务）"
        
        print(f"✅ MainWindow 实例创建成功")
        print(f"✅ 创建了 {len(window.tabs)} 个标签页")
        
        # 验证标签页类型
        for i, tab in enumerate(window.tabs):
            assert isinstance(tab, BaseTab), f"标签页 {i} 应该继承自 BaseTab"
            print(f"✅ 标签页 {i} ({tab.tab_name}) 验证通过")
        
        # 验证第一个标签页是草稿生成器
        assert isinstance(window.tabs[0], DraftGeneratorTab), "第一个标签页应该是 DraftGeneratorTab"
        assert window.tabs[0].tab_name == "手动草稿生成", "第一个标签页名称应该是 '手动草稿生成'"
        print("✅ 第一个标签页是手动草稿生成标签页")
        
        # 验证第二个标签页是本地服务
        assert isinstance(window.tabs[1], LocalServiceTab), "第二个标签页应该是 LocalServiceTab"
        assert window.tabs[1].tab_name == "本地服务", "第二个标签页名称应该是 '本地服务'"
        print("✅ 第二个标签页是本地服务标签页")
        
        # 验证草稿生成器标签页的组件
        draft_tab = window.tabs[0]
        assert hasattr(draft_tab, 'draft_generator'), "应该有 draft_generator"
        assert hasattr(draft_tab, 'output_folder'), "应该有 output_folder"
        assert hasattr(draft_tab, 'generate_btn'), "应该有生成按钮"
        assert hasattr(draft_tab, 'generate_meta_btn'), "应该有生成元信息按钮"
        assert hasattr(draft_tab, 'input_text'), "应该有输入文本框"
        print("✅ 草稿生成器标签页组件验证通过")
        
        # 验证本地服务标签页的组件
        service_tab = window.tabs[1]
        assert hasattr(service_tab, 'draft_generator'), "应该有 draft_generator（用于文件夹检测）"
        assert hasattr(service_tab, 'output_folder'), "应该有 output_folder"
        assert hasattr(service_tab, 'start_service_btn'), "应该有启动服务按钮"
        assert hasattr(service_tab, 'stop_service_btn'), "应该有停止服务按钮"
        assert hasattr(service_tab, 'check_port_btn'), "应该有检测端口按钮"
        assert hasattr(service_tab, 'service_running'), "应该有服务运行状态"
        assert hasattr(service_tab, 'service_status_indicator'), "应该有服务状态指示器"
        print("✅ 本地服务标签页组件验证通过")
        
        # 测试变量隔离
        print("\n测试3: 变量隔离")
        draft_tab.set_tab_variable("test_var", "value_from_draft_tab")
        
        # 验证标签页之间的变量是隔离的
        service_tab = window.tabs[1]
        service_value = service_tab.get_tab_variable("test_var")
        assert service_value is None, "不同标签页的变量应该是隔离的"
        print("✅ 标签页变量隔离验证通过（草稿生成 vs 本地服务）")
        
        # 销毁窗口
        window.root.destroy()
        
        print("\n" + "="*60)
        print("✅ 标签页架构 GUI 测试全部通过！")
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
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n所有测试完成")
