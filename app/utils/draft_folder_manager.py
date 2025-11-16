"""
草稿文件夹管理模块

提供统一的草稿文件夹路径管理功能，包括：
1. 草稿文件夹路径的选择和存储
2. 自动检测剪映草稿文件夹
3. 管理是否传输草稿到指定文件夹的选项
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable
from app.utils.logger import get_logger


class DraftFolderManager:
    """草稿文件夹管理器
    
    统一管理草稿文件夹路径的选择、存储和配置
    """
    
    # 默认剪映草稿路径
    DEFAULT_DRAFT_PATHS = [
        r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    
    def __init__(self):
        """初始化草稿文件夹管理器"""
        self.logger = get_logger(__name__)
        self._folder_path: Optional[str] = None
        self._enable_transfer: bool = True  # 默认启用传输到草稿文件夹
    
    @property
    def folder_path(self) -> Optional[str]:
        """获取草稿文件夹路径"""
        return self._folder_path
    
    @folder_path.setter
    def folder_path(self, path: Optional[str]):
        """设置草稿文件夹路径"""
        self._folder_path = path
    
    @property
    def enable_transfer(self) -> bool:
        """获取是否启用传输到草稿文件夹"""
        return self._enable_transfer
    
    @enable_transfer.setter
    def enable_transfer(self, value: bool):
        """设置是否启用传输到草稿文件夹"""
        self._enable_transfer = value
    
    def detect_default_folder(self) -> Optional[str]:
        """
        自动检测剪映草稿文件夹
        
        Returns:
            检测到的文件夹路径，如果未检测到则返回None
        """
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        for path_template in self.DEFAULT_DRAFT_PATHS:
            path = path_template.format(username=username)
            if os.path.exists(path) and os.path.isdir(path):
                self.logger.info(f"检测到剪映草稿文件夹: {path}")
                return path
        
        self.logger.warning("未能检测到剪映草稿文件夹")
        return None
    
    def get_output_folder(self, fallback_folder: Optional[str] = None) -> Optional[str]:
        """
        获取最终的输出文件夹路径
        
        Args:
            fallback_folder: 备用文件夹路径（当未启用传输时使用）
            
        Returns:
            输出文件夹路径，如果未配置则返回None
        """
        if not self._enable_transfer:
            # 未启用传输，使用备用文件夹
            return fallback_folder
        
        if self._folder_path:
            # 已配置文件夹路径，直接返回
            return self._folder_path
        
        # 尝试自动检测
        detected = self.detect_default_folder()
        if detected:
            self._folder_path = detected
            return detected
        
        return None
    
    def validate_folder(self, folder_path: str) -> tuple[bool, str]:
        """
        验证文件夹路径是否有效
        
        Args:
            folder_path: 要验证的文件夹路径
            
        Returns:
            (是否有效, 错误消息)
        """
        if not folder_path:
            return False, "未指定文件夹路径"
        
        if not os.path.exists(folder_path):
            return False, f"指定的文件夹不存在:\n{folder_path}"
        
        if not os.path.isdir(folder_path):
            return False, f"指定的路径不是文件夹:\n{folder_path}"
        
        return True, ""


class DraftFolderWidget:
    """草稿文件夹选择UI组件
    
    提供可复用的草稿文件夹选择界面，包括：
    - 文件夹路径显示
    - 选择文件夹按钮
    - 自动检测按钮
    - 是否传输到草稿文件夹的勾选框
    """
    
    def __init__(
        self,
        parent: ttk.Frame,
        manager: DraftFolderManager,
        on_folder_changed: Optional[Callable[[str], None]] = None,
        on_transfer_changed: Optional[Callable[[bool], None]] = None
    ):
        """
        初始化草稿文件夹UI组件
        
        Args:
            parent: 父容器
            manager: 草稿文件夹管理器实例
            on_folder_changed: 文件夹路径改变时的回调函数
            on_transfer_changed: 传输选项改变时的回调函数
        """
        self.parent = parent
        self.manager = manager
        self.on_folder_changed = on_folder_changed
        self.on_transfer_changed = on_transfer_changed
        self.logger = get_logger(__name__)
        
        # UI变量
        self.folder_var = tk.StringVar(value="未选择（将使用默认路径）")
        self.enable_transfer_var = tk.BooleanVar(value=True)
        
        # 创建UI
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="草稿文件夹设置", padding="5")
        
        # 传输选项勾选框
        self.enable_transfer_check = ttk.Checkbutton(
            self.frame,
            text="传输草稿到指定文件夹",
            variable=self.enable_transfer_var,
            command=self._on_transfer_changed
        )
        
        # 文件夹路径行
        self.folder_label = ttk.Label(self.frame, text="剪映草稿文件夹:")
        self.folder_entry = ttk.Entry(
            self.frame,
            textvariable=self.folder_var,
            state="readonly",
            width=50
        )
        self.folder_btn = ttk.Button(
            self.frame,
            text="选择文件夹...",
            command=self._select_folder
        )
        self.auto_detect_btn = ttk.Button(
            self.frame,
            text="自动检测",
            command=self._auto_detect_folder
        )
    
    def _setup_layout(self):
        """设置布局"""
        # 传输选项勾选框 - 第一行
        self.enable_transfer_check.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 5))
        
        # 文件夹路径行 - 第二行
        self.folder_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_btn.grid(row=1, column=2, padx=(0, 5))
        self.auto_detect_btn.grid(row=1, column=3)
        
        # 配置列权重
        self.frame.columnconfigure(1, weight=1)
    
    def _select_folder(self):
        """选择文件夹"""
        # 设置初始目录
        initial_dir = self.manager.folder_path if self.manager.folder_path else os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="选择剪映草稿文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            self.manager.folder_path = folder
            self.folder_var.set(folder)
            self.logger.info(f"已选择草稿文件夹: {folder}")
            
            if self.on_folder_changed:
                self.on_folder_changed(folder)
    
    def _auto_detect_folder(self):
        """自动检测剪映草稿文件夹"""
        self.logger.info("尝试自动检测剪映草稿文件夹...")
        
        detected_path = self.manager.detect_default_folder()
        
        if detected_path:
            self.manager.folder_path = detected_path
            self.folder_var.set(detected_path)
            self.logger.info(f"检测到剪映草稿文件夹: {detected_path}")
            messagebox.showinfo("检测成功", f"已检测到剪映草稿文件夹:\n{detected_path}")
            
            if self.on_folder_changed:
                self.on_folder_changed(detected_path)
        else:
            self.logger.warning("未能检测到剪映草稿文件夹")
            messagebox.showwarning(
                "检测失败",
                "未能自动检测到剪映草稿文件夹。\n请手动选择或确认剪映专业版已安装。"
            )
    
    def _on_transfer_changed(self):
        """传输选项改变事件处理"""
        enabled = self.enable_transfer_var.get()
        self.manager.enable_transfer = enabled
        
        # 根据传输选项启用/禁用文件夹选择组件
        state = tk.NORMAL if enabled else tk.DISABLED
        self.folder_btn.config(state=state)
        self.auto_detect_btn.config(state=state)
        
        self.logger.info(f"传输草稿到文件夹: {'启用' if enabled else '禁用'}")
        
        if self.on_transfer_changed:
            self.on_transfer_changed(enabled)
    
    def grid(self, **kwargs):
        """将组件放置到网格布局中"""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """将组件放置到pack布局中"""
        self.frame.pack(**kwargs)
    
    def get_output_folder(self, fallback_folder: Optional[str] = None) -> Optional[str]:
        """
        获取输出文件夹路径（便捷方法）
        
        Args:
            fallback_folder: 备用文件夹路径
            
        Returns:
            输出文件夹路径
        """
        return self.manager.get_output_folder(fallback_folder)
