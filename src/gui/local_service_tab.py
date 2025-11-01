"""
本地服务标签页模块

包含FastAPI服务管理和草稿文件夹配置功能
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os
import threading
import time

from gui.base_tab import BaseTab
from utils.draft_generator import DraftGenerator
from utils.logger import get_logger


class LocalServiceTab(BaseTab):
    """本地服务标签页
    
    包含FastAPI服务生命周期管理和草稿文件夹配置
    """
    
    def __init__(self, parent: ttk.Notebook, log_callback=None):
        """
        初始化本地服务标签页
        
        Args:
            parent: 父Notebook组件
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback
        
        # 初始化草稿生成器（用于检测文件夹）
        self.draft_generator = DraftGenerator()
        
        # 输出文件夹路径
        self.output_folder = None
        
        # FastAPI服务相关
        self.service_thread = None
        self.service_running = False
        self.service_port = 8000
        
        # 调用父类初始化
        super().__init__(parent, "本地服务")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 草稿文件夹选择区域
        self.folder_frame = ttk.LabelFrame(self.frame, text="草稿文件夹设置", padding="5")
        
        self.folder_label = ttk.Label(self.folder_frame, text="剪映草稿文件夹:")
        self.folder_var = tk.StringVar(value="未选择（将使用默认路径）")
        self.folder_entry = ttk.Entry(
            self.folder_frame, 
            textvariable=self.folder_var, 
            state="readonly", 
            width=50
        )
        self.folder_btn = ttk.Button(
            self.folder_frame,
            text="选择文件夹...",
            command=self._select_output_folder
        )
        self.auto_detect_btn = ttk.Button(
            self.folder_frame,
            text="自动检测",
            command=self._auto_detect_folder
        )
        
        # FastAPI服务管理区域
        self.service_frame = ttk.LabelFrame(self.frame, text="FastAPI 服务管理", padding="10")
        
        # 服务配置
        self.config_frame = ttk.Frame(self.service_frame)
        self.port_label = ttk.Label(self.config_frame, text="端口:")
        self.port_var = tk.StringVar(value="8000")
        self.port_entry = ttk.Entry(self.config_frame, textvariable=self.port_var, width=10)
        
        # 服务状态显示
        self.status_frame = ttk.Frame(self.service_frame)
        self.service_status_label = ttk.Label(
            self.status_frame, 
            text="服务状态: 未启动",
            font=("Arial", 10, "bold")
        )
        self.service_status_indicator = tk.Canvas(
            self.status_frame, 
            width=20, 
            height=20,
            highlightthickness=0
        )
        self._update_status_indicator(False)
        
        # 服务控制按钮
        self.control_frame = ttk.Frame(self.service_frame)
        self.start_service_btn = ttk.Button(
            self.control_frame,
            text="启动服务",
            command=self._start_service
        )
        self.stop_service_btn = ttk.Button(
            self.control_frame,
            text="停止服务",
            command=self._stop_service,
            state=tk.DISABLED
        )
        
        # 服务信息显示
        self.info_frame = ttk.LabelFrame(self.service_frame, text="服务信息", padding="5")
        self.info_text = tk.Text(
            self.info_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
    
    def _setup_layout(self):
        """设置布局"""
        # 草稿文件夹选择区域
        self.folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folder_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_btn.grid(row=0, column=2, padx=(0, 5))
        self.auto_detect_btn.grid(row=0, column=3)
        self.folder_frame.columnconfigure(1, weight=1)
        
        # FastAPI服务管理区域
        self.service_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 服务配置
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        self.port_label.pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry.pack(side=tk.LEFT)
        
        # 服务状态
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        self.service_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.service_status_label.pack(side=tk.LEFT)
        
        # 服务控制按钮
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_service_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_service_btn.pack(side=tk.LEFT)
        
        # 服务信息
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部状态栏
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
    
    def _select_output_folder(self):
        """选择输出文件夹"""
        # 设置初始目录
        initial_dir = self.output_folder if self.output_folder else os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="选择剪映草稿文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            self.output_folder = folder
            self.folder_var.set(folder)
            self.logger.info(f"已选择输出文件夹: {folder}")
            self.status_var.set(f"输出文件夹: {folder}")
    
    def _auto_detect_folder(self):
        """自动检测剪映草稿文件夹"""
        self.logger.info("尝试自动检测剪映草稿文件夹...")
        
        detected_path = self.draft_generator.detect_default_draft_folder()
        
        if detected_path:
            self.output_folder = detected_path
            self.folder_var.set(detected_path)
            self.logger.info(f"检测到剪映草稿文件夹: {detected_path}")
            self.status_var.set(f"已检测到: {detected_path}")
            messagebox.showinfo("检测成功", f"已检测到剪映草稿文件夹:\n{detected_path}")
        else:
            self.logger.warning("未能检测到剪映草稿文件夹")
            messagebox.showwarning(
                "检测失败",
                "未能自动检测到剪映草稿文件夹。\n请手动选择或确认剪映专业版已安装。"
            )
    
    def _update_status_indicator(self, running: bool):
        """更新服务状态指示器
        
        Args:
            running: 服务是否运行中
        """
        self.service_status_indicator.delete("all")
        color = "green" if running else "red"
        self.service_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)
    
    def _append_to_info(self, message: str):
        """添加信息到服务信息文本框"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _start_service(self):
        """启动FastAPI服务"""
        if self.service_running:
            messagebox.showwarning("警告", "服务已在运行中！")
            return
        
        try:
            port = int(self.port_var.get())
            if not (1024 <= port <= 65535):
                raise ValueError("端口必须在 1024-65535 之间")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的端口号: {e}")
            return
        
        self.service_port = port
        self.logger.info(f"准备启动FastAPI服务，端口: {port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 正在启动服务...")
        
        # 在后台线程中启动服务
        self.service_thread = threading.Thread(
            target=self._run_service,
            args=(port,),
            daemon=True
        )
        self.service_thread.start()
        
        # 更新UI状态
        self.service_running = True
        self._update_status_indicator(True)
        self.service_status_label.config(text=f"服务状态: 运行中 (端口 {port})")
        self.start_service_btn.config(state=tk.DISABLED)
        self.stop_service_btn.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.DISABLED)
        self.status_var.set(f"服务运行中 - http://localhost:{port}")
        
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务已启动")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 访问地址: http://localhost:{port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] API文档: http://localhost:{port}/docs")
    
    def _stop_service(self):
        """停止FastAPI服务"""
        if not self.service_running:
            messagebox.showwarning("警告", "服务未运行！")
            return
        
        self.logger.info("停止FastAPI服务")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 正在停止服务...")
        
        # 更新状态（实际的停止逻辑在占位符服务中处理）
        self.service_running = False
        self._update_status_indicator(False)
        self.service_status_label.config(text="服务状态: 未启动")
        self.start_service_btn.config(state=tk.NORMAL)
        self.stop_service_btn.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.status_var.set("就绪")
        
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务已停止")
    
    def _run_service(self, port: int):
        """运行FastAPI服务（后台线程）
        
        Args:
            port: 服务端口
        """
        try:
            # 这是一个占位符实现
            # 实际的FastAPI服务将在后续实现
            self.logger.info("FastAPI服务线程已启动（占位符实现）")
            
            # 模拟服务运行
            while self.service_running:
                time.sleep(1)
            
            self.logger.info("FastAPI服务线程已停止")
        except Exception as e:
            self.logger.error(f"FastAPI服务出错: {e}", exc_info=True)
            # 在主线程中更新UI
            self.frame.after(0, self._on_service_error, e)
    
    def _on_service_error(self, error):
        """服务错误回调"""
        self.service_running = False
        self._update_status_indicator(False)
        self.service_status_label.config(text="服务状态: 错误")
        self.start_service_btn.config(state=tk.NORMAL)
        self.stop_service_btn.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.status_var.set("服务错误")
        
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务错误: {error}")
        messagebox.showerror("服务错误", f"FastAPI服务出错:\n{error}")
    
    def cleanup(self):
        """清理标签页资源"""
        # 停止服务
        if self.service_running:
            self.service_running = False
            if self.service_thread and self.service_thread.is_alive():
                self.service_thread.join(timeout=2)
        
        super().cleanup()
        # 清理标签页特定的资源
        self.output_folder = None
        self.draft_generator = None
        self.service_thread = None
