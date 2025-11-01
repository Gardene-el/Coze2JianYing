"""
草稿生成器标签页模块

包含原有的草稿生成功能
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from datetime import datetime
import os
import threading

from gui.base_tab import BaseTab
from utils.draft_generator import DraftGenerator
from utils.logger import get_logger


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
        
        # 输出文件夹路径（标签页特定）
        self.output_folder = None
        
        # 后台线程相关（标签页特定）
        self.generation_thread = None
        self.is_generating = False
        
        # 调用父类初始化
        super().__init__(parent, "草稿生成")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 输出文件夹选择区域
        self.folder_frame = ttk.LabelFrame(self.frame, text="输出设置", padding="5")
        
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
        
        # 输入区域
        self.input_label = ttk.Label(self.frame, text="输入内容:")
        self.input_text = scrolledtext.ScrolledText(
            self.frame,
            height=10,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.frame)
        self.generate_btn = ttk.Button(
            self.button_frame,
            text="生成草稿",
            command=self._generate_draft
        )
        self.generate_meta_btn = ttk.Button(
            self.button_frame,
            text="生成元信息",
            command=self._generate_meta_info
        )
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="清空",
            command=self._clear_input
        )
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
    
    def _setup_layout(self):
        """设置布局"""
        # 文件夹选择区域
        self.folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folder_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_btn.grid(row=0, column=2, padx=(0, 5))
        self.auto_detect_btn.grid(row=0, column=3)
        self.folder_frame.columnconfigure(1, weight=1)
        
        # 输入区域
        self.input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.input_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 按钮区域
        self.button_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.generate_meta_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态栏
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))
    
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
        
        # 确定输出文件夹
        output_folder = self.output_folder
        if output_folder is None:
            # 尝试自动检测
            output_folder = self.draft_generator.detect_default_draft_folder()
            if output_folder is None:
                messagebox.showerror(
                    "错误",
                    "未指定输出文件夹，且无法自动检测到剪映草稿文件夹。\n\n请点击「选择文件夹...」或「自动检测」按钮指定输出位置。"
                )
                return
            self.logger.info(f"自动检测到输出文件夹: {output_folder}")
        
        # 验证文件夹是否存在
        if not os.path.exists(output_folder):
            messagebox.showerror("错误", f"指定的文件夹不存在:\n{output_folder}\n\n请重新选择有效的文件夹。")
            return
        
        if not os.path.isdir(output_folder):
            messagebox.showerror("错误", f"指定的路径不是文件夹:\n{output_folder}\n\n请选择一个文件夹。")
            return
        
        self.logger.info("开始生成草稿")
        self.status_var.set("正在生成草稿...")
        self.generate_btn.config(state=tk.DISABLED)
        self.is_generating = True
        
        # 在后台线程中生成草稿
        self.generation_thread = threading.Thread(
            target=self._generate_draft_worker,
            args=(content, output_folder),
            daemon=True
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
    
    def _generate_meta_info(self):
        """生成元信息文件"""
        # 确定目标文件夹
        target_folder = self.output_folder
        if target_folder is None:
            # 尝试自动检测
            target_folder = self.draft_generator.detect_default_draft_folder()
            if target_folder is None:
                messagebox.showerror(
                    "错误",
                    "未指定文件夹，且无法自动检测到剪映草稿文件夹。\n\n请点击「选择文件夹...」或「自动检测」按钮指定位置。"
                )
                return
            self.logger.info(f"自动检测到文件夹: {target_folder}")
        
        # 验证文件夹是否存在
        if not os.path.exists(target_folder):
            messagebox.showerror("错误", f"指定的文件夹不存在:\n{target_folder}\n\n请重新选择有效的文件夹。")
            return
        
        if not os.path.isdir(target_folder):
            messagebox.showerror("错误", f"指定的路径不是文件夹:\n{target_folder}\n\n请选择一个文件夹。")
            return
        
        # 确认操作
        if not messagebox.askyesno(
            "确认生成",
            f"将在以下文件夹生成 root_meta_info.json:\n{target_folder}\n\n是否继续？"
        ):
            return
        
        self.logger.info("开始生成元信息文件")
        self.status_var.set("正在生成元信息...")
        self.generate_meta_btn.config(state=tk.DISABLED)
        
        try:
            # 调用草稿生成器的方法
            meta_info_path = self.draft_generator.generate_root_meta_info(target_folder)
            
            self.logger.info(f"元信息文件生成成功: {meta_info_path}")
            self.status_var.set("元信息生成成功")
            messagebox.showinfo("成功", f"元信息文件已生成:\n{meta_info_path}")
            
        except Exception as e:
            self.logger.error(f"元信息生成失败: {e}", exc_info=True)
            self.status_var.set("元信息生成失败")
            messagebox.showerror("错误", f"元信息生成失败:\n{e}")
        
        finally:
            self.generate_meta_btn.config(state=tk.NORMAL)
    
    def cleanup(self):
        """清理标签页资源"""
        super().cleanup()
        # 清理标签页特定的资源
        self.output_folder = None
        self.draft_generator = None
        self.generation_thread = None
