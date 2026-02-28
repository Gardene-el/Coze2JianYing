import os
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from app.frontend.gui.base_page import BasePage
from app.backend.utils.draft_generator import DraftGenerator
from app.backend.utils.settings_manager import get_settings_manager

class DraftGeneratorPage(BasePage):
    """手动草稿生成页面"""

    def __init__(self, parent):
        self.draft_generator = DraftGenerator()
        self.settings = get_settings_manager()
        self.generation_thread = None
        self.is_generating = False
        
        super().__init__(parent, "手动草稿生成")

    def _create_widgets(self):
        # 统一设置字体
        title_font = ctk.CTkFont(family="Microsoft YaHei", size=26, weight="bold")
        label_font = ctk.CTkFont(family="Microsoft YaHei", size=13)
        btn_font = ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold")
        text_font = ctk.CTkFont(family="Consolas", size=14)

        # 主容器框架
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("white", "#2D2D2D"))
        main_frame.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # 1. 顶部区域：标题和说明
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(25, 5))

        ctk.CTkLabel(
            header_frame,
            text="手动草稿生成 (旧版)",
            font=title_font
        ).pack(side="left")

        ctk.CTkLabel(
            main_frame,
            text="在此处粘贴 Coze 插件生成的 JSON 数据",
            text_color="gray",
            font=label_font
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # 2. 底部区域：优先 pack 底部，保证由于文本框扩展不再将底部挤出可视范围
        # 状态显示 (最下面)
        self.status_label = ctk.CTkLabel(main_frame, text="状态: 就绪", text_color="gray", font=label_font)  
        self.status_label.pack(side="bottom", pady=(5, 20))

        # 按钮区域 (倒数第二下)
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=25, pady=(15, 5))

        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="生成草稿",
            command=self._generate_draft,
            height=45,
            corner_radius=8,
            font=btn_font,
            fg_color="#0067C0",
            hover_color="#005A9E"
        )
        self.generate_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="清空内容",
            command=self._clear_input,
            height=45,
            corner_radius=8,
            fg_color=("gray75", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray65", "gray35"),
            font=btn_font
        )
        self.clear_btn.pack(side="left", padx=(10, 0), expand=True, fill="x")   

        # 3. 中间输入区域 (最后 pack，自动占据剩余空间)
        self.input_textbox = ctk.CTkTextbox(
            main_frame, 
            height=300, 
            font=text_font, 
            corner_radius=10,
            fg_color=("white", "#3B3B3B"),
            border_width=1, 
            border_color=("gray70", "gray40")
        )
        self.input_textbox.pack(fill="both", expand=True, padx=25, pady=(0, 0))
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
