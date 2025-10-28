"""
日志窗口模块
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class LogWindow:
    """日志窗口类"""
    
    def __init__(self, parent):
        """
        初始化日志窗口
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("日志查看器")
        self.window.geometry("800x500")
        
        # 允许窗口调整大小
        self.window.resizable(True, True)
        
        # 设置最小窗口大小
        self.window.minsize(600, 400)
        
        # 创建UI
        self._create_widgets()
        self._setup_layout()
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 工具栏
        toolbar = ttk.Frame(main_frame)
        
        # 按钮
        self.clear_btn = ttk.Button(
            toolbar,
            text="清空日志",
            command=self._clear_logs
        )
        self.save_btn = ttk.Button(
            toolbar,
            text="保存日志",
            command=self._save_logs
        )
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ttk.Checkbutton(
            toolbar,
            text="自动滚动",
            variable=self.auto_scroll_var
        )
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        
        # 配置文本标签（不同日志级别使用不同颜色）
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="gray")
        
        # 保存组件引用
        self.main_frame = main_frame
        self.toolbar = toolbar
        
        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def _setup_layout(self):
        """设置布局"""
        # 工具栏
        self.toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_scroll_check.pack(side=tk.LEFT)
        
        # 日志文本框
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def append_log(self, message: str):
        """
        添加日志消息
        
        Args:
            message: 日志消息
        """
        if not self.is_open():
            return
        
        # 确定日志级别
        tag = "INFO"
        if "ERROR" in message:
            tag = "ERROR"
        elif "WARNING" in message:
            tag = "WARNING"
        elif "DEBUG" in message:
            tag = "DEBUG"
        
        # 添加日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.config(state=tk.DISABLED)
        
        # 自动滚动到底部
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        # 强制更新显示
        self.log_text.update_idletasks()
    
    def _clear_logs(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _save_logs(self):
        """保存日志到文件"""
        from tkinter import filedialog
        
        # 获取日志内容
        log_content = self.log_text.get("1.0", tk.END)
        
        # 选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                from tkinter import messagebox
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def _on_closing(self):
        """窗口关闭事件"""
        self.window.destroy()
    
    def is_open(self) -> bool:
        """检查窗口是否打开"""
        try:
            return self.window.winfo_exists()
        except:
            return False
    
    def focus(self):
        """将焦点设置到日志窗口"""
        if self.is_open():
            self.window.lift()
            self.window.focus_force()
