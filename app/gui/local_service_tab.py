"""
本地服务标签页模块（端插件）

用于端插件模式：使用 cozepy SDK 监听 Coze Bot 事件，在本地执行操作
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
    """本地服务标签页（端插件）

    用于端插件模式：使用 cozepy SDK 连接 Coze Bot，监听事件并在本地执行操作
    不同于云端服务，这里需要配置 Coze Token 和 Bot ID
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

        # Coze API 配置（端插件必需）
        self.coze_api_token = None
        self.coze_base_url = COZE_CN_BASE_URL
        self.coze_workflow_id = None
        self.coze_client = None

        # 调用父类初始化
        super().__init__(parent, "本地服务")

    def _create_widgets(self):
        """创建UI组件"""
        # 说明文字
        self.info_label_frame = ttk.LabelFrame(self.frame, text="端插件说明", padding="10")
        self.info_label = ttk.Label(
            self.info_label_frame,
            text="端插件模式：使用 cozepy SDK 连接 Coze Workflow，监听 SSE 事件并在本地执行操作。\n需要配置 Coze API Token 和 Workflow ID。本地应用无需公网 IP。",
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

        # Coze API 配置区域（端插件必需）
        self.coze_frame = ttk.LabelFrame(self.frame, text="Coze API 配置（端插件必需）", padding="5")
        
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
        
        # Workflow ID 输入
        self.workflow_id_label = ttk.Label(self.coze_frame, text="Workflow ID:")
        self.workflow_id_var = tk.StringVar(value="")
        self.workflow_id_entry = ttk.Entry(self.coze_frame, textvariable=self.workflow_id_var, width=50)
        
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

        # 端插件服务管理区域
        self.plugin_frame = ttk.LabelFrame(self.frame, text="端插件服务管理", padding="10")
        
        # 运行模式选择
        self.mode_frame = ttk.Frame(self.plugin_frame)
        self.mode_label = ttk.Label(self.mode_frame, text="运行模式:")
        self.mode_var = tk.StringVar(value="bot")
        self.mode_bot_radio = ttk.Radiobutton(
            self.mode_frame, 
            text="Bot 模式（对话驱动）", 
            variable=self.mode_var, 
            value="bot"
        )
        self.mode_workflow_radio = ttk.Radiobutton(
            self.mode_frame, 
            text="Workflow 模式（流程驱动）", 
            variable=self.mode_var, 
            value="workflow"
        )
        
        # Bot ID / Workflow ID 输入（根据模式切换）
        self.target_id_frame = ttk.Frame(self.plugin_frame)
        self.target_id_label = ttk.Label(self.target_id_frame, text="Bot ID:")
        self.target_id_var = tk.StringVar(value="")
        self.target_id_entry = ttk.Entry(self.target_id_frame, textvariable=self.target_id_var, width=40)
        
        # 绑定模式切换事件
        self.mode_var.trace_add('write', self._on_mode_changed)
        
        # 服务状态显示
        self.plugin_status_frame = ttk.Frame(self.plugin_frame)
        self.plugin_status_label = ttk.Label(self.plugin_status_frame, text="服务状态: 未启动", font=("Arial", 10, "bold"))
        self.plugin_status_indicator = tk.Canvas(self.plugin_status_frame, width=20, height=20, highlightthickness=0)
        self._update_plugin_status_indicator(False)
        
        # 服务控制按钮
        self.plugin_control_frame = ttk.Frame(self.plugin_frame)
        self.start_plugin_btn = ttk.Button(
            self.plugin_control_frame, 
            text="启动端插件服务", 
            command=self._start_plugin_service
        )
        self.stop_plugin_btn = ttk.Button(
            self.plugin_control_frame, 
            text="停止服务", 
            command=self._stop_plugin_service, 
            state=tk.DISABLED
        )
        
        # 服务日志显示
        self.plugin_log_frame = ttk.LabelFrame(self.plugin_frame, text="服务日志", padding="5")
        self.plugin_log_text = tk.Text(
            self.plugin_log_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.plugin_log_scrollbar = ttk.Scrollbar(
            self.plugin_log_frame, 
            orient=tk.VERTICAL, 
            command=self.plugin_log_text.yview
        )
        self.plugin_log_text.config(yscrollcommand=self.plugin_log_scrollbar.set)
        self.clear_plugin_log_btn = ttk.Button(
            self.plugin_log_frame, 
            text="清空日志", 
            command=self._clear_plugin_log
        )
        
        # 端插件服务实例
        self.plugin_service = None
        self.plugin_service_running = False

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

        # Coze API 配置区域
        self.coze_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Token 输入行
        self.token_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        self.token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 5))
        self.show_token_btn.grid(row=0, column=2, padx=(0, 5), pady=(0, 5))
        
        # Workflow ID 输入行
        self.workflow_id_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        self.workflow_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 5))
        
        # Base URL 选择行
        self.base_url_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        self.base_url_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 5))
        
        # 状态和测试按钮行
        self.coze_status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.test_coze_btn.grid(row=3, column=2, padx=(0, 5), pady=(5, 0))
        
        self.coze_frame.columnconfigure(1, weight=1)

        # 端插件服务管理区域
        self.plugin_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 运行模式
        self.mode_frame.pack(fill=tk.X, pady=(0, 10))
        self.mode_label.pack(side=tk.LEFT, padx=(0, 10))
        self.mode_bot_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.mode_workflow_radio.pack(side=tk.LEFT)
        
        # Target ID
        self.target_id_frame.pack(fill=tk.X, pady=(0, 10))
        self.target_id_label.pack(side=tk.LEFT, padx=(0, 5))
        self.target_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 服务状态
        self.plugin_status_frame.pack(fill=tk.X, pady=(0, 10))
        self.plugin_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.plugin_status_label.pack(side=tk.LEFT)
        
        # 服务控制按钮
        self.plugin_control_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_plugin_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_plugin_btn.pack(side=tk.LEFT)
        
        # 服务日志
        self.plugin_log_frame.pack(fill=tk.BOTH, expand=True)
        log_content_frame = ttk.Frame(self.plugin_log_frame)
        log_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.plugin_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, in_=log_content_frame)
        self.plugin_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=log_content_frame)
        self.clear_plugin_log_btn.pack(side=tk.RIGHT)

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

    def _toggle_token_visibility(self):
        """切换 API Token 的显示/隐藏"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def _on_mode_changed(self, *args):
        """模式切换事件处理"""
        mode = self.mode_var.get()
        if mode == "bot":
            self.target_id_label.config(text="Bot ID:")
        else:
            self.target_id_label.config(text="Workflow ID:")
    
    def _update_plugin_status_indicator(self, running: bool):
        """更新端插件服务状态指示器"""
        self.plugin_status_indicator.delete("all")
        color = "green" if running else "red"
        self.plugin_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)
    
    def _append_to_plugin_log(self, message: str):
        """添加信息到端插件日志"""
        self.plugin_log_text.config(state=tk.NORMAL)
        self.plugin_log_text.insert(tk.END, message + "\n")
        self.plugin_log_text.see(tk.END)
        self.plugin_log_text.config(state=tk.DISABLED)
    
    def _clear_plugin_log(self):
        """清空端插件日志"""
        self.plugin_log_text.config(state=tk.NORMAL)
        self.plugin_log_text.delete(1.0, tk.END)
        self.plugin_log_text.config(state=tk.DISABLED)
        self.logger.info("端插件日志已清空")
    
    def _start_plugin_service(self):
        """启动端插件服务"""
        if self.plugin_service_running:
            messagebox.showwarning("警告", "服务已在运行中！")
            return
        
        # 检查 cozepy 是否可用
        if not COZEPY_AVAILABLE:
            messagebox.showerror(
                "错误", 
                "cozepy SDK 未安装。\n\n请运行: pip install cozepy"
            )
            self.logger.error("cozepy SDK 未安装")
            return
        
        # 检查配置
        token = self.token_var.get().strip()
        if not token:
            messagebox.showwarning("警告", "请先输入 API Token")
            return
        
        target_id = self.target_id_var.get().strip()
        if not target_id:
            mode_name = "Bot ID" if self.mode_var.get() == "bot" else "Workflow ID"
            messagebox.showwarning("警告", f"请先输入 {mode_name}")
            return
        
        base_url = self.base_url_var.get()
        mode = self.mode_var.get()
        
        self.logger.info(f"启动端插件服务 ({mode} 模式)...")
        self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 正在启动端插件服务...")
        self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 模式: {mode}")
        self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] Target ID: {target_id}")
        
        try:
            # 导入端插件服务
            from app.services.local_plugin_service import (
                LocalPluginService, 
                create_draft_tool_handler
            )
            
            # 创建服务实例
            self.plugin_service = LocalPluginService(
                coze_token=token,
                base_url=base_url,
                logger=self.logger
            )
            
            # 注册草稿生成工具
            draft_handler = create_draft_tool_handler(self.draft_generator)
            self.plugin_service.register_tool("generate_draft", draft_handler)
            
            self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 已注册工具: generate_draft")
            
            # 根据模式启动服务
            success = False
            if mode == "bot":
                success = self.plugin_service.start_bot_mode(
                    bot_id=target_id,
                    user_id="local-user"
                )
            else:  # workflow
                success = self.plugin_service.start_workflow_mode(
                    workflow_id=target_id,
                    parameters={}
                )
            
            if success:
                self.plugin_service_running = True
                self._update_plugin_status_indicator(True)
                self.plugin_status_label.config(text=f"服务状态: 运行中 ({mode} 模式)")
                self.start_plugin_btn.config(state=tk.DISABLED)
                self.stop_plugin_btn.config(state=tk.NORMAL)
                
                self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] ✓ 服务已启动")
                self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] " + "=" * 60)
                
                if mode == "bot":
                    self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 💡 请在 Coze 平台与 Bot 对话")
                    self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 当 Bot 调用工具时，本地会自动执行")
                else:
                    self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 💡 Workflow 将自动执行")
                    self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 完成后服务将自动停止")
                
                self.status_var.set(f"端插件服务运行中 ({mode} 模式)")
                self.logger.info("端插件服务启动成功")
            else:
                self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] ✗ 服务启动失败")
                messagebox.showerror("启动失败", "无法启动端插件服务")
        
        except Exception as e:
            self.logger.error(f"启动端插件服务失败: {e}", exc_info=True)
            self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] ✗ 错误: {e}")
            messagebox.showerror("启动失败", f"无法启动端插件服务:\n{e}")
    
    def _stop_plugin_service(self):
        """停止端插件服务"""
        if not self.plugin_service_running:
            messagebox.showwarning("警告", "服务未运行！")
            return
        
        self.logger.info("停止端插件服务...")
        self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] 正在停止服务...")
        
        try:
            if self.plugin_service:
                self.plugin_service.stop()
            
            self.plugin_service_running = False
            self._update_plugin_status_indicator(False)
            self.plugin_status_label.config(text="服务状态: 未启动")
            self.start_plugin_btn.config(state=tk.NORMAL)
            self.stop_plugin_btn.config(state=tk.DISABLED)
            
            self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] ✓ 服务已停止")
            self.status_var.set("就绪")
            self.logger.info("端插件服务已停止")
        
        except Exception as e:
            self.logger.error(f"停止端插件服务时出错: {e}", exc_info=True)
            self._append_to_plugin_log(f"[{time.strftime('%H:%M:%S')}] ✗ 停止时出错: {e}")

    def _test_coze_connection(self):
        """测试 Coze API 连接（端插件模式）"""
        if not COZEPY_AVAILABLE:
            messagebox.showerror("错误", "cozepy 库未安装。\n请运行: pip install cozepy")
            self.logger.error("cozepy 库未安装")
            return

        token = self.token_var.get().strip()
        workflow_id = self.workflow_id_var.get().strip()
        
        if not token:
            messagebox.showwarning("警告", "请先输入 API Token")
            self.logger.warning("尝试测试连接但未输入 API Token")
            return
        
        if not workflow_id:
            messagebox.showwarning("警告", "请先输入 Workflow ID")
            self.logger.warning("尝试测试连接但未输入 Workflow ID")
            return

        base_url = self.base_url_var.get()
        
        self.logger.info(f"测试 Coze API 连接... (Base URL: {base_url})")
        self.coze_status_label.config(text="状态: 测试连接中...")
        self.status_var.set("正在测试 Coze API 连接...")
        
        try:
            # 创建 Coze 客户端
            from cozepy import Coze, TokenAuth
            test_client = Coze(auth=TokenAuth(token), base_url=base_url)
            
            # 存储配置（包括 Workflow ID）
            self.coze_api_token = token
            self.coze_base_url = base_url
            self.coze_workflow_id = workflow_id
            self.coze_client = test_client
            
            # 更新状态
            self.coze_status_label.config(text="状态: 已配置 ✓", foreground="green")
            self.status_var.set("Coze API 配置成功")
            self.logger.info("Coze API 连接测试成功")
            
            messagebox.showinfo(
                "连接成功", 
                f"Coze API 配置成功!\n\nAPI Token: {'*' * (len(token) - 4) + token[-4:]}\nWorkflow ID: {workflow_id}\nBase URL: {base_url}"
            )
            
        except Exception as e:
            self.coze_status_label.config(text="状态: 连接失败 ✗", foreground="red")
            self.status_var.set("Coze API 连接失败")
            self.logger.error(f"Coze API 连接测试失败: {e}", exc_info=True)
            messagebox.showerror("连接失败", f"无法连接到 Coze API:\n\n{str(e)}\n\n请检查:\n1. API Token 是否正确\n2. Workflow ID 是否正确\n3. 网络连接是否正常\n4. Base URL 是否正确")

    def _get_coze_client(self):
        """获取配置好的 Coze 客户端
        
        Returns:
            Coze客户端实例，如果未配置则返回None
        """
        if self.coze_client is None:
            token = self.token_var.get().strip()
            workflow_id = self.workflow_id_var.get().strip()
            if token and workflow_id and COZEPY_AVAILABLE:
                try:
                    from cozepy import Coze, TokenAuth
                    self.coze_api_token = token
                    self.coze_base_url = self.base_url_var.get()
                    self.coze_workflow_id = workflow_id
                    self.coze_client = Coze(
                        auth=TokenAuth(self.coze_api_token),
                        base_url=self.coze_base_url
                    )
                    self.logger.info("Coze 客户端已初始化")
                except Exception as e:
                    self.logger.error(f"初始化 Coze 客户端失败: {e}")
                    return None
        return self.coze_client

    def cleanup(self):
        """清理标签页资源"""
        # 停止端插件服务
        if self.plugin_service_running and self.plugin_service:
            self.logger.info("清理时停止端插件服务")
            try:
                self.plugin_service.stop()
            except Exception as e:
                self.logger.warning(f"清理时停止端插件服务出错: {e}")
        
        super().cleanup()
        # 清理标签页特定的资源
        self.output_folder = None
        self.draft_generator = None
        
        # 清理 Coze API 相关资源
        self.coze_api_token = None
        self.coze_workflow_id = None
        self.coze_client = None
        
        # 清理端插件服务
        self.plugin_service = None
        self.plugin_service_running = False
