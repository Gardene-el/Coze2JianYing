"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import os

from gui.log_window import LogWindow
from utils.draft_generator import DraftGenerator
from utils.logger import get_logger, set_gui_log_callback


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.root = tk.Tk()
        self.root.title("Coze剪映草稿生成器")
        self.root.geometry("800x600")
        
        # 设置窗口图标（如果存在）
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        
        # 初始化草稿生成器
        self.draft_generator = DraftGenerator()
        
        # 输出文件夹路径
        self.output_folder = None
        
        # 创建日志窗口
        self.log_window = None
        
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
        view_menu.add_command(label="日志窗口", command=self._show_log_window)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
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
            height=15,
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
        self.clear_btn = ttk.Button(
            button_frame,
            text="清空",
            command=self._clear_input
        )
        self.log_btn = ttk.Button(
            button_frame,
            text="查看日志",
            command=self._show_log_window
        )
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
        # 保存组件引用
        self.main_frame = main_frame
        self.folder_frame = folder_frame
        self.folder_label = folder_label
        self.folder_entry = folder_entry
        self.input_label = input_label
        self.button_frame = button_frame
        self.status_bar = status_bar
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
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
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.log_btn.pack(side=tk.LEFT)
        
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
        
        try:
            # 调用草稿生成器，传入已验证的输出文件夹
            draft_paths = self.draft_generator.generate(content, output_folder)
            self.logger.info(f"草稿生成成功: {draft_paths}")
            self.status_var.set("草稿生成成功")
            
            # 构建结果消息
            result_msg = f"成功生成 {len(draft_paths)} 个草稿！\n\n"
            for i, path in enumerate(draft_paths, 1):
                result_msg += f"{i}. {path}\n"
            
            messagebox.showinfo("成功", result_msg)
        except Exception as e:
            self.logger.error(f"草稿生成失败: {e}", exc_info=True)
            self.status_var.set("草稿生成失败")
            messagebox.showerror("错误", f"草稿生成失败:\n{e}")
        finally:
            self.generate_btn.config(state=tk.NORMAL)
    
    def _clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", tk.END)
        self.logger.info("已清空输入")
        self.status_var.set("已清空")
    
    def _show_log_window(self):
        """显示日志窗口"""
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
        """处理日志消息"""
        if self.log_window and self.log_window.is_open():
            self.log_window.append_log(message)
    
    def _on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.logger.info("用户关闭应用程序")
            self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
