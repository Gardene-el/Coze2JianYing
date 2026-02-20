"""
主窗口模块 (CustomTkinter Refactor)
"""

import os
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox, filedialog
from PIL import Image

from app.frontend.gui.pages.draft_generator_page import DraftGeneratorPage
from app.frontend.gui.pages.cloud_service_page import CloudServicePage
from app.frontend.gui.pages.script_executor_page import ScriptExecutorPage
from app.frontend.gui.pages.settings_page import SettingsPage
from app.frontend.gui.log_window import LogWindow
from app.backend.utils.logger import get_logger, set_gui_log_callback
from app.backend.core.settings_manager import get_settings_manager

class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        self.logger = get_logger(__name__)
        self.settings = get_settings_manager()
        
        # 配置窗口
        self.title("Coze剪映草稿生成器")
        self.geometry("1100x700")
        
        # 设置主题
        ctk.set_appearance_mode(self.settings.get("theme_mode", "System"))
        ctk.set_default_color_theme("blue")

        # 外部日志窗口
        self.log_window = None
        
        # 设置GUI日志回调
        set_gui_log_callback(self._on_log_message)

        # 布局配置
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建侧边栏
        self._create_sidebar()
        
        # 创建内容区域
        self._create_content_area()
        
        # 创建日志区域
        self._create_log_area()

        # 初始化页面
        self.pages = {}
        self._init_pages()

        # 默认显示首页
        self.select_frame_by_name("draft_generator")

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_sidebar(self):
        """创建侧边栏"""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Coze2JianYing", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 导航按钮
        self.btn_draft = self._create_nav_button("草稿生成", "draft_generator", 1)
        self.btn_cloud = self._create_nav_button("云端服务", "cloud_service", 2)
        self.btn_script = self._create_nav_button("脚本执行", "script_executor", 3)
        self.btn_settings = self._create_nav_button("系统设置", "settings", 4)

        # 底部按钮
        self.btn_log_window = ctk.CTkButton(
            self.sidebar_frame,
            text="独立日志窗口",
            command=self._show_log_window,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE")
        )
        self.btn_log_window.grid(row=6, column=0, padx=20, pady=10)

        # 外观模式
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="主题模式:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self._change_appearance_mode
        )
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        # 设置初始值
        self.appearance_mode_optionemenu.set(self.settings.get("theme_mode", "System"))

    def _create_nav_button(self, text, name, row):
        """创建导航按钮"""
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            command=lambda n=name: self.select_frame_by_name(n),
            height=40,
            font=ctk.CTkFont(size=14)
        )
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        return btn

    def _create_content_area(self):
        """创建内容显示区域"""
        # 这里不直接创建Frame，而是作为容器放置各个Page
        pass

    def _create_log_area(self):
        """创建底部日志区域"""
        self.log_frame = ctk.CTkFrame(self, height=150, corner_radius=0)
        self.log_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(self.log_frame, height=30, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(toolbar, text="运行日志", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar, text="清空", width=60, height=24, 
            command=self._clear_logs
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            toolbar, text="保存", width=60, height=24, 
            command=self._save_logs
        ).pack(side="right", padx=5)

        # 日志文本框
        self.log_textbox = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12))
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.log_textbox.configure(state="disabled")

    def _init_pages(self):
        """初始化所有页面"""
        self.pages["draft_generator"] = DraftGeneratorPage(self)
        self.pages["cloud_service"] = CloudServicePage(self)
        self.pages["script_executor"] = ScriptExecutorPage(self)
        self.pages["settings"] = SettingsPage(self)

    def select_frame_by_name(self, name):
        """切换页面"""
        # 显示选中的页面
        for page_name, page in self.pages.items():
            if page_name == name:
                page.grid(row=0, column=1, sticky="nsew")
                # 如果页面有 update_settings 方法，调用它以刷新设置
                if hasattr(page, "update_settings"):
                    page.update_settings()
            else:
                page.grid_forget()

    def _change_appearance_mode(self, new_appearance_mode):
        """切换外观模式"""
        ctk.set_appearance_mode(new_appearance_mode)
        self.settings.set("theme_mode", new_appearance_mode)

    def _on_log_message(self, message: str):
        """处理日志消息"""
        def update_log():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
            
            if self.log_window and self.log_window.is_open():
                self.log_window.append_log(message)

        try:
            self.after(0, update_log)
        except:
            pass

    def _clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def _save_logs(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt")],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.log_textbox.get("1.0", "end"))
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")

    def _show_log_window(self):
        if self.log_window is None or not self.log_window.is_open():
            self.log_window = LogWindow(self)
        else:
            self.log_window.focus()

    def _on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            # 清理资源
            for page in self.pages.values():
                if hasattr(page, "cleanup"):
                    page.cleanup()
            self.destroy()

    def run(self):
        self.mainloop()
