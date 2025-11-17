"""
草稿生成器标签页模块

包含原有的草稿生成功能
"""

import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from app.gui.base_tab import BaseTab
from app.utils.draft_generator import DraftGenerator
from app.utils.draft_path_manager import get_draft_path_manager
from app.utils.logger import get_logger


class DraftGeneratorTab(BaseTab):
    """草稿生成器标签页

    包含草稿生成、元信息生成等核心功能
    """

    def __init__(self, parent: ttk.Notebook, log_callback=None):
        """
        初始化草稿生成器标签页

        Args:
            parent: 父Notebook组件
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback

        # 初始化草稿生成器（标签页特定）
        self.draft_generator = DraftGenerator()

        # 使用全局路径管理器
        self.draft_path_manager = get_draft_path_manager()

        # 后台线程相关（标签页特定）
        self.generation_thread = None
        self.is_generating = False

        # 调用父类初始化
        super().__init__(parent, "手动草稿生成（旧版）")

    def _create_widgets(self):
        """创建UI组件"""
        # 输入区域
        self.input_label = ttk.Label(self.frame, text="输入内容:")
        self.input_text = scrolledtext.ScrolledText(
            self.frame, height=10, wrap=tk.WORD, font=("Arial", 10)
        )

        # 按钮区域
        self.button_frame = ttk.Frame(self.frame)
        self.generate_btn = ttk.Button(
            self.button_frame, text="生成草稿", command=self._generate_draft
        )
        self.clear_btn = ttk.Button(
            self.button_frame, text="清空", command=self._clear_input
        )

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )

        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=0)  # 不扩展输入框所在行

    def _setup_layout(self):
        """设置布局"""
        # 输入区域
        self.input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.input_text.grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
        )  # 移除N,S避免垂直拉伸

        # 按钮区域
        self.button_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 状态栏
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))

    def _generate_draft(self):
        """生成草稿"""
        # 如果正在生成，提示用户
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成草稿，请稍候...")
            return

        content = self.input_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        # 从全局路径管理器获取输出文件夹
        output_folder = self.draft_path_manager.get_effective_output_path()

        # 验证文件夹是否存在
        if not os.path.exists(output_folder):
            messagebox.showerror(
                "错误",
                f"输出文件夹不存在:\n{output_folder}\n\n请在全局设置中配置有效的草稿文件夹。",
            )
            return

        if not os.path.isdir(output_folder):
            messagebox.showerror(
                "错误",
                f"指定的路径不是文件夹:\n{output_folder}\n\n请在全局设置中配置有效的草稿文件夹。",
            )
            return

        self.logger.info(f"开始生成草稿，输出文件夹: {output_folder}")
        self.status_var.set("正在生成草稿...")
        self.generate_btn.config(state=tk.DISABLED)
        self.is_generating = True

        # 在后台线程中生成草稿
        self.generation_thread = threading.Thread(
            target=self._generate_draft_worker,
            args=(content, output_folder),
            daemon=True,
        )
        self.generation_thread.start()

        # 定期检查线程状态
        self._check_generation_status()

    def _generate_draft_worker(self, content: str, output_folder: str):
        """后台线程工作函数"""
        try:
            # 调用草稿生成器，传入已验证的输出文件夹
            draft_paths = self.draft_generator.generate(content, output_folder)

            # 使用after方法在主线程中更新GUI
            self.frame.after(0, self._on_generation_success, draft_paths)
        except Exception as e:
            # 使用after方法在主线程中更新GUI
            self.frame.after(0, self._on_generation_error, e)

    def _check_generation_status(self):
        """定期检查生成状态"""
        if self.generation_thread and self.generation_thread.is_alive():
            # 线程仍在运行，100ms后再次检查
            self.frame.after(100, self._check_generation_status)
        else:
            # 线程已结束
            self.is_generating = False

    def _on_generation_success(self, draft_paths):
        """生成成功的回调"""
        self.logger.info(f"草稿生成成功: {draft_paths}")
        self.status_var.set("草稿生成成功")
        self.generate_btn.config(state=tk.NORMAL)

        # 构建结果消息
        result_msg = f"成功生成 {len(draft_paths)} 个草稿！\n\n"
        for i, path in enumerate(draft_paths, 1):
            result_msg += f"{i}. {path}\n"

        messagebox.showinfo("成功", result_msg)

    def _on_generation_error(self, error):
        """生成失败的回调"""
        self.logger.error(f"草稿生成失败: {error}", exc_info=True)
        self.status_var.set("草稿生成失败")
        self.generate_btn.config(state=tk.NORMAL)
        messagebox.showerror("错误", f"草稿生成失败:\n{error}")

    def _clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", tk.END)
        self.logger.info("已清空输入")
        self.status_var.set("已清空")

    def cleanup(self):
        """清理标签页资源"""
        super().cleanup()
        # 清理标签页特定的资源
        self.draft_generator = None
        self.generation_thread = None
