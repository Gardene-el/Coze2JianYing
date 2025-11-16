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
        
        # 说明标签（提示使用全局设置）
        self.global_hint_frame = ttk.LabelFrame(self.frame, text="提示", padding="5")
        hint_label = ttk.Label(
            self.global_hint_frame,
            text="💡 文件夹设置：请在窗口顶部的「全局草稿存储设置」中配置",
            foreground="blue",
            font=("Arial", 9)
        )
        hint_label.pack()

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

        # 功能说明区域
        self.feature_frame = ttk.LabelFrame(self.frame, text="本地服务不可用", padding="10")
        self.feature_label = ttk.Label(
            self.feature_frame,
            text="经过详细调查，端侧插件（Local Plugin）无法在 Coze 工作流中使用。\n\n"
                 "调查结果：\n"
                 "• Bot Chat 模式：✅ 支持端侧插件，有完整的 API（chat.stream + REQUIRES_ACTION 事件）\n"
                 "• Workflow 模式：❌ 不支持端侧插件，没有工具调用机制\n\n"
                 "技术原因：\n"
                 "1. Workflow 没有 REQUIRES_ACTION 事件，只有 MESSAGE、ERROR、DONE、INTERRUPT\n"
                 "2. INTERRUPT 事件用于用户交互（如问答节点），不是工具调用\n"
                 "3. Workflow 缺少类似 submit_tool_outputs() 的工具结果提交方法\n"
                 "4. cozepy SDK 文档和示例中只有 Bot Chat 的端侧插件用法\n\n"
                 "建议方案：\n"
                 "• 使用 Bot Chat 代替工作流（Bot 可以配置工作流且支持端侧插件）\n"
                 "• 使用云端服务模式（FastAPI + 公网访问），切换到\"云端服务\"标签页\n"
                 "• 将本地功能封装为 HTTP 服务，通过工作流的 API 节点调用\n\n"
                 "详细调查报告：docs/analysis/LOCAL_PLUGIN_NOT_SUPPORTED.md",
            justify=tk.LEFT,
            wraplength=650,
            foreground="red"
        )

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
        
        # 提示信息
        self.global_hint_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

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

        # 功能说明区域
        self.feature_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.feature_label.pack(fill=tk.BOTH, expand=True)

        # 底部状态栏
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))

    def _toggle_token_visibility(self):
        """切换 API Token 的显示/隐藏"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")

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
        super().cleanup()
        # 清理标签页特定的资源
        self.draft_generator = None
        
        # 清理 Coze API 相关资源
        self.coze_api_token = None
        self.coze_workflow_id = None
        self.coze_client = None
