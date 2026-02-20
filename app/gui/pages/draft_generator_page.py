import os
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from app.gui.base_page import BasePage
from backend.utils.draft_generator import DraftGenerator
from backend.utils.settings_manager import get_settings_manager

class DraftGeneratorPage(BasePage):
    """手动草稿生成页面"""

    def __init__(self, parent):
        self.draft_generator = DraftGenerator()
        self.settings = get_settings_manager()
        self.generation_thread = None
        self.is_generating = False
        
        super().__init__(parent, "手动草稿生成")

    def _create_widgets(self):
        # 标题
        ctk.CTkLabel(
            self, 
            text="手动草稿生成 (旧版)", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self,
            text="在此处粘贴 Coze 插件生成的 JSON 数据",
            text_color="gray"
        ).pack(pady=(0, 20))

        # 输入区域
        self.input_textbox = ctk.CTkTextbox(self, height=300)
        self.input_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 按钮区域
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.generate_btn = ctk.CTkButton(
            btn_frame, 
            text="生成草稿", 
            command=self._generate_draft,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="清空内容", 
            command=self._clear_input,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_btn.pack(side="left", padx=(10, 0), expand=True, fill="x")

        # 状态显示
        self.status_label = ctk.CTkLabel(self, text="就绪", text_color="gray")
        self.status_label.pack(pady=(0, 10))

    def _generate_draft(self):
        if self.is_generating:
            messagebox.showwarning("警告", "正在生成草稿，请稍候...")
            return

        content = self.input_textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        output_folder = self.settings.get_effective_output_path()
        if not os.path.exists(output_folder):
            # 尝试创建
            try:
                os.makedirs(output_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出文件夹:\n{output_folder}\n{e}")
                return

        self.logger.info(f"开始生成草稿，输出文件夹: {output_folder}")
        self.status_label.configure(text="正在生成草稿...", text_color="blue")
        self.generate_btn.configure(state="disabled")
        self.is_generating = True

        self.generation_thread = threading.Thread(
            target=self._generate_draft_worker,
            args=(content, output_folder),
            daemon=True,
        )
        self.generation_thread.start()
        self._check_generation_status()

    def _generate_draft_worker(self, content: str, output_folder: str):
        try:
            draft_paths = self.draft_generator.generate(content, output_folder)
            self.after(0, self._on_generation_success, draft_paths)
        except Exception as e:
            self.after(0, self._on_generation_error, e)

    def _check_generation_status(self):
        if self.generation_thread and self.generation_thread.is_alive():
            self.after(100, self._check_generation_status)
        else:
            self.is_generating = False

    def _on_generation_success(self, draft_paths):
        self.logger.info(f"草稿生成成功: {draft_paths}")
        self.status_label.configure(text="草稿生成成功", text_color="green")
        self.generate_btn.configure(state="normal")
        
        msg = f"成功生成 {len(draft_paths)} 个草稿！\n\n" + "\n".join(draft_paths)
        messagebox.showinfo("成功", msg)

    def _on_generation_error(self, error):
        self.logger.error(f"草稿生成失败: {error}", exc_info=True)
        self.status_label.configure(text="草稿生成失败", text_color="red")
        self.generate_btn.configure(state="normal")
        messagebox.showerror("错误", f"草稿生成失败:\n{error}")

    def _clear_input(self):
        self.input_textbox.delete("1.0", "end")
        self.status_label.configure(text="已清空", text_color="gray")
