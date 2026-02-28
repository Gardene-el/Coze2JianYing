"""
日志窗口模块 (CustomTkinter Refactor)
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
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
        self.window = ctk.CTkToplevel(parent)
        self.window.title("日志查看器")
        self.window.geometry("800x500")
        
        # 允许窗口调整大小
        self.window.resizable(True, True)
        
        # 设置最小窗口大小
        self.window.minsize(600, 400)
        
        # 确保窗口在最前
        self.window.lift()
        self.window.focus_force()
        
        # 创建UI
        self._create_widgets()
        self._setup_layout()
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=15, fg_color=("white", "#2D2D2D"))
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  

        # 工具栏
        self.toolbar = ctk.CTkFrame(self.main_frame, fg_color="transparent")    

        # 按钮
        self.clear_btn = ctk.CTkButton(
            self.toolbar,
            text="清空日志",
            command=self._clear_logs,
            width=100,
            corner_radius=8,
            fg_color=("gray75", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray65", "gray35")
        )
        self.save_btn = ctk.CTkButton(
            self.toolbar,
            text="保存日志",
            command=self._save_logs,
            width=100,
            corner_radius=8,
            fg_color=("gray75", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray65", "gray35")
        )
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        self.auto_scroll_check = ctk.CTkCheckBox(
            self.toolbar,
            text="自动滚动",
            variable=self.auto_scroll_var,
            font=ctk.CTkFont(family='Microsoft YaHei', size=13)
        )

        # 日志文本框
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            font=("Consolas", 13),
            state="disabled",
            corner_radius=10,
            fg_color=("gray97", "#383838"),
            border_width=1,
            border_color=("gray70", "gray40")
        )

        # 配置网格权重
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

    def _setup_layout(self):
        """设置布局"""
        # 工具栏
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        self.clear_btn.pack(side="left", padx=(0, 10))
        self.save_btn.pack(side="left", padx=(0, 10))
        self.auto_scroll_check.pack(side="left")

        # 日志文本框
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    def append_log(self, message: str):
        """
        添加日志消息
        
        Args:
            message: 日志消息
        """
        if not self.is_open():
            return
        
        # 添加日志
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")
        
        # 自动滚动到底部
        if self.auto_scroll_var.get():
            self.log_text.see("end")
    
    def _clear_logs(self):
        """清空日志"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
    
    def _save_logs(self):
        """保存日志到文件"""
        # 获取日志内容
        log_content = self.log_text.get("1.0", "end")
        
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
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
            except Exception as e:
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
