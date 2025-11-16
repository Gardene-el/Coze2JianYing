"""
全局文件夹选择器

在主窗口中提供统一的草稿文件夹设置界面
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable
from app.utils.storage_settings import get_storage_settings
from app.utils.logger import get_logger


class GlobalFolderSelector:
    """
    全局文件夹选择器
    
    在主窗口中显示，供所有标签页共享使用
    """
    
    def __init__(self, parent: tk.Widget, on_settings_changed: Optional[Callable] = None):
        """
        初始化全局文件夹选择器
        
        Args:
            parent: 父组件
            on_settings_changed: 设置改变时的回调函数
        """
        self.parent = parent
        self.logger = get_logger(__name__)
        self.storage_settings = get_storage_settings()
        self.on_settings_changed = on_settings_changed
        
        # 创建主框架
        self.frame = ttk.LabelFrame(parent, text="全局草稿存储设置", padding="10")
        
        # 创建UI组件
        self._create_widgets()
        self._setup_layout()
        
        # 初始化状态
        self._update_ui_state()
    
    def _create_widgets(self):
        """创建UI组件"""
        # 传输选项勾选框
        self.enable_transfer_var = tk.BooleanVar(value=self.storage_settings.enable_transfer)
        self.enable_transfer_check = ttk.Checkbutton(
            self.frame,
            text="传输草稿到指定文件夹",
            variable=self.enable_transfer_var,
            command=self._on_transfer_changed
        )
        
        # 文件夹路径显示
        self.folder_label = ttk.Label(self.frame, text="剪映草稿文件夹:")
        self.folder_var = tk.StringVar(
            value=self.storage_settings.target_folder or "未选择（将使用本地数据目录）"
        )
        self.folder_entry = ttk.Entry(
            self.frame,
            textvariable=self.folder_var,
            state="readonly",
            width=60
        )
        
        # 选择文件夹按钮
        self.select_btn = ttk.Button(
            self.frame,
            text="选择文件夹...",
            command=self._select_folder
        )
        
        # 自动检测按钮
        self.detect_btn = ttk.Button(
            self.frame,
            text="自动检测",
            command=self._auto_detect
        )
        
        # 状态标签
        self.status_label = ttk.Label(
            self.frame,
            text="",
            foreground="blue",
            font=("Arial", 9)
        )
    
    def _setup_layout(self):
        """布局UI组件"""
        # 第一行：勾选框
        self.enable_transfer_check.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # 第二行：文件夹选择
        self.folder_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.select_btn.grid(row=1, column=2, padx=(0, 5))
        self.detect_btn.grid(row=1, column=3)
        
        # 第三行：状态
        self.status_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 配置列权重
        self.frame.columnconfigure(1, weight=1)
    
    def _update_ui_state(self):
        """更新UI状态（启用/禁用控件）"""
        enabled = self.enable_transfer_var.get()
        state = "normal" if enabled else "disabled"
        
        self.select_btn.config(state=state)
        self.detect_btn.config(state=state)
        
        # 更新状态文本
        if enabled:
            if self.storage_settings.target_folder:
                self.status_label.config(
                    text=f"✓ 草稿将保存到: {self.storage_settings.target_folder}",
                    foreground="green"
                )
            else:
                self.status_label.config(
                    text="⚠ 请选择或检测剪映草稿文件夹",
                    foreground="orange"
                )
        else:
            from app.config import get_config
            config = get_config()
            self.status_label.config(
                text=f"ℹ 草稿将保存到本地数据目录: {config.drafts_dir}",
                foreground="blue"
            )
    
    def _on_transfer_changed(self):
        """传输选项改变回调"""
        enabled = self.enable_transfer_var.get()
        self.storage_settings.enable_transfer = enabled
        
        self.logger.info(f"全局设置: 传输草稿 = {enabled}")
        self._update_ui_state()
        
        # 通知回调
        if self.on_settings_changed:
            self.on_settings_changed()
    
    def _select_folder(self):
        """选择文件夹"""
        initial_dir = self.storage_settings.target_folder or os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="选择剪映草稿文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            self.storage_settings.target_folder = folder
            self.folder_var.set(folder)
            self.logger.info(f"全局设置: 文件夹 = {folder}")
            self._update_ui_state()
            
            # 通知回调
            if self.on_settings_changed:
                self.on_settings_changed()
    
    def _auto_detect(self):
        """自动检测剪映草稿文件夹"""
        self.logger.info("自动检测剪映草稿文件夹...")
        
        detected_path = self.storage_settings.detect_default_folder()
        
        if detected_path:
            self.storage_settings.target_folder = detected_path
            self.folder_var.set(detected_path)
            self.logger.info(f"检测到剪映草稿文件夹: {detected_path}")
            self._update_ui_state()
            messagebox.showinfo("检测成功", f"已检测到剪映草稿文件夹:\n{detected_path}")
            
            # 通知回调
            if self.on_settings_changed:
                self.on_settings_changed()
        else:
            self.logger.warning("未能检测到剪映草稿文件夹")
            messagebox.showwarning(
                "检测失败",
                "未能自动检测到剪映草稿文件夹。\n\n请手动选择或确认剪映专业版已安装。"
            )
    
    def pack(self, **kwargs):
        """打包布局"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局"""
        self.frame.grid(**kwargs)
