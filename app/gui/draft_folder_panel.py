"""
草稿文件夹设置面板
在主窗口顶部显示，用于统一管理草稿文件夹路径
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.utils.draft_config_manager import get_draft_config_manager
from app.utils.draft_generator import DraftGenerator
from app.utils.logger import get_logger


class DraftFolderPanel:
    """草稿文件夹设置面板"""
    
    def __init__(self, parent, log_callback=None):
        """
        初始化草稿文件夹设置面板
        
        Args:
            parent: 父组件
            log_callback: 日志回调函数
        """
        self.parent = parent
        self.log_callback = log_callback
        self.logger = get_logger(__name__)
        
        # 获取配置管理器
        self.config_manager = get_draft_config_manager()
        
        # 创建草稿生成器用于自动检测
        self.draft_generator = DraftGenerator()
        
        # 创建UI
        self._create_widgets()
        self._setup_layout()
        
        # 加载当前配置
        self._load_current_config()
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="草稿文件夹设置", padding="10")
        
        # 路径设置行
        self.path_frame = ttk.Frame(self.frame)
        
        self.path_label = ttk.Label(self.path_frame, text="剪映草稿文件夹:")
        self.path_var = tk.StringVar(value="未设置")
        self.path_entry = ttk.Entry(
            self.path_frame,
            textvariable=self.path_var,
            state="readonly",
            width=60
        )
        self.select_btn = ttk.Button(
            self.path_frame,
            text="选择文件夹...",
            command=self._select_folder
        )
        self.auto_detect_btn = ttk.Button(
            self.path_frame,
            text="自动检测",
            command=self._auto_detect_folder
        )
        
        # 传输选项行
        self.option_frame = ttk.Frame(self.frame)
        
        self.transfer_var = tk.BooleanVar(value=False)
        self.transfer_check = ttk.Checkbutton(
            self.option_frame,
            text="传输草稿到指定文件夹（勾选后草稿将保存在上方指定的文件夹中，素材保存在 CozeJianYingAssistantAssets 文件夹）",
            variable=self.transfer_var,
            command=self._on_transfer_changed
        )
        
        # 说明标签
        self.info_label = ttk.Label(
            self.frame,
            text="• 勾选：草稿直接保存在剪映文件夹，素材存储在 CozeJianYingAssistantAssets 文件夹\n"
                 "• 不勾选：草稿和素材保存在本地数据目录（%LOCALAPPDATA%\\coze2jianying_data）",
            foreground="blue",
            justify=tk.LEFT,
            font=("Arial", 9)
        )
    
    def _setup_layout(self):
        """设置布局"""
        # 主框架填充
        self.frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 路径设置行
        self.path_frame.pack(fill=tk.X, pady=(0, 5))
        self.path_label.pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.select_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_detect_btn.pack(side=tk.LEFT)
        
        # 传输选项行
        self.option_frame.pack(fill=tk.X, pady=(0, 5))
        self.transfer_check.pack(side=tk.LEFT)
        
        # 说明标签
        self.info_label.pack(fill=tk.X, pady=(5, 0))
    
    def _load_current_config(self):
        """加载当前配置"""
        # 加载路径
        if self.config_manager.draft_folder_path:
            self.path_var.set(self.config_manager.draft_folder_path)
        
        # 加载传输选项
        self.transfer_var.set(self.config_manager.transfer_to_draft_folder)
    
    def _select_folder(self):
        """选择文件夹"""
        # 设置初始目录
        initial_dir = self.config_manager.draft_folder_path
        if not initial_dir:
            initial_dir = os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="选择剪映草稿文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            self._set_folder_path(folder)
    
    def _auto_detect_folder(self):
        """自动检测剪映草稿文件夹"""
        self.logger.info("尝试自动检测剪映草稿文件夹...")
        
        detected_path = self.draft_generator.detect_default_draft_folder()
        
        if detected_path:
            self._set_folder_path(detected_path)
            messagebox.showinfo("检测成功", f"已检测到剪映草稿文件夹:\n{detected_path}")
        else:
            self.logger.warning("未能检测到剪映草稿文件夹")
            messagebox.showwarning(
                "检测失败",
                "未能自动检测到剪映草稿文件夹。\n请手动选择或确认剪映专业版已安装。"
            )
    
    def _set_folder_path(self, path: str):
        """设置文件夹路径"""
        self.path_var.set(path)
        self.config_manager.draft_folder_path = path
        self.logger.info(f"草稿文件夹路径已设置: {path}")
        
        if self.log_callback:
            self.log_callback(f"草稿文件夹路径已设置: {path}")
    
    def _on_transfer_changed(self):
        """传输选项改变事件"""
        value = self.transfer_var.get()
        self.config_manager.transfer_to_draft_folder = value
        
        if value:
            # 勾选时，验证路径是否有效
            is_valid, error_msg = self.config_manager.validate_draft_folder_path()
            if not is_valid:
                messagebox.showwarning(
                    "警告",
                    f"草稿文件夹路径无效：{error_msg}\n\n请先设置有效的文件夹路径。"
                )
                # 取消勾选
                self.transfer_var.set(False)
                self.config_manager.transfer_to_draft_folder = False
                return
            
            self.logger.info(f"已启用传输到草稿文件夹: {self.config_manager.draft_folder_path}")
            if self.log_callback:
                self.log_callback(f"已启用传输到草稿文件夹: {self.config_manager.draft_folder_path}")
        else:
            self.logger.info("已禁用传输到草稿文件夹，将使用本地数据目录")
            if self.log_callback:
                self.log_callback("已禁用传输到草稿文件夹，将使用本地数据目录")
    
    def get_frame(self):
        """获取面板框架"""
        return self.frame
