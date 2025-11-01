"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from datetime import datetime
import os
import threading
import queue

from GUI.log_window import LogWindow
from utils.draft_generator import DraftGenerator
from utils.logger import get_logger, set_gui_log_callback


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.root = tk.Tk()
        self.root.title("Coze剪映草稿生成器")
        self.root.geometry("900x700")
        
        # 设置窗口图标（如果存在）
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        
        # 初始化草稿生成器
        self.draft_generator = DraftGenerator()
        
        # 输出文件夹路径
        self.output_folder = None
        
        # 外部日志窗口（保留用于文件菜单）
        self.log_window = None
        
        # 日志面板显示状态
        self.log_panel_visible = True
        
        # 后台线程相关
        self.generation_thread = None
        self.is_generating = False
        
        # 设置GUI日志回调
        set_gui_log_callback(self._on_log_message)
        
        # 创建UI
        self._create_widgets()
        self._setup_layout()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """创建所有UI组件"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self._on_closing)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="切换日志面板", command=self._toggle_log_panel)
        view_menu.add_command(label="日志窗口（独立）", command=self._show_log_window)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
        
        # 主PanedWindow - 分隔上下区域
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 上部框架 - 主要工作区
        top_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(top_frame, weight=3)
        
        # 主框架
        main_frame = ttk.Frame(top_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输出文件夹选择区域
        folder_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="5")
        
        folder_label = ttk.Label(folder_frame, text="剪映草稿文件夹:")
        self.folder_var = tk.StringVar(value="未选择（将使用默认路径）")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, state="readonly", width=50)
        self.folder_btn = ttk.Button(
            folder_frame,
            text="选择文件夹...",
            command=self._select_output_folder
        )
        self.auto_detect_btn = ttk.Button(
            folder_frame,
            text="自动检测",
            command=self._auto_detect_folder
        )
        
        # 输入区域
        input_label = ttk.Label(main_frame, text="输入内容:")
        self.input_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        self.generate_btn = ttk.Button(
            button_frame,
            text="生成草稿",
            command=self._generate_draft
        )
        self.generate_meta_btn = ttk.Button(
            button_frame,
            text="生成元信息",
            command=self._generate_meta_info
        )
        self.clear_btn = ttk.Button(
            button_frame,
            text="清空",
            command=self._clear_input
        )
        self.toggle_log_btn = ttk.Button(
            button_frame,
            text="隐藏日志",
            command=self._toggle_log_panel
        )
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        # 下部框架 - 日志面板
        self.log_frame = ttk.LabelFrame(self.paned_window, text="日志", padding="5")
        self.paned_window.add(self.log_frame, weight=1)
        
        # 日志工具栏
        log_toolbar = ttk.Frame(self.log_frame)
        
        self.clear_log_btn = ttk.Button(
            log_toolbar,
            text="清空",
            command=self._clear_embedded_logs
        )
        self.save_log_btn = ttk.Button(
            log_toolbar,
            text="保存",
            command=self._save_embedded_logs
        )
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ttk.Checkbutton(
            log_toolbar,
            text="自动滚动",
            variable=self.auto_scroll_var
        )
        
        # 日志文本框
        self.embedded_log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            height=8
        )
        
        # 配置日志文本标签（不同日志级别使用不同颜色）
        self.embedded_log_text.tag_config("INFO", foreground="black")
        self.embedded_log_text.tag_config("WARNING", foreground="orange")
        self.embedded_log_text.tag_config("ERROR", foreground="red")
        self.embedded_log_text.tag_config("DEBUG", foreground="gray")
        
        # 保存组件引用
        self.main_frame = main_frame
        self.top_frame = top_frame
        self.folder_frame = folder_frame
        self.folder_label = folder_label
        self.folder_entry = folder_entry
        self.input_label = input_label
        self.button_frame = button_frame
        self.status_bar = status_bar
        self.log_toolbar = log_toolbar
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)
        top_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(1, weight=1)
    
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
        self.toggle_log_btn.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        # 日志工具栏
        self.log_toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.clear_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.save_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_scroll_check.pack(side=tk.LEFT)
        
        # 日志文本框
        self.embedded_log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
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
        
        # 确保日志面板可见
        if not self.log_panel_visible:
            self._toggle_log_panel()
        
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
            self.root.after(0, self._on_generation_success, draft_paths)
        except Exception as e:
            # 使用after方法在主线程中更新GUI
            self.root.after(0, self._on_generation_error, e)
    
    def _check_generation_status(self):
        """定期检查生成状态"""
        if self.generation_thread and self.generation_thread.is_alive():
            # 线程仍在运行，100ms后再次检查
            self.root.after(100, self._check_generation_status)
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
        
        # 确保日志面板可见
        if not self.log_panel_visible:
            self._toggle_log_panel()
        
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
    
    def _toggle_log_panel(self):
        """切换日志面板显示/隐藏"""
        if self.log_panel_visible:
            # 隐藏日志面板
            self.paned_window.remove(self.log_frame)
            self.toggle_log_btn.config(text="显示日志")
            self.log_panel_visible = False
        else:
            # 显示日志面板
            self.paned_window.add(self.log_frame, weight=1)
            self.toggle_log_btn.config(text="隐藏日志")
            self.log_panel_visible = True
    
    def _clear_embedded_logs(self):
        """清空嵌入式日志"""
        self.embedded_log_text.config(state=tk.NORMAL)
        self.embedded_log_text.delete("1.0", tk.END)
        self.embedded_log_text.config(state=tk.DISABLED)
    
    def _save_embedded_logs(self):
        """保存嵌入式日志到文件"""
        from tkinter import filedialog
        
        # 获取日志内容
        log_content = self.embedded_log_text.get("1.0", tk.END)
        
        # 选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def _append_to_embedded_log(self, message: str):
        """添加日志到嵌入式日志面板"""
        # 确定日志级别
        tag = "INFO"
        if "ERROR" in message:
            tag = "ERROR"
        elif "WARNING" in message:
            tag = "WARNING"
        elif "DEBUG" in message:
            tag = "DEBUG"
        
        # 添加日志
        self.embedded_log_text.config(state=tk.NORMAL)
        self.embedded_log_text.insert(tk.END, message + "\n", tag)
        self.embedded_log_text.config(state=tk.DISABLED)
        
        # 自动滚动到底部
        if self.auto_scroll_var.get():
            self.embedded_log_text.see(tk.END)
        
        # 强制更新显示
        self.embedded_log_text.update_idletasks()
    
    def _show_log_window(self):
        """显示独立日志窗口"""
        if self.log_window is None or not self.log_window.is_open():
            self.log_window = LogWindow(self.root)
        else:
            self.log_window.focus()
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = """Coze剪映草稿生成器
版本: 1.0.0

基于Tkinter和pyJianYingDraft开发

© 2025 版权所有"""
        messagebox.showinfo("关于", about_text)
    
    def _on_log_message(self, message: str):
        """处理日志消息（线程安全）"""
        # 使用after方法确保在主线程中更新GUI
        def update_log():
            # 更新嵌入式日志面板
            self._append_to_embedded_log(message)
            
            # 同时更新独立日志窗口（如果已打开）
            if self.log_window and self.log_window.is_open():
                self.log_window.append_log(message)
        
        try:
            self.root.after(0, update_log)
        except:
            # 如果root已销毁，忽略错误
            pass
    
    def _on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.logger.info("用户关闭应用程序")
            self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
