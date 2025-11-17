"""
主窗口模块
"""

import os
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from app.gui.cloud_service_tab import CloudServiceTab
from app.gui.draft_generator_tab import DraftGeneratorTab
from app.gui.log_window import LogWindow
from app.gui.script_executor_tab import ScriptExecutorTab
from app.utils.logger import get_logger, set_gui_log_callback
from app.utils.draft_path_manager import get_draft_path_manager


class MainWindow:
    """主窗口类"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.root = tk.Tk()
        self.root.title("Coze剪映草稿生成器")
        self.root.geometry("900x700")

        # 外部日志窗口（保留用于文件菜单）
        self.log_window = None

        # 日志面板显示状态
        self.log_panel_visible = True

        # 标签页列表（用于管理所有标签页）
        self.tabs = []
        
        # 全局草稿路径管理器
        self.draft_path_manager = get_draft_path_manager()

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
        file_menu.add_command(label="打开数据文件夹", command=self._open_data_folder)
        file_menu.add_command(label="清空数据文件", command=self._clear_data_files)
        file_menu.add_command(label="清空缓存", command=self._clear_cache)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

        # 主PanedWindow - 分隔上下区域（使用tk.PanedWindow避免拖影）
        self.paned_window = tk.PanedWindow(
            self.root,
            orient=tk.VERTICAL,
            sashwidth=8,  # 分隔条宽度
            sashrelief=tk.RAISED,  # 分隔条样式（凸起）
            sashpad=2,  # 分隔条内边距
            bg="#d0d0d0",  # 分隔条背景色（灰色，更明显）
            bd=1,  # 边框宽度
            relief=tk.SUNKEN,  # 边框样式
        )
        self.paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 上部框架 - 主要工作区（包含标签页和滚动条）
        self.top_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.top_frame, minsize=300, stretch="always")

        # 创建Canvas和滚动条用于标签页区域
        self.top_canvas = tk.Canvas(self.top_frame, highlightthickness=0)
        self.top_scrollbar = ttk.Scrollbar(
            self.top_frame, orient=tk.VERTICAL, command=self.top_canvas.yview
        )
        self.top_canvas.configure(yscrollcommand=self.top_scrollbar.set)

        # 创建容器框架用于放置Notebook
        self.notebook_container = ttk.Frame(self.top_canvas)
        self.canvas_window = self.top_canvas.create_window(
            (0, 0), window=self.notebook_container, anchor=tk.NW
        )
        
        # 全局草稿路径设置面板（在标签页上方）
        self.path_settings_frame = ttk.LabelFrame(
            self.notebook_container, 
            text="全局草稿路径设置", 
            padding="10"
        )
        
        # 路径选择区域
        self.path_select_frame = ttk.Frame(self.path_settings_frame)
        
        self.path_label = ttk.Label(self.path_select_frame, text="剪映草稿文件夹:")
        self.path_var = tk.StringVar(value="未选择")
        self.path_entry = ttk.Entry(
            self.path_select_frame, 
            textvariable=self.path_var, 
            state="readonly", 
            width=50
        )
        self.path_select_btn = ttk.Button(
            self.path_select_frame,
            text="选择文件夹...",
            command=self._select_draft_folder
        )
        self.path_auto_detect_btn = ttk.Button(
            self.path_select_frame,
            text="自动检测",
            command=self._auto_detect_draft_folder
        )
        
        # 传输选项区域
        self.transfer_frame = ttk.Frame(self.path_settings_frame)
        
        self.transfer_var = tk.BooleanVar(value=False)
        self.transfer_check = ttk.Checkbutton(
            self.transfer_frame,
            text="传输草稿到指定文件夹（启用后草稿将直接保存到剪映草稿文件夹，否则保存在本地数据目录）",
            variable=self.transfer_var,
            command=self._on_transfer_option_changed
        )
        
        # 状态显示
        self.path_status_var = tk.StringVar(value="当前使用本地数据目录")
        self.path_status_label = ttk.Label(
            self.path_settings_frame,
            textvariable=self.path_status_var,
            foreground="blue"
        )

        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(self.notebook_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 绑定Canvas大小变化事件
        self.notebook_container.bind(
            "<Configure>", self._on_notebook_container_configure
        )
        self.top_canvas.bind("<Configure>", self._on_canvas_configure)

        # 绑定鼠标滚轮事件
        self.top_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 创建标签页
        self._create_tabs()

        # 下部框架 - 日志面板
        self.log_frame = ttk.LabelFrame(self.paned_window, text="日志", padding="5")
        self.paned_window.add(self.log_frame, minsize=150, stretch="always")

        # 日志工具栏
        log_toolbar = ttk.Frame(self.log_frame)

        self.clear_log_btn = ttk.Button(
            log_toolbar, text="清空", command=self._clear_embedded_logs
        )
        self.save_log_btn = ttk.Button(
            log_toolbar, text="保存", command=self._save_embedded_logs
        )
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ttk.Checkbutton(
            log_toolbar, text="自动滚动", variable=self.auto_scroll_var
        )

        # 日志文本框
        self.embedded_log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            height=8,
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
        self.top_frame.columnconfigure(1, weight=0)  # 滚动条列不扩展
        self.top_frame.rowconfigure(0, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(1, weight=1)

    def _on_notebook_container_configure(self, event):
        """当notebook容器大小改变时更新滚动区域"""
        self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """当canvas大小改变时调整内部窗口宽度"""
        canvas_width = event.width
        self.top_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 检查鼠标是否在top_canvas区域内
        if (
            self.top_canvas.winfo_containing(event.x_root, event.y_root)
            == self.top_canvas
            or self.notebook.winfo_containing(event.x_root, event.y_root) is not None
        ):
            # Windows和Linux的滚轮事件delta不同
            if event.delta:
                self.top_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    self.top_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.top_canvas.yview_scroll(1, "units")

    def _create_tabs(self):
        """创建所有标签页"""
        # 创建云端服务标签页（基于已有服务的云侧插件）
        cloud_service_tab = CloudServiceTab(
            self.notebook, log_callback=self._on_log_message
        )
        self.tabs.append(cloud_service_tab)
        self._add_tooltip(
            0, "启动 FastAPI 服务，配置为 Coze 云侧插件\n无需 cozepy SDK 或 Coze Token"
        )

        # 创建脚本执行标签页（方案三：脚本生成执行）
        script_executor_tab = ScriptExecutorTab(
            self.notebook, log_callback=self._on_log_message
        )
        self.tabs.append(script_executor_tab)
        self._add_tooltip(1, "执行从Coze导出的Python脚本生成草稿")

        # 创建手动草稿生成器标签页（原有功能 - 旧版）
        draft_tab = DraftGeneratorTab(self.notebook, log_callback=self._on_log_message)
        self.tabs.append(draft_tab)
        self._add_tooltip(2, "手动粘贴 JSON 生成草稿（旧版）")

        self.logger.info(f"已创建 {len(self.tabs)} 个标签页")

    def _add_tooltip(self, tab_index: int, text: str):
        """为标签页添加工具提示

        Args:
            tab_index: 标签页索引
            text: 提示文本
        """

        # 创建工具提示类
        class ToolTip:
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tip_window = None
                widget.bind("<Enter>", self.show_tip)
                widget.bind("<Leave>", self.hide_tip)

            def show_tip(self, event=None):
                if self.tip_window or not self.text:
                    return
                x, y, _, _ = self.widget.bbox("insert")
                x += self.widget.winfo_rootx() + 25
                y += self.widget.winfo_rooty() + 25

                self.tip_window = tw = tk.Toplevel(self.widget)
                tw.wm_overrideredirect(True)
                tw.wm_geometry(f"+{x}+{y}")

                label = tk.Label(
                    tw,
                    text=self.text,
                    justify=tk.LEFT,
                    background="#ffffe0",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=("Arial", 9),
                )
                label.pack()

            def hide_tip(self, event=None):
                if self.tip_window:
                    self.tip_window.destroy()
                    self.tip_window = None

        # 获取标签页的标签控件
        try:
            tab_id = self.notebook.tabs()[tab_index]
            # 为整个notebook绑定鼠标事件
            if not hasattr(self, "_tab_tooltips"):
                self._tab_tooltips = {}
                self.notebook.bind("<Motion>", self._on_tab_motion)
                self.notebook.bind("<Leave>", self._hide_all_tooltips)

            self._tab_tooltips[tab_index] = text
        except Exception as e:
            self.logger.warning(f"添加工具提示失败: {e}")

    def _on_tab_motion(self, event):
        """处理鼠标在notebook上移动"""
        try:
            # 获取鼠标下的标签页索引
            tab_index = self.notebook.index(f"@{event.x},{event.y}")

            # 如果鼠标在标签上且有tooltip
            if tab_index >= 0 and tab_index in self._tab_tooltips:
                self._show_tab_tooltip(
                    event.x_root, event.y_root, self._tab_tooltips[tab_index]
                )
            else:
                self._hide_all_tooltips()
        except:
            self._hide_all_tooltips()

    def _show_tab_tooltip(self, x, y, text):
        """显示标签页工具提示"""
        if hasattr(self, "_tooltip_window") and self._tooltip_window:
            return

        self._tooltip_window = tw = tk.Toplevel(self.root)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x + 10}+{y + 10}")

        label = tk.Label(
            tw,
            text=text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            padx=5,
            pady=3,
        )
        label.pack()

    def _hide_all_tooltips(self, event=None):
        """隐藏所有工具提示"""
        if hasattr(self, "_tooltip_window") and self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None

    def _setup_layout(self):
        """设置布局"""
        # 布局全局路径设置面板
        self.path_settings_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # 路径选择区域
        self.path_select_frame.pack(fill=tk.X, pady=(0, 10))
        self.path_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.path_select_btn.grid(row=0, column=2, padx=(0, 5))
        self.path_auto_detect_btn.grid(row=0, column=3)
        self.path_select_frame.columnconfigure(1, weight=1)
        
        # 传输选项区域
        self.transfer_frame.pack(fill=tk.X, pady=(0, 5))
        self.transfer_check.pack(side=tk.LEFT)
        
        # 状态显示
        self.path_status_label.pack(fill=tk.X, pady=(0, 5))
        
        # 布局上部框架（Canvas和滚动条）
        self.top_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.top_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

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
            filetypes=[
                ("日志文件", "*.log"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*"),
            ],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
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
    
    def _select_draft_folder(self):
        """选择草稿文件夹"""
        # 设置初始目录
        current_path = self.draft_path_manager.get_draft_folder()
        initial_dir = current_path if current_path else os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="选择剪映草稿文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            self.draft_path_manager.set_draft_folder(folder)
            self.path_var.set(folder)
            self.logger.info(f"已选择草稿文件夹: {folder}")
            self._update_path_status()
    
    def _auto_detect_draft_folder(self):
        """自动检测剪映草稿文件夹"""
        self.logger.info("尝试自动检测剪映草稿文件夹...")
        
        detected_path = self.draft_path_manager.detect_default_draft_folder()
        
        if detected_path:
            self.draft_path_manager.set_draft_folder(detected_path)
            self.path_var.set(detected_path)
            self.logger.info(f"检测到剪映草稿文件夹: {detected_path}")
            self._update_path_status()
            messagebox.showinfo("检测成功", f"已检测到剪映草稿文件夹:\n{detected_path}")
        else:
            self.logger.warning("未能检测到剪映草稿文件夹")
            messagebox.showwarning(
                "检测失败",
                "未能自动检测到剪映草稿文件夹。\n请手动选择或确认剪映专业版已安装。"
            )
    
    def _on_transfer_option_changed(self):
        """传输选项改变时的回调"""
        enabled = self.transfer_var.get()
        self.draft_path_manager.set_transfer_enabled(enabled)
        self.logger.info(f"传输草稿到指定文件夹: {'启用' if enabled else '禁用'}")
        self._update_path_status()
    
    def _update_path_status(self):
        """更新路径状态显示"""
        status_text = self.draft_path_manager.get_status_text()
        self.path_status_var.set(f"当前状态: {status_text}")

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
    
    def _open_data_folder(self):
        """打开数据文件夹"""
        import subprocess
        from app.config import get_config
        
        try:
            config = get_config()
            data_root = config.data_root
            
            if not os.path.exists(data_root):
                messagebox.showwarning("警告", f"数据文件夹不存在:\n{data_root}")
                return
            
            # 在 Windows 中打开文件夹
            if os.name == 'nt':
                os.startfile(data_root)
            else:
                # 非 Windows 系统使用 xdg-open 或 open
                try:
                    subprocess.run(['xdg-open', data_root], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(['open', data_root], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        messagebox.showerror("错误", f"无法打开文件夹:\n{data_root}\n请手动打开。")
            
            self.logger.info(f"打开数据文件夹: {data_root}")
        except Exception as e:
            self.logger.error(f"打开数据文件夹失败: {e}", exc_info=True)
            messagebox.showerror("错误", f"打开数据文件夹失败:\n{e}")
    
    def _clear_data_files(self):
        """清空数据文件"""
        from app.config import get_config
        
        if not messagebox.askyesno(
            "确认清空", 
            "确定要清空所有数据文件吗？\n\n这将删除所有草稿配置和片段数据。\n此操作不可恢复！",
            icon='warning'
        ):
            return
        
        try:
            config = get_config()
            drafts_dir = config.drafts_dir
            
            if os.path.exists(drafts_dir):
                import shutil
                # 删除并重建目录
                shutil.rmtree(drafts_dir)
                os.makedirs(drafts_dir, exist_ok=True)
                self.logger.info(f"已清空数据文件: {drafts_dir}")
                messagebox.showinfo("成功", f"数据文件已清空！\n\n文件夹: {drafts_dir}")
            else:
                self.logger.warning(f"数据文件夹不存在: {drafts_dir}")
                messagebox.showinfo("提示", "数据文件夹不存在，无需清空。")
        except Exception as e:
            self.logger.error(f"清空数据文件失败: {e}", exc_info=True)
            messagebox.showerror("错误", f"清空数据文件失败:\n{e}")
    
    def _clear_cache(self):
        """清空缓存"""
        from app.config import get_config
        
        if not messagebox.askyesno(
            "确认清空", 
            "确定要清空缓存文件吗？\n\n这将删除缓存目录中的临时文件。\n此操作不可恢复！",
            icon='warning'
        ):
            return
        
        try:
            config = get_config()
            cache_dir = config.cache_dir
            
            # 清空 cache 目录
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                self.logger.info(f"已清空缓存: {cache_dir}")
                messagebox.showinfo("成功", f"缓存已清空！\n\n缓存目录: {cache_dir}")
            else:
                self.logger.warning(f"缓存目录不存在: {cache_dir}")
                messagebox.showinfo("提示", "缓存目录不存在，无需清空。")
        except Exception as e:
            self.logger.error(f"清空缓存失败: {e}", exc_info=True)
            messagebox.showerror("错误", f"清空缓存失败:\n{e}")

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

            # 解绑鼠标滚轮事件
            try:
                self.top_canvas.unbind_all("<MouseWheel>")
            except:
                pass

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
