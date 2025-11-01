"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from datetime import datetime
import os

from gui.log_window import LogWindow
from gui.draft_generator_tab import DraftGeneratorTab
from gui.example_tab import ExampleTab
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
        
        # 外部日志窗口（保留用于文件菜单）
        self.log_window = None
        
        # 日志面板显示状态
        self.log_panel_visible = True
        
        # 标签页列表（用于管理所有标签页）
        self.tabs = []
        
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
        
        # 上部框架 - 主要工作区（包含标签页）
        self.top_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.top_frame, weight=3)
        
        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(self.top_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 创建标签页
        self._create_tabs()
        
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
        self.log_toolbar = log_toolbar
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.rowconfigure(0, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(1, weight=1)
    
    def _create_tabs(self):
        """创建所有标签页"""
        # 创建草稿生成器标签页（原有功能）
        draft_tab = DraftGeneratorTab(self.notebook, log_callback=self._on_log_message)
        self.tabs.append(draft_tab)
        
        # 创建示例标签页（演示扩展性）
        example_tab = ExampleTab(self.notebook)
        self.tabs.append(example_tab)
        
        self.logger.info(f"已创建 {len(self.tabs)} 个标签页")
    
    def _setup_layout(self):
        """设置布局"""
        # 日志工具栏
        self.log_toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.clear_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.save_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_scroll_check.pack(side=tk.LEFT)
        
        # 日志文本框
        self.embedded_log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _toggle_log_panel(self):
        """切换日志面板显示/隐藏"""
        if self.log_panel_visible:
            # 隐藏日志面板
            self.paned_window.remove(self.log_frame)
            self.log_panel_visible = False
        else:
            # 显示日志面板
            self.paned_window.add(self.log_frame, weight=1)
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
            
            # 清理所有标签页资源
            for tab in self.tabs:
                try:
                    tab.cleanup()
                except Exception as e:
                    self.logger.error(f"清理标签页时出错: {e}")
            
            self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
