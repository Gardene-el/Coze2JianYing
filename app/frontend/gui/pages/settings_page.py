import customtkinter as ctk
import json
from tkinter import filedialog, messagebox
from app.frontend.gui.base_page import BasePage
from app.backend.core.settings_manager import get_settings_manager

class SettingsPage(BasePage):
    """设置页面"""

    def __init__(self, parent):
        self.settings = get_settings_manager()
        super().__init__(parent, "系统设置")

    def _create_widgets(self):
        # 标题
        ctk.CTkLabel(
            self, 
            text="系统设置", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 30))

        # 设置容器
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # ==================== 路径设置 ====================
        ctk.CTkLabel(
            settings_frame, 
            text="📁 路径设置", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        ctk.CTkLabel(settings_frame, text="剪映草稿文件夹:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        path_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        path_frame.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        self.draft_path_var = ctk.StringVar(value=self.settings.get("draft_folder", ""))
        self.draft_path_entry = ctk.CTkEntry(path_frame, textvariable=self.draft_path_var, width=300)
        self.draft_path_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(path_frame, text="浏览", command=self._select_draft_folder, width=80).pack(side="left", padx=(0, 5))
        ctk.CTkButton(path_frame, text="自动检测", command=self._auto_detect_draft_folder, width=80).pack(side="left")

        # 传输选项
        self.transfer_var = ctk.BooleanVar(value=self.settings.get("transfer_enabled", False))
        ctk.CTkCheckBox(
            settings_frame, 
            text="传输草稿到指定文件夹（启用后草稿将直接保存到剪映草稿文件夹）", 
            variable=self.transfer_var,
            command=self._on_transfer_change
        ).grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # ==================== API 设置 ====================
        ctk.CTkLabel(
            settings_frame, 
            text="🌐 API 设置", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=3, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        ctk.CTkLabel(settings_frame, text="API 端口:").grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.api_port_var = ctk.StringVar(value=self.settings.get("api_port", "20211"))
        self.api_port_entry = ctk.CTkEntry(settings_frame, textvariable=self.api_port_var, width=100)
        self.api_port_entry.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(settings_frame, text="ngrok Authtoken:").grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.ngrok_token_var = ctk.StringVar(value=self.settings.get("ngrok_auth_token", ""))
        self.ngrok_token_entry = ctk.CTkEntry(settings_frame, textvariable=self.ngrok_token_var, width=300, show="*")
        self.ngrok_token_entry.grid(row=5, column=1, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(settings_frame, text="ngrok 区域:").grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.ngrok_region_var = ctk.StringVar(value=self.settings.get("ngrok_region", "us"))
        self.ngrok_region_menu = ctk.CTkOptionMenu(
            settings_frame,
            variable=self.ngrok_region_var,
            values=["us", "eu", "ap", "au", "sa", "jp", "in"],
            width=100
        )
        self.ngrok_region_menu.grid(row=6, column=1, padx=20, pady=10, sticky="w")

        # ==================== 外观设置 ====================
        ctk.CTkLabel(
            settings_frame, 
            text="🎨 外观设置", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=7, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        ctk.CTkLabel(settings_frame, text="主题模式:").grid(row=8, column=0, padx=20, pady=10, sticky="w")
        self.theme_mode_var = ctk.StringVar(value=self.settings.get("theme_mode", "System"))
        self.theme_mode_menu = ctk.CTkOptionMenu(
            settings_frame,
            variable=self.theme_mode_var,
            values=["System", "Dark", "Light"],
            command=self._change_appearance_mode
        )
        self.theme_mode_menu.grid(row=8, column=1, padx=20, pady=10, sticky="w")

        # 按钮区域
        btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        btn_frame.grid(row=9, column=0, columnspan=3, pady=30)

        ctk.CTkButton(
            btn_frame, 
            text="保存设置", 
            command=self._save_settings,
            width=150,
            height=40
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, 
            text="重置默认", 
            command=self._reset_settings,
            width=150,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=10)

        # ==================== 当前配置概览 ====================
        ctk.CTkLabel(
            settings_frame, 
            text="ℹ️ 当前生效配置 (调试信息)", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=10, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        self.config_display = ctk.CTkTextbox(settings_frame, height=150, width=600)
        self.config_display.grid(row=11, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        self.config_display.configure(state="disabled")
        
        # 初始化显示
        self._update_config_display()

    def _update_config_display(self):
        settings_data = self.settings.get_all()
        # 隐藏敏感信息
        display_data = settings_data.copy()
        if display_data.get("ngrok_auth_token"):
            token = display_data["ngrok_auth_token"]
            if len(token) > 8:
                display_data["ngrok_auth_token"] = token[:4] + "..." + token[-4:]
            else:
                display_data["ngrok_auth_token"] = "***"
        
        formatted_json = json.dumps(display_data, indent=4, ensure_ascii=False)
        
        self.config_display.configure(state="normal")
        self.config_display.delete("1.0", "end")
        self.config_display.insert("1.0", formatted_json)
        self.config_display.configure(state="disabled")

    def _select_draft_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.draft_path_var.set(folder)

    def _auto_detect_draft_folder(self):
        path = self.settings.detect_default_draft_folder()
        if path:
            self.draft_path_var.set(path)
            # 自动保存
            self._save_settings(silent=True)
            messagebox.showinfo("成功", f"检测到路径:\n{path}\n\n设置已自动保存。")
        else:
            messagebox.showwarning("失败", "未能自动检测到剪映草稿文件夹")

    def _on_transfer_change(self):
        # 自动保存
        self._save_settings(silent=True)

    def _change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def _save_settings(self, silent=False):
        self.settings.set("draft_folder", self.draft_path_var.get())
        self.settings.set("transfer_enabled", self.transfer_var.get())
        self.settings.set("api_port", self.api_port_var.get())
        self.settings.set("ngrok_auth_token", self.ngrok_token_var.get())
        self.settings.set("ngrok_region", self.ngrok_region_var.get())
        self.settings.set("theme_mode", self.theme_mode_var.get())
        
        self._update_config_display()
        
        if not silent:
            messagebox.showinfo("成功", "设置已保存")

    def _reset_settings(self):
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            defaults = self.settings._get_default_settings()
            self.draft_path_var.set(defaults["draft_folder"])
            self.transfer_var.set(defaults["transfer_enabled"])
            self.api_port_var.set(defaults["api_port"])
            self.ngrok_token_var.set(defaults["ngrok_auth_token"])
            self.ngrok_region_var.set(defaults["ngrok_region"])
            self.theme_mode_var.set(defaults["theme_mode"])
            self._change_appearance_mode(defaults["theme_mode"])
            self._save_settings()
