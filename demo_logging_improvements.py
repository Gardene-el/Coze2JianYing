#!/usr/bin/env python3
"""
演示日志系统改进

这个脚本模拟草稿生成过程，展示:
1. 可调整大小的日志窗口
2. 后台线程处理，不阻塞UI
3. 实时日志输出
"""
import sys
import os
import time
import tkinter as tk
from tkinter import ttk
import threading

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger, get_logger, set_gui_log_callback
from gui.log_window import LogWindow


class DemoWindow:
    """演示窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("日志系统改进演示")
        self.root.geometry("600x400")
        
        # 设置日志
        setup_logger()
        self.logger = get_logger(__name__)
        
        # 日志窗口
        self.log_window = None
        
        # 后台任务状态
        self.is_running = False
        self.task_thread = None
        
        # 设置GUI日志回调
        set_gui_log_callback(self._on_log_message)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建UI组件"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明文本
        info_text = """
日志系统改进演示

改进内容:
1. 日志窗口可以自由调整大小（拖拽窗口边缘试试）
2. 模拟任务在后台线程运行，不会阻塞主窗口
3. 日志实时显示每个步骤，便于监控和调试

点击"开始演示"按钮查看效果！
        """
        
        info_label = ttk.Label(
            main_frame,
            text=info_text,
            justify=tk.LEFT,
            font=("Arial", 10)
        )
        info_label.pack(pady=20)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="开始演示",
            command=self._start_demo
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.log_btn = ttk.Button(
            button_frame,
            text="打开日志窗口",
            command=self._show_log_window
        )
        self.log_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 10, "bold")
        )
        status_label.pack(pady=10)
    
    def _show_log_window(self):
        """显示日志窗口"""
        if self.log_window is None or not self.log_window.is_open():
            self.log_window = LogWindow(self.root)
        else:
            self.log_window.focus()
    
    def _start_demo(self):
        """开始演示"""
        if self.is_running:
            return
        
        # 自动打开日志窗口
        self._show_log_window()
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("运行中...")
        
        self.logger.info("=" * 60)
        self.logger.info("开始演示日志系统改进")
        self.logger.info("=" * 60)
        
        # 在后台线程中运行
        self.task_thread = threading.Thread(
            target=self._demo_worker,
            daemon=True
        )
        self.task_thread.start()
        
        # 检查状态
        self._check_status()
    
    def _demo_worker(self):
        """后台工作线程"""
        try:
            # 模拟草稿生成过程
            steps = [
                "解析JSON输入数据",
                "验证数据格式",
                "创建草稿文件夹",
                "下载视频素材 (1/3)",
                "下载视频素材 (2/3)",
                "下载视频素材 (3/3)",
                "下载音频素材 (1/2)",
                "下载音频素材 (2/2)",
                "创建视频轨道",
                "添加视频片段",
                "创建音频轨道",
                "添加音频片段",
                "生成元数据",
                "保存草稿文件",
                "验证草稿完整性"
            ]
            
            for i, step in enumerate(steps, 1):
                self.logger.info(f"步骤 {i}/{len(steps)}: {step}")
                time.sleep(0.5)  # 模拟耗时操作
                
                # 模拟某些步骤有警告
                if i == 7:
                    self.logger.warning("音频文件较大，下载时间可能较长")
                
                # 模拟进度更新
                progress = int((i / len(steps)) * 100)
                self.root.after(0, self.status_var.set, f"运行中... {progress}%")
            
            self.logger.info("=" * 60)
            self.logger.info("✅ 草稿生成完成！")
            self.logger.info("=" * 60)
            
            # 完成回调
            self.root.after(0, self._on_demo_complete)
            
        except Exception as e:
            self.logger.error(f"演示过程出错: {e}", exc_info=True)
            self.root.after(0, self._on_demo_error, e)
    
    def _check_status(self):
        """检查任务状态"""
        if self.task_thread and self.task_thread.is_alive():
            self.root.after(100, self._check_status)
        else:
            self.is_running = False
    
    def _on_demo_complete(self):
        """演示完成"""
        self.status_var.set("✅ 演示完成！")
        self.start_btn.config(state=tk.NORMAL)
        
        # 显示提示
        from tkinter import messagebox
        messagebox.showinfo(
            "演示完成",
            "演示完成！\n\n"
            "注意观察:\n"
            "1. 日志窗口可以调整大小\n"
            "2. 主窗口在生成过程中保持响应\n"
            "3. 每个步骤的日志都实时显示"
        )
    
    def _on_demo_error(self, error):
        """演示出错"""
        self.status_var.set("❌ 演示出错")
        self.start_btn.config(state=tk.NORMAL)
    
    def _on_log_message(self, message: str):
        """处理日志消息（线程安全）"""
        def update_log():
            if self.log_window and self.log_window.is_open():
                self.log_window.append_log(message)
        
        try:
            self.root.after(0, update_log)
        except:
            pass
    
    def run(self):
        """运行演示"""
        self.root.mainloop()


def main():
    """主函数"""
    print("启动日志系统改进演示...")
    print("\n说明:")
    print("1. 点击 '开始演示' 按钮启动模拟任务")
    print("2. 观察日志窗口实时显示每个步骤")
    print("3. 尝试调整日志窗口大小（拖拽边缘）")
    print("4. 注意主窗口在运行过程中保持响应\n")
    
    app = DemoWindow()
    app.run()


if __name__ == "__main__":
    main()
