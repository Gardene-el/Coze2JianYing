"""
云端服务标签页模块

管理基于已有服务的云侧插件（FastAPI服务）
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import time
import socket
import subprocess
import sys
import queue
from pathlib import Path
import uvicorn
import atexit

from app.gui.base_tab import BaseTab
from app.utils.draft_generator import DraftGenerator
from app.utils.ngrok_manager import NgrokManager


class CloudServiceTab(BaseTab):
    """云端服务标签页
    
    管理 FastAPI 服务，用于"基于已有服务的云侧插件"模式
    Coze 通过 HTTP API 调用本服务，无需 cozepy SDK
    """

    def __init__(self, parent: ttk.Notebook, log_callback=None):
        """
        初始化云端服务标签页

        Args:
            parent: 父Notebook组件
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback

        # 初始化草稿生成器（用于检测文件夹）
        self.draft_generator = DraftGenerator()

        # 输出文件夹路径
        self.output_folder = None

        # FastAPI服务相关(使用子进程方式)
        self.service_process = None  # 子进程对象(源码环境)
        self.service_thread = None   # 服务线程(打包环境)
        self.uvicorn_server = None   # uvicorn 服务器实例(用于停止)
        self.service_running = False
        self.service_port = 8000
        self.log_queue = queue.Queue()  # 日志队列
        self.log_reader_thread = None  # 日志读取线程
        self.stop_event = threading.Event()
        
        # ngrok 隧道管理
        self.ngrok_manager = None
        self.ngrok_running = False
        self.ngrok_public_url = None
        
        # 注册清理函数,确保应用退出时停止服务
        atexit.register(self._cleanup_on_exit)

        # 调用父类初始化
        super().__init__(parent, "云端服务")
    
    def _cleanup_on_exit(self):
        """应用退出时的清理函数"""
        try:
            if self.ngrok_running and self.ngrok_manager:
                # 使用异步模式，快速退出
                self.ngrok_manager.stop_tunnel(async_mode=True)
            if self.service_running:
                self._stop_service()
        except:
            pass  # 忽略清理时的错误
    
    def __del__(self):
        """析构函数：确保在对象销毁时停止服务"""
        try:
            if self.ngrok_running and self.ngrok_manager:
                # 使用异步模式，快速退出
                self.ngrok_manager.stop_tunnel(async_mode=True)
            if self.service_running:
                self._stop_service()
        except:
            pass  # 忽略析构时的错误

    def _create_widgets(self):
        """创建UI组件"""
        # 说明文字
        self.info_label_frame = ttk.LabelFrame(self.frame, text="服务说明", padding="10")
        self.info_label = ttk.Label(
            self.info_label_frame,
            text="云端服务模式：启动 FastAPI 服务，在 Coze 平台配置\"云侧插件 - 基于已有服务\"，\nCoze 通过 HTTP API 直接调用本服务，无需 cozepy SDK 或 Coze Token。",
            justify=tk.LEFT,
            foreground="blue"
        )
        
        # 草稿文件夹选择区域
        self.folder_frame = ttk.LabelFrame(self.frame, text="草稿文件夹设置", padding="5")

        self.folder_label = ttk.Label(self.folder_frame, text="剪映草稿文件夹:")
        self.folder_var = tk.StringVar(value="未选择（将使用默认路径）")
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_var, state="readonly", width=50)
        self.folder_btn = ttk.Button(self.folder_frame, text="选择文件夹...", command=self._select_output_folder)
        self.auto_detect_btn = ttk.Button(self.folder_frame, text="自动检测", command=self._auto_detect_folder)

        # FastAPI服务管理区域
        self.service_frame = ttk.LabelFrame(self.frame, text="FastAPI 服务管理", padding="10")

        # 服务配置
        self.config_frame = ttk.Frame(self.service_frame)
        self.port_label = ttk.Label(self.config_frame, text="端口:")
        self.port_var = tk.StringVar(value="8000")
        self.port_entry = ttk.Entry(self.config_frame, textvariable=self.port_var, width=10)
        self.check_port_btn = ttk.Button(self.config_frame, text="检测端口", command=self._check_port_available)

        # 端口状态显示
        self.port_status_frame = ttk.Frame(self.service_frame)
        self.port_status_label = ttk.Label(self.port_status_frame, text="端口状态: 未检测", font=("Arial", 10))
        self.port_status_indicator = tk.Canvas(self.port_status_frame, width=20, height=20, highlightthickness=0)
        self._update_port_status_indicator("未检测")

        # 服务状态显示
        self.status_frame = ttk.Frame(self.service_frame)
        self.service_status_label = ttk.Label(self.status_frame, text="服务状态: 未启动", font=("Arial", 10, "bold"))
        self.service_status_indicator = tk.Canvas(self.status_frame, width=20, height=20, highlightthickness=0)
        self._update_status_indicator(False)

        # 服务控制按钮
        self.control_frame = ttk.Frame(self.service_frame)
        self.start_service_btn = ttk.Button(self.control_frame, text="启动服务", command=self._start_service)
        self.stop_service_btn = ttk.Button(
            self.control_frame, text="停止服务", command=self._stop_service, state=tk.DISABLED
        )

        # 服务信息显示（实时日志）
        self.info_frame = ttk.LabelFrame(self.service_frame, text="服务实时日志", padding="5")
        self.info_text = tk.Text(
            self.info_frame, 
            height=12, 
            wrap=tk.WORD, 
            font=("Consolas", 9), 
            state=tk.DISABLED,
            bg="#1e1e1e",  # 深色背景
            fg="#d4d4d4"   # 浅色文字
        )
        # 添加滚动条
        self.info_scrollbar = ttk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=self.info_scrollbar.set)
        
        # 清空日志按钮
        self.clear_log_btn = ttk.Button(self.info_frame, text="清空日志", command=self._clear_log)

        # ngrok 内网穿透管理区域
        self.ngrok_frame = ttk.LabelFrame(self.frame, text="ngrok 内网穿透", padding="10")
        
        # ngrok 说明文字
        self.ngrok_info_label = ttk.Label(
            self.ngrok_frame,
            text="💡 提示：无需注册即可使用 ngrok，Authtoken 为可选项。点击 '?' 查看详情。",
            justify=tk.LEFT,
            foreground="blue",
            font=("Arial", 9)
        )
        
        # ngrok 配置
        self.ngrok_config_frame = ttk.Frame(self.ngrok_frame)
        
        # Authtoken 输入
        self.ngrok_token_label = ttk.Label(self.ngrok_config_frame, text="Authtoken (可选):")
        self.ngrok_token_var = tk.StringVar(value="")
        self.ngrok_token_entry = ttk.Entry(self.ngrok_config_frame, textvariable=self.ngrok_token_var, show="*", width=40)
        self.ngrok_token_entry.configure(foreground="gray")  # 使用灰色表示可选
        
        self.show_ngrok_token_var = tk.BooleanVar(value=False)
        self.show_ngrok_token_btn = ttk.Checkbutton(
            self.ngrok_config_frame, 
            text="显示", 
            variable=self.show_ngrok_token_var,
            command=self._toggle_ngrok_token_visibility
        )
        
        # 添加帮助按钮
        self.ngrok_token_help_btn = ttk.Button(
            self.ngrok_config_frame,
            text="?",
            width=3,
            command=self._show_authtoken_help
        )
        
        # Region 选择
        self.ngrok_region_label = ttk.Label(self.ngrok_config_frame, text="区域:")
        self.ngrok_region_var = tk.StringVar(value="us")
        self.ngrok_region_combo = ttk.Combobox(
            self.ngrok_config_frame,
            textvariable=self.ngrok_region_var,
            values=["us", "eu", "ap", "au", "sa", "jp", "in"],
            state="readonly",
            width=10
        )
        
        # ngrok 状态显示
        self.ngrok_status_frame = ttk.Frame(self.ngrok_frame)
        self.ngrok_status_label = ttk.Label(self.ngrok_status_frame, text="ngrok 状态: 未启动", font=("Arial", 10, "bold"))
        self.ngrok_status_indicator = tk.Canvas(self.ngrok_status_frame, width=20, height=20, highlightthickness=0)
        self._update_ngrok_status_indicator(False)
        
        # ngrok 公网 URL 显示
        self.ngrok_url_frame = ttk.Frame(self.ngrok_frame)
        self.ngrok_url_label = ttk.Label(self.ngrok_url_frame, text="公网地址:")
        self.ngrok_url_var = tk.StringVar(value="未启动")
        self.ngrok_url_entry = ttk.Entry(self.ngrok_url_frame, textvariable=self.ngrok_url_var, state="readonly", width=50)
        self.copy_ngrok_url_btn = ttk.Button(self.ngrok_url_frame, text="复制", command=self._copy_ngrok_url, state=tk.DISABLED)
        
        # ngrok 控制按钮
        self.ngrok_control_frame = ttk.Frame(self.ngrok_frame)
        self.start_ngrok_btn = ttk.Button(self.ngrok_control_frame, text="启动 ngrok", command=self._start_ngrok, state=tk.DISABLED)
        self.stop_ngrok_btn = ttk.Button(self.ngrok_control_frame, text="停止 ngrok", command=self._stop_ngrok, state=tk.DISABLED)
        
        # ngrok 日志显示
        self.ngrok_log_frame = ttk.LabelFrame(self.ngrok_frame, text="ngrok 日志", padding="5")
        self.ngrok_log_text = tk.Text(
            self.ngrok_log_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.ngrok_log_scrollbar = ttk.Scrollbar(self.ngrok_log_frame, orient=tk.VERTICAL, command=self.ngrok_log_text.yview)
        self.ngrok_log_text.config(yscrollcommand=self.ngrok_log_scrollbar.set)
        self.clear_ngrok_log_btn = ttk.Button(self.ngrok_log_frame, text="清空日志", command=self._clear_ngrok_log)

        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)

        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)

    def _setup_layout(self):
        """设置布局"""
        # 说明文字
        self.info_label_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.info_label.pack(fill=tk.X)
        
        # 草稿文件夹选择区域
        self.folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folder_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_btn.grid(row=0, column=2, padx=(0, 5))
        self.auto_detect_btn.grid(row=0, column=3)
        self.folder_frame.columnconfigure(1, weight=1)

        # FastAPI服务管理区域
        self.service_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 服务配置
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        self.port_label.pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.check_port_btn.pack(side=tk.LEFT)

        # 端口状态
        self.port_status_frame.pack(fill=tk.X, pady=(0, 10))
        self.port_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.port_status_label.pack(side=tk.LEFT)

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
        
        # 日志显示区域布局
        log_content_frame = ttk.Frame(self.info_frame)
        log_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, in_=log_content_frame)
        self.info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=log_content_frame)
        
        self.clear_log_btn.pack(side=tk.RIGHT)

        # ngrok 内网穿透区域
        self.ngrok_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ngrok 说明文字
        self.ngrok_info_label.pack(fill=tk.X, pady=(0, 10))
        
        # ngrok 配置
        self.ngrok_config_frame.pack(fill=tk.X, pady=(0, 10))
        self.ngrok_token_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ngrok_token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.show_ngrok_token_btn.grid(row=0, column=2, padx=(0, 5))
        self.ngrok_token_help_btn.grid(row=0, column=3, padx=(0, 5))
        self.ngrok_region_label.grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.ngrok_region_combo.grid(row=0, column=5)
        self.ngrok_config_frame.columnconfigure(1, weight=1)
        
        # ngrok 状态
        self.ngrok_status_frame.pack(fill=tk.X, pady=(0, 10))
        self.ngrok_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.ngrok_status_label.pack(side=tk.LEFT)
        
        # ngrok URL
        self.ngrok_url_frame.pack(fill=tk.X, pady=(0, 10))
        self.ngrok_url_label.pack(side=tk.LEFT, padx=(0, 5))
        self.ngrok_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.copy_ngrok_url_btn.pack(side=tk.LEFT)
        
        # ngrok 控制按钮
        self.ngrok_control_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_ngrok_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_ngrok_btn.pack(side=tk.LEFT)
        
        # ngrok 日志
        self.ngrok_log_frame.pack(fill=tk.BOTH, expand=True)
        ngrok_log_content_frame = ttk.Frame(self.ngrok_log_frame)
        ngrok_log_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.ngrok_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, in_=ngrok_log_content_frame)
        self.ngrok_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=ngrok_log_content_frame)
        self.clear_ngrok_log_btn.pack(side=tk.RIGHT)

        # 底部状态栏
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))

    def _select_output_folder(self):
        """选择输出文件夹"""
        # 设置初始目录
        initial_dir = self.output_folder if self.output_folder else os.path.expanduser("~")

        folder = filedialog.askdirectory(title="选择剪映草稿文件夹", initialdir=initial_dir)

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
            messagebox.showwarning("检测失败", "未能自动检测到剪映草稿文件夹。\n请手动选择或确认剪映专业版已安装。")

    def _check_port_available(self):
        """检测端口是否可用"""
        try:
            port = int(self.port_var.get())
            if not (1024 <= port <= 65535):
                raise ValueError("端口必须在 1024-65535 之间")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的端口号: {e}")
            return

        # 检测端口是否可用
        is_available = self._is_port_available(port)

        if is_available:
            self.logger.info(f"端口 {port} 可用")
            self.port_status_label.config(text=f"端口状态: 端口 {port} 可用")
            self._update_port_status_indicator("可用")
            self.status_var.set(f"端口 {port} 可用")
        else:
            self.logger.warning(f"端口 {port} 已被占用")
            self.port_status_label.config(text=f"端口状态: 端口 {port} 已被占用")
            self._update_port_status_indicator("被占用")
            self.status_var.set(f"端口 {port} 被占用")

    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("localhost", port))
                return True
        except OSError:
            return False

    def _update_port_status_indicator(self, status: str):
        """更新端口状态指示器"""
        self.port_status_indicator.delete("all")
        if status == "可用":
            color = "green"
        elif status == "被占用":
            color = "red"
        else:  # 未检测
            color = "gray"
        self.port_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _update_status_indicator(self, running: bool):
        """更新服务状态指示器"""
        self.service_status_indicator.delete("all")
        color = "green" if running else "red"
        self.service_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _append_to_info(self, message: str, tag: str = None):
        """添加信息到服务信息文本框"""
        self.info_text.config(state=tk.NORMAL)
        if tag:
            self.info_text.insert(tk.END, message + "\n", tag)
        else:
            self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _clear_log(self):
        """清空日志显示"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.logger.info("日志已清空")

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

        # 检查端口是否可用
        if not self._is_port_available(port):
            self.port_status_label.config(text=f"端口状态: 端口 {port} 已被占用")
            self._update_port_status_indicator("被占用")
            messagebox.showerror(
                "端口被占用", f"端口 {port} 已被其他程序占用。\n\n请选择其他端口或停止占用该端口的程序。"
            )
            self.logger.warning(f"无法启动服务: 端口 {port} 已被占用")
            return

        self.service_port = port
        self.logger.info(f"准备启动FastAPI服务，端口: {port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 正在启动服务...")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 使用子进程模式，可完整捕获日志")

        # 启动服务子进程
        try:
            self._start_service_process(port)
        except Exception as e:
            self.logger.error(f"启动服务失败: {e}", exc_info=True)
            messagebox.showerror("启动失败", f"无法启动服务:\n{e}")
            return

        # 更新UI状态
        self.service_running = True
        self._update_status_indicator(True)
        self.service_status_label.config(text=f"服务状态: 运行中 (端口 {port})")
        self.port_status_label.config(text=f"端口状态: 端口 {port} 使用中")
        self._update_port_status_indicator("被占用")
        self.start_service_btn.config(state=tk.DISABLED)
        self.stop_service_btn.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.DISABLED)
        self.check_port_btn.config(state=tk.DISABLED)
        self.status_var.set(f"服务运行中 - http://localhost:{port}")

        if self.service_process:
            self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务进程已启动 (PID: {self.service_process.pid})")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 访问地址: http://localhost:{port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] API文档: http://localhost:{port}/docs")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] " + "-" * 60)
        
        # 启动日志处理
        self._start_log_processing()
        
        # 启用 ngrok 按钮
        self.start_ngrok_btn.config(state=tk.NORMAL)

    def _stop_service(self):
        """停止FastAPI服务"""
        if not self.service_running:
            messagebox.showwarning("警告", "服务未运行！")
            return

        self.logger.info("停止FastAPI服务")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 正在停止服务...")

        # 设置停止标志
        self.service_running = False
        self.stop_event.set()
        
        is_frozen = getattr(sys, 'frozen', False)
        
        # 停止服务
        try:
            if is_frozen and self.uvicorn_server:
                # 打包环境：停止 uvicorn 服务器（线程模式）
                self.uvicorn_server.should_exit = True
                self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 正在停止嵌入式服务...")
                
                # 等待线程结束
                if self.service_thread and self.service_thread.is_alive():
                    self.service_thread.join(timeout=5)
                
                self.uvicorn_server = None
                self.service_thread = None
                self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 嵌入式服务已停止")
                
            elif self.service_process:
                # 源码环境：Popen 对象
                self.service_process.terminate()
                try:
                    self.service_process.wait(timeout=5)
                    self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务进程已正常终止")
                except subprocess.TimeoutExpired:
                    self.service_process.kill()
                    self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务进程已强制终止")
                
                self.service_process = None
                
        except Exception as e:
            self.logger.warning(f"停止服务时出错: {e}")
            self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 停止服务时出错: {e}")

        # 停止日志读取线程（仅源码环境）
        if self.log_reader_thread and self.log_reader_thread.is_alive():
            self.log_reader_thread.join(timeout=2)
            self.log_reader_thread = None

        # 更新UI状态
        self._update_status_indicator(False)
        self.service_status_label.config(text="服务状态: 未启动")
        self.port_status_label.config(text="端口状态: 未检测")
        self._update_port_status_indicator("未检测")
        self.start_service_btn.config(state=tk.NORMAL)
        self.stop_service_btn.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.check_port_btn.config(state=tk.NORMAL)
        self.status_var.set("就绪")

        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务已停止")
        
        # 如果 ngrok 正在运行，也停止它
        if self.ngrok_running:
            self._stop_ngrok()
        
        # 禁用 ngrok 按钮
        self.start_ngrok_btn.config(state=tk.DISABLED)

    def _start_service_process(self, port: int):
        """启动FastAPI服务（根据运行环境选择方式）"""
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # 打包环境：使用多进程直接运行 FastAPI
            self._start_embedded_service(port)
        else:
            # 源码环境：使用 uvicorn 命令行方式启动
            self._start_uvicorn_service(port)
    
    def _start_embedded_service(self, port: int):
        """在打包环境中启动嵌入式 FastAPI 服务（线程模式）"""
        from app.api_main import app
        
        def run_server_thread():
            """在后台线程中运行服务器"""
            try:
                config = uvicorn.Config(
                    app=app,
                    host="127.0.0.1",
                    port=port,
                    log_level="error",
                    access_log=False,
                    log_config=None
                )
                server = uvicorn.Server(config)
                self.uvicorn_server = server
                server.run()
            except OSError as e:
                if e.errno == 10048:
                    error_msg = f"端口 {port} 已被占用，请选择其他端口"
                else:
                    error_msg = f"网络错误: {e}"
                self.logger.error(error_msg)
                self.log_queue.put(f"ERROR: {error_msg}")
                self.service_running = False
            except Exception as e:
                error_msg = f"服务器错误: {e}"
                self.logger.error(error_msg)
                self.log_queue.put(f"ERROR: {error_msg}")
                self.service_running = False
        
        self.service_thread = threading.Thread(target=run_server_thread, daemon=True)
        self.service_thread.start()
        self.service_process = None
        
        self.logger.info(f"嵌入式服务已启动（线程模式）")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 嵌入式服务已启动（线程模式）")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务地址: http://127.0.0.1:{port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] API 文档: http://127.0.0.1:{port}/docs")
    
    def _start_uvicorn_service(self, port: int):
        """在源码环境中使用 uvicorn 命令行方式启动服务"""
        project_root = Path(__file__).parent.parent.parent.resolve()
        api_main_path = project_root / "app" / "api_main.py"
        
        if not api_main_path.exists():
            error_msg = f"找不到 API 主文件: {api_main_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        python_exe = sys.executable
        cmd = [
            python_exe,
            "-m", "uvicorn",
            "app.api_main:app",
            "--host", "127.0.0.1",
            "--port", str(port),
            "--log-level", "info",
        ]
        
        self.logger.info(f"启动命令: {' '.join(cmd)}")
        self.logger.info(f"项目根目录: {project_root}")
        
        self.service_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace',
            cwd=str(project_root)
        )
        
        self.logger.info(f"服务进程已启动，PID: {self.service_process.pid}")
    
    def _start_log_processing(self):
        """启动日志处理"""
        is_frozen = getattr(sys, 'frozen', False)
        
        if not is_frozen:
            self.log_reader_thread = threading.Thread(
                target=self._read_process_output, 
                daemon=True
            )
            self.log_reader_thread.start()
        
        self._update_log_display()
    
    def _read_process_output(self):
        """读取子进程输出（仅源码环境）"""
        if not hasattr(self.service_process, 'stdout') or self.service_process.stdout is None:
            return
            
        try:
            for line in iter(self.service_process.stdout.readline, ''):
                if not line:
                    break
                line = line.rstrip()
                if line:
                    self.log_queue.put(line)
                
                if self.stop_event.is_set():
                    break
        except Exception as e:
            self.logger.error(f"读取进程输出时出错: {e}", exc_info=True)
        finally:
            self.logger.info("日志读取线程已停止")
    
    def _update_log_display(self):
        """更新日志显示（在主线程中定期调用）"""
        try:
            while not self.log_queue.empty():
                try:
                    log_line = self.log_queue.get_nowait()
                    self._append_to_info(log_line)
                except queue.Empty:
                    break
            
            if self.service_running:
                self.frame.after(100, self._update_log_display)
        except Exception as e:
            self.logger.error(f"更新日志显示时出错: {e}", exc_info=True)

    # ==================== ngrok 相关方法 ====================
    
    def _show_authtoken_help(self):
        """显示 Authtoken 帮助信息"""
        help_text = """ngrok Authtoken 说明

