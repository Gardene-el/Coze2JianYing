#!/usr/bin/env python3
"""
显示GUI并截图
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from PIL import Image
import time

# Import the main window
from app.gui.main_window import MainWindow

def take_screenshot():
    """创建GUI并截图"""
    print("创建主窗口...")
    app = MainWindow()
    
    # 等待窗口渲染
    app.root.update()
    time.sleep(0.5)
    app.root.update()
    
    print("截图标签页 1 (草稿生成)...")
    # 截取第一个标签页
    x = app.root.winfo_rootx()
    y = app.root.winfo_rooty()
    w = app.root.winfo_width()
    h = app.root.winfo_height()
    
    # 使用PIL截图
    import subprocess
    subprocess.run(['import', '-window', 'root', '/tmp/tabbed_gui_tab1.png'], check=False)
    
    print("切换到标签页 2 (示例标签页)...")
    # 切换到第二个标签页
    app.notebook.select(1)
    app.root.update()
    time.sleep(0.5)
    
    print("截图标签页 2...")
    subprocess.run(['import', '-window', 'root', '/tmp/tabbed_gui_tab2.png'], check=False)
    
    # 关闭窗口
    app.root.destroy()
    
    print("✅ 截图完成")
    print("  - /tmp/tabbed_gui_tab1.png (草稿生成标签页)")
    print("  - /tmp/tabbed_gui_tab2.png (示例标签页)")

if __name__ == "__main__":
    take_screenshot()
