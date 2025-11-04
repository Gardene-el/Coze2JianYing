"""
本地服务标签页模块

包含FastAPI服务管理和草稿文件夹配置功能
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
import asyncio
import uvicorn
import atexit

from app.gui.base_tab import BaseTab
from app.utils.draft_generator import DraftGenerator

# Coze API 相关导入
try:
    from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL, COZE_COM_BASE_URL
    COZEPY_AVAILABLE = True
except ImportError:
    COZEPY_AVAILABLE = False
    COZE_CN_BASE_URL = "https://api.coze.cn"
    COZE_COM_BASE_URL = "https://api.coze.com"


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

        # Coze API 配置
        self.coze_api_token = None
        self.coze_base_url = COZE_CN_BASE_URL
        self.coze_client = None

        # FastAPI服务相关(使用子进程方式)
        self.service_process = None  # 子进程对象(源码环境)
        self.service_thread = None   # 服务线程(打包环境)
        self.uvicorn_server = None   # uvicorn 服务器实例(用于停止)
        self.service_running = False
        self.service_port = 8000
        self.log_queue = queue.Queue()  # 日志队列
        self.log_reader_thread = None  # 日志读取线程
        self.stop_event = threading.Event()
        
        # 注册清理函数,确保应用退出时停止服务
        atexit.register(self._cleanup_on_exit)

        # 调用父类初始化
        super().__init__(parent, "本地服务")
    
    def _cleanup_on_exit(self):
        """应用退出时的清理函数"""
        try:
            if self.service_running:
                self._stop_service()
        except:
            pass  # 忽略清理时的错误
    
    def __del__(self):
        """析构函数：确保在对象销毁时停止服务"""
        try:
            if self.service_running:
                self._stop_service()
        except:
            pass  # 忽略析构时的错误

    def _create_widgets(self):
        """创建UI组件"""
        # 草稿文件夹选择区域
        self.folder_frame = ttk.LabelFrame(self.frame, text="草稿文件夹设置", padding="5")

        self.folder_label = ttk.Label(self.folder_frame, text="剪映草稿文件夹:")
        self.folder_var = tk.StringVar(value="未选择（将使用默认路径）")
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_var, state="readonly", width=50)
        self.folder_btn = ttk.Button(self.folder_frame, text="选择文件夹...", command=self._select_output_folder)
        self.auto_detect_btn = ttk.Button(self.folder_frame, text="自动检测", command=self._auto_detect_folder)

        # Coze API 配置区域
        self.coze_frame = ttk.LabelFrame(self.frame, text="Coze API 配置", padding="5")
        
        # API Token 输入
        self.token_label = ttk.Label(self.coze_frame, text="API Token:")
        self.token_var = tk.StringVar(value="")
        self.token_entry = ttk.Entry(self.coze_frame, textvariable=self.token_var, show="*", width=50)
        
        # 显示/隐藏密码按钮
        self.show_token_var = tk.BooleanVar(value=False)
        self.show_token_btn = ttk.Checkbutton(
            self.coze_frame, 
            text="显示", 
            variable=self.show_token_var,
            command=self._toggle_token_visibility
        )
        
        # Base URL 选择
        self.base_url_label = ttk.Label(self.coze_frame, text="服务地址:")
        self.base_url_var = tk.StringVar(value=COZE_CN_BASE_URL)
        self.base_url_combo = ttk.Combobox(
            self.coze_frame,
            textvariable=self.base_url_var,
            values=[COZE_CN_BASE_URL, COZE_COM_BASE_URL],
            state="readonly",
            width=30
        )
        
        # Coze 客户端状态
        self.coze_status_label = ttk.Label(self.coze_frame, text="状态: 未配置", font=("Arial", 9))
        
        # 测试连接按钮
        self.test_coze_btn = ttk.Button(self.coze_frame, text="测试连接", command=self._test_coze_connection)

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

        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)

        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)  # 更新为row 2，因为添加了Coze配置框

    def _setup_layout(self):
        """设置布局"""
        # 草稿文件夹选择区域
        self.folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folder_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_btn.grid(row=0, column=2, padx=(0, 5))
        self.auto_detect_btn.grid(row=0, column=3)
        self.folder_frame.columnconfigure(1, weight=1)

        # Coze API 配置区域
        self.coze_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Token 输入行
        self.token_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        self.token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 5))
        self.show_token_btn.grid(row=0, column=2, padx=(0, 5), pady=(0, 5))
        
        # Base URL 选择行
        self.base_url_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        self.base_url_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 5))
        
        # 状态和测试按钮行
        self.coze_status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.test_coze_btn.grid(row=2, column=2, padx=(0, 5), pady=(5, 0))
        
        self.coze_frame.columnconfigure(1, weight=1)

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

        # 底部状态栏
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))

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

    def _toggle_token_visibility(self):
        """切换 API Token 的显示/隐藏"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")

    def _test_coze_connection(self):
        """测试 Coze API 连接"""
        if not COZEPY_AVAILABLE:
            messagebox.showerror("错误", "cozepy 库未安装。\n请运行: pip install cozepy")
            self.logger.error("cozepy 库未安装")
            return

        token = self.token_var.get().strip()
        if not token:
            messagebox.showwarning("警告", "请先输入 API Token")
            self.logger.warning("尝试测试连接但未输入 API Token")
            return

        base_url = self.base_url_var.get()
        
        self.logger.info(f"测试 Coze API 连接... (Base URL: {base_url})")
        self.coze_status_label.config(text="状态: 测试连接中...")
        self.status_var.set("正在测试 Coze API 连接...")
        
        try:
            # 创建 Coze 客户端
            from cozepy import Coze, TokenAuth
            test_client = Coze(auth=TokenAuth(token), base_url=base_url)
            
            # 存储配置
            self.coze_api_token = token
            self.coze_base_url = base_url
            self.coze_client = test_client
            
            # 更新状态
            self.coze_status_label.config(text="状态: 已配置 ✓", foreground="green")
            self.status_var.set("Coze API 配置成功")
            self.logger.info("Coze API 连接测试成功")
            
            messagebox.showinfo(
                "连接成功", 
                f"Coze API 配置成功!\n\nAPI Token: {'*' * (len(token) - 4) + token[-4:]}\nBase URL: {base_url}"
            )
            
        except Exception as e:
            self.coze_status_label.config(text="状态: 连接失败 ✗", foreground="red")
            self.status_var.set("Coze API 连接失败")
            self.logger.error(f"Coze API 连接测试失败: {e}", exc_info=True)
            messagebox.showerror("连接失败", f"无法连接到 Coze API:\n\n{str(e)}\n\n请检查:\n1. API Token 是否正确\n2. 网络连接是否正常\n3. Base URL 是否正确")

    def _get_coze_client(self):
        """获取配置好的 Coze 客户端
        
        Returns:
            Coze客户端实例，如果未配置则返回None
        """
        if self.coze_client is None:
            token = self.token_var.get().strip()
            if token and COZEPY_AVAILABLE:
                try:
                    from cozepy import Coze, TokenAuth
                    self.coze_api_token = token
                    self.coze_base_url = self.base_url_var.get()
                    self.coze_client = Coze(
                        auth=TokenAuth(self.coze_api_token),
                        base_url=self.coze_base_url
                    )
                    self.logger.info("Coze 客户端已初始化")
                except Exception as e:
                    self.logger.error(f"初始化 Coze 客户端失败: {e}")
                    return None
        return self.coze_client

    def _check_port_available(self):
        """检测端口是否可用"""
        try:
            port = int(self.port_var.get())
            if not (1024 <= port <= 65535):
                raise ValueError("端口必须在 1024-65535 之间")
        except ValueError as e:
            # 只在输入无效时使用对话框
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
        """检查端口是否可用

        Args:
            port: 要检查的端口号

        Returns:
            True 如果端口可用，False 如果端口被占用
        """
        try:
            # 尝试创建一个socket并绑定到指定端口
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("localhost", port))
                return True
        except OSError:
            # 端口已被占用
            return False

    def _update_port_status_indicator(self, status: str):
        """更新端口状态指示器

        Args:
            status: 端口状态 ("未检测", "可用", "被占用")
        """
        self.port_status_indicator.delete("all")
        if status == "可用":
            color = "green"
        elif status == "被占用":
            color = "red"
        else:  # 未检测
            color = "gray"
        self.port_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _update_status_indicator(self, running: bool):
        """更新服务状态指示器

        Args:
            running: 服务是否运行中
        """
        self.service_status_indicator.delete("all")
        color = "green" if running else "red"
        self.service_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _append_to_info(self, message: str, tag: str = None):
        """添加信息到服务信息文本框
        
        Args:
            message: 日志消息
            tag: 可选的文本标签，用于着色
        """
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

        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务进程已启动 (PID: {self.service_process.pid})")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 访问地址: http://localhost:{port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] API文档: http://localhost:{port}/docs")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] " + "-" * 60)
        
        # 启动日志处理
        self._start_log_processing()

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

    def _start_service_process(self, port: int):
        """启动FastAPI服务
        
        根据运行环境选择不同的启动方式：
        - 打包环境（exe）：使用多进程方式启动
        - 源码环境：使用子进程+uvicorn方式启动
        
        Args:
            port: 服务端口
        """
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
                # 配置 uvicorn，禁用默认日志配置以避免打包环境的配置错误
                config = uvicorn.Config(
                    app=app,
                    host="127.0.0.1",
                    port=port,
                    log_level="error",  # 降低日志级别
                    access_log=False,   # 禁用访问日志
                    log_config=None     # 禁用日志配置文件
                )
                server = uvicorn.Server(config)
                
                # 保存 server 实例以便后续停止
                self.uvicorn_server = server
                
                # 运行服务器（阻塞调用）
                server.run()
            except OSError as e:
                # 处理端口占用等网络错误
                if e.errno == 10048:  # Windows: 地址已在使用中
                    error_msg = f"端口 {port} 已被占用，请选择其他端口"
                else:
                    error_msg = f"网络错误: {e}"
                self.logger.error(error_msg)
                self.log_queue.put(f"ERROR: {error_msg}")
                # 标记服务未运行
                self.service_running = False
            except Exception as e:
                error_msg = f"服务器错误: {e}"
                self.logger.error(error_msg)
                self.log_queue.put(f"ERROR: {error_msg}")
                self.service_running = False
        
        # 使用线程启动服务（避免多进程的序列化问题）
        self.service_thread = threading.Thread(target=run_server_thread, daemon=True)
        self.service_thread.start()
        
        # 标记为线程模式（用于停止时判断）
        self.service_process = None  # 没有进程对象
        
        self.logger.info(f"嵌入式服务已启动（线程模式）")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 嵌入式服务已启动（线程模式）")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] 服务地址: http://127.0.0.1:{port}")
        self._append_to_info(f"[{time.strftime('%H:%M:%S')}] API 文档: http://127.0.0.1:{port}/docs")
    
    def _start_uvicorn_service(self, port: int):
        """在源码环境中使用 uvicorn 命令行方式启动服务"""
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.resolve()
        
        # 验证 api_main.py 是否存在
        api_main_path = project_root / "app" / "api_main.py"
        if not api_main_path.exists():
            error_msg = f"找不到 API 主文件: {api_main_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 构建启动命令
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
        
        # 启动子进程
        self.service_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace',
            cwd=str(project_root)  # 设置工作目录
        )
        
        self.logger.info(f"服务进程已启动，PID: {self.service_process.pid}")
    
    def _start_log_processing(self):
        """启动日志处理
        
        只在源码环境中读取子进程输出
        打包环境的 Process 不支持 stdout 捕获
        """
        is_frozen = getattr(sys, 'frozen', False)
        
        if not is_frozen:
            # 只在源码环境启动日志读取线程
            self.log_reader_thread = threading.Thread(
                target=self._read_process_output, 
                daemon=True
            )
            self.log_reader_thread.start()
        
        # 启动日志显示更新
        self._update_log_display()
    
    def _read_process_output(self):
        """读取子进程输出（仅源码环境，在后台线程中运行）"""
        if not hasattr(self.service_process, 'stdout') or self.service_process.stdout is None:
            return
            
        try:
            for line in iter(self.service_process.stdout.readline, ''):
                if not line:
                    break
                # 去除末尾换行符
                line = line.rstrip()
                if line:
                    # 将日志放入队列
                    self.log_queue.put(line)
                
                # 检查是否需要停止
                if self.stop_event.is_set():
                    break
        except Exception as e:
            self.logger.error(f"读取进程输出时出错: {e}", exc_info=True)
        finally:
            self.logger.info("日志读取线程已停止")
    
    def _update_log_display(self):
        """更新日志显示（在主线程中定期调用）"""
        try:
            # 从队列中获取所有可用的日志
            has_new_log = False
            while not self.log_queue.empty():
                try:
                    log_line = self.log_queue.get_nowait()
                    self._append_to_info(log_line)
                    has_new_log = True
                except queue.Empty:
                    break
            
            # 如果服务正在运行，继续定期更新
            if self.service_running:
                self.frame.after(100, self._update_log_display)  # 每100ms更新一次
        except Exception as e:
            self.logger.error(f"更新日志显示时出错: {e}", exc_info=True)

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
            self.logger.info("清理时停止FastAPI服务")
            self.service_running = False
            self.stop_event.set()
            
            # 终止子进程
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
            
            # 等待日志线程结束
            if self.log_reader_thread and self.log_reader_thread.is_alive():
                self.log_reader_thread.join(timeout=2)

        super().cleanup()
        # 清理标签页特定的资源
        self.output_folder = None
        self.draft_generator = None
        self.service_process = None
        self.log_reader_thread = None
        self.stop_event.clear()
        
        # 清理 Coze API 相关资源
        self.coze_api_token = None
        self.coze_client = None