✅ 免费使用（无需注册）
• 无需 authtoken 即可使用 ngrok
• 每次启动会生成随机的公网 URL
• 适合临时测试和开发使用

⚠️ 免费版限制
• URL 每次都不同（无法固定）
• 有带宽和连接数限制
• 会话可能不够稳定

🎯 注册后的优势（可选）
• 可以使用固定的自定义域名
• 更高的带宽和连接数配额
• 更稳定的连接质量
• 可以同时运行多个隧道

📝 如何获取 Authtoken（可选）
1. 访问 https://ngrok.com/
2. 免费注册账号
3. 在 Dashboard 中获取 Authtoken
4. 将 Authtoken 填入输入框

💡 建议
• 测试阶段可以不填写 authtoken
• 正式使用建议注册获取 authtoken
• Authtoken 请妥善保管，不要泄露"""
        
        messagebox.showinfo("Authtoken 帮助", help_text)
    
    def _toggle_ngrok_token_visibility(self):
        """切换 ngrok token 的显示/隐藏"""
        if self.show_ngrok_token_var.get():
            self.ngrok_token_entry.config(show="")
        else:
            self.ngrok_token_entry.config(show="*")
    
    def _update_ngrok_status_indicator(self, running: bool):
        """更新 ngrok 状态指示器"""
        self.ngrok_status_indicator.delete("all")
        color = "green" if running else "red"
        self.ngrok_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)
    
    def _append_to_ngrok_log(self, message: str):
        """添加信息到 ngrok 日志文本框"""
        self.ngrok_log_text.config(state=tk.NORMAL)
        self.ngrok_log_text.insert(tk.END, message + "\n")
        self.ngrok_log_text.see(tk.END)
        self.ngrok_log_text.config(state=tk.DISABLED)
    
    def _clear_ngrok_log(self):
        """清空 ngrok 日志显示"""
        self.ngrok_log_text.config(state=tk.NORMAL)
        self.ngrok_log_text.delete(1.0, tk.END)
        self.ngrok_log_text.config(state=tk.DISABLED)
        self.logger.info("ngrok 日志已清空")
    
    def _copy_ngrok_url(self):
        """复制 ngrok 公网 URL 到剪贴板"""
        if self.ngrok_public_url:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(self.ngrok_public_url)
            self.frame.update()
            messagebox.showinfo("复制成功", f"已复制到剪贴板:\n{self.ngrok_public_url}")
            self.logger.info(f"已复制 ngrok URL: {self.ngrok_public_url}")
        else:
            messagebox.showwarning("警告", "ngrok 未启动或未获取到公网地址")
    
    def _start_ngrok(self):
        """启动 ngrok 隧道"""
        if not self.service_running:
            messagebox.showwarning("警告", "请先启动 FastAPI 服务！")
            return
        
        if self.ngrok_running:
            messagebox.showwarning("警告", "ngrok 已在运行中！")
            return
        
        # 初始化 ngrok 管理器（如果还没有）
        if self.ngrok_manager is None:
            self.ngrok_manager = NgrokManager(logger=self.logger)
        
        # 检查 ngrok 是否可用
        if not self.ngrok_manager.is_ngrok_available():
            messagebox.showerror(
                "ngrok 不可用", 
                "pyngrok 库未安装或不可用。\n\n请运行以下命令安装:\npip install pyngrok"
            )
            self.logger.error("pyngrok 不可用")
            self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 错误: pyngrok 库未安装")
            return
        
        authtoken = self.ngrok_token_var.get().strip()
        region = self.ngrok_region_var.get()
        port = self.service_port
        
        self.logger.info(f"启动 ngrok 隧道: port={port}, region={region}")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 正在启动 ngrok 隧道...")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 端口: {port}, 区域: {region}")
        
        # 在后台线程中启动 ngrok
        def start_ngrok_thread():
            try:
                public_url = self.ngrok_manager.start_tunnel(
                    port=port,
                    authtoken=authtoken if authtoken else None,
                    region=region
                )
                
                if public_url:
                    # 在主线程中更新 UI
                    self.frame.after(0, lambda: self._on_ngrok_started(public_url))
                else:
                    self.frame.after(0, self._on_ngrok_start_failed)
                    
            except Exception as e:
                self.logger.error(f"启动 ngrok 失败: {e}", exc_info=True)
                self.frame.after(0, lambda: self._on_ngrok_start_failed(str(e)))
        
        thread = threading.Thread(target=start_ngrok_thread, daemon=True)
        thread.start()
    
    def _on_ngrok_started(self, public_url: str):
        """ngrok 启动成功的回调"""
        self.ngrok_running = True
        self.ngrok_public_url = public_url
        
        # 更新 UI
        self._update_ngrok_status_indicator(True)
        self.ngrok_status_label.config(text="ngrok 状态: 运行中")
        self.ngrok_url_var.set(public_url)
        self.start_ngrok_btn.config(state=tk.DISABLED)
        self.stop_ngrok_btn.config(state=tk.NORMAL)
        self.copy_ngrok_url_btn.config(state=tk.NORMAL)
        self.ngrok_token_entry.config(state=tk.DISABLED)
        self.ngrok_region_combo.config(state=tk.DISABLED)
        
        # 更新日志
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] ngrok 隧道已启动")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 公网地址: {public_url}")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] API 文档: {public_url}/docs")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] " + "-" * 60)
        
        self.status_var.set(f"ngrok 运行中 - {public_url}")
        self.logger.info(f"ngrok 启动成功: {public_url}")
        
        messagebox.showinfo(
            "ngrok 启动成功",
            f"ngrok 隧道已启动！\n\n公网地址: {public_url}\nAPI 文档: {public_url}/docs\n\n请使用此地址配置 Coze 插件。"
        )
    
    def _on_ngrok_start_failed(self, error_msg: str = ""):
        """ngrok 启动失败的回调"""
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 启动失败: {error_msg}")
        self.logger.error(f"ngrok 启动失败: {error_msg}")
        
        error_text = f"无法启动 ngrok 隧道"
        if error_msg:
            error_text += f":\n\n{error_msg}"
        else:
            error_text += "。\n\n可能的原因:\n1. authtoken 未设置或无效\n2. 网络连接问题\n3. ngrok 服务不可用"
        
        messagebox.showerror("启动失败", error_text)
    
    def _stop_ngrok(self):
        """停止 ngrok 隧道"""
        if not self.ngrok_running:
            messagebox.showwarning("警告", "ngrok 未运行！")
            return
        
        self.logger.info("停止 ngrok 隧道")
        self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 正在停止 ngrok 隧道...")
        
        # 立即更新 UI 状态，让用户感觉响应迅速
        self.ngrok_running = False
        self.ngrok_public_url = None
        self._update_ngrok_status_indicator(False)
        self.ngrok_status_label.config(text="ngrok 状态: 停止中...")
        self.ngrok_url_var.set("停止中...")
        self.start_ngrok_btn.config(state=tk.DISABLED)  # 临时禁用，等停止完成后再启用
        self.stop_ngrok_btn.config(state=tk.DISABLED)
        self.copy_ngrok_url_btn.config(state=tk.DISABLED)
        self.ngrok_token_entry.config(state=tk.NORMAL)
        self.ngrok_region_combo.config(state="readonly")
        self.status_var.set("正在停止 ngrok...")
        
        # 定义停止完成的回调函数
        def on_stop_complete():
            # 在主线程中更新 UI
            self.frame.after(0, self._on_ngrok_stopped)
        
        try:
            if self.ngrok_manager:
                # 使用异步模式停止，避免阻塞 GUI
                self.ngrok_manager.stop_tunnel(async_mode=True, callback=on_stop_complete)
            else:
                # 如果没有管理器，直接完成
                self._on_ngrok_stopped()
            
        except Exception as e:
            self.logger.error(f"停止 ngrok 时出错: {e}", exc_info=True)
            self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 停止时出错: {e}")
            self._on_ngrok_stopped(error_msg=str(e))
    
    def _on_ngrok_stopped(self, error_msg: str = ""):
        """ngrok 停止完成的回调"""
        if error_msg:
            self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] 停止时出错: {error_msg}")
            self.ngrok_status_label.config(text="ngrok 状态: 停止失败")
        else:
            self._append_to_ngrok_log(f"[{time.strftime('%H:%M:%S')}] ngrok 隧道已停止")
            self.ngrok_status_label.config(text="ngrok 状态: 未启动")
            self.logger.info("ngrok 隧道已停止")
        
        self.ngrok_url_var.set("未启动")
        self.start_ngrok_btn.config(state=tk.NORMAL if self.service_running else tk.DISABLED)
        self.status_var.set("就绪")

    # ==================== 资源清理方法 ====================

    def cleanup(self):
        """清理标签页资源"""
        # 先停止 ngrok（使用异步模式，快速退出）
        if self.ngrok_running and self.ngrok_manager:
            self.logger.info("清理时停止 ngrok")
            try:
                self.ngrok_manager.stop_tunnel(async_mode=True)
            except Exception as e:
                self.logger.warning(f"清理时停止 ngrok 出错: {e}")
        
        # 停止 FastAPI 服务
        if self.service_running:
            self.logger.info("清理时停止FastAPI服务")
            self.service_running = False
            self.stop_event.set()
            
            if self.service_process:
                try:
                    self.service_process.terminate()
                    try:
                        self.service_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.service_process.kill()
                    self.service_process = None
                except Exception as e:
                    self.logger.warning(f"清理时停止服务进程出错: {e}")
            
            if self.log_reader_thread and self.log_reader_thread.is_alive():
                self.log_reader_thread.join(timeout=2)

        super().cleanup()
        self.output_folder = None
        self.draft_generator = None
        self.service_process = None
        self.log_reader_thread = None
        self.stop_event.clear()
        self.ngrok_manager = None
        self.ngrok_running = False
        self.ngrok_public_url = None
