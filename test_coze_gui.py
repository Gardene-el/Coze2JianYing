#!/usr/bin/env python3
"""
GUI测试脚本 - 显示本地服务标签页（包含Coze API设置）
"""
import sys
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def create_test_gui():
    """创建测试GUI窗口"""
    root = tk.Tk()
    root.title("Coze2JianYing - 本地服务标签页测试")
    root.geometry("900x750")
    
    # 创建Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 导入并创建本地服务标签页
    from app.gui.local_service_tab import LocalServiceTab
    
    # 简单的日志回调
    def log_callback(message):
        print(f"[LOG] {message}")
    
    # 创建本地服务标签页
    local_service_tab = LocalServiceTab(notebook, log_callback=log_callback)
    
    # 添加一些测试数据
    local_service_tab.token_var.set("pat_xxx...示例token")
    local_service_tab.base_url_var.set("https://api.coze.cn")
    
    return root, local_service_tab

def take_screenshot(widget, filename):
    """截取窗口截图"""
    try:
        # 等待窗口完全渲染
        widget.update()
        time.sleep(0.5)
        
        # 获取窗口位置和大小
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        width = widget.winfo_width()
        height = widget.winfo_height()
        
        # 使用PIL截图
        from PIL import ImageGrab
        
        # 截取屏幕区域
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screenshot.save(filename)
        print(f"✅ 截图已保存: {filename}")
        return True
        
    except ImportError:
        print("⚠️ PIL/Pillow 未安装，无法截图")
        print("   可以运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return False

def main():
    """主函数"""
    print("=== GUI 测试 - 本地服务标签页（Coze API设置） ===\n")
    
    try:
        # 创建GUI
        root, tab = create_test_gui()
        
        print("✅ GUI 创建成功")
        print("📝 标签页包含以下组件:")
        print("   1. 草稿文件夹设置")
        print("   2. Coze API 配置 (新增)")
        print("      - API Token 输入框（密码模式）")
        print("      - 显示/隐藏按钮")
        print("      - 服务地址选择（下拉框）")
        print("      - 测试连接按钮")
        print("   3. FastAPI 服务管理")
        
        # 等待窗口渲染
        root.update()
        time.sleep(1)
        
        # 尝试截图
        screenshot_taken = take_screenshot(root, "local_service_tab_with_coze_api.png")
        
        if screenshot_taken:
            print("\n💡 截图已保存，按任意键关闭窗口...")
            # 保持窗口打开3秒
            root.after(3000, root.destroy)
        else:
            print("\n💡 GUI窗口将保持打开5秒供查看...")
            root.after(5000, root.destroy)
        
        root.mainloop()
        
        print("\n✅ GUI 测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ GUI 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
