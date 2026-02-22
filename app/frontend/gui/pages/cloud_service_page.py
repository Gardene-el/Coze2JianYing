import tkinter as tk
from tkinter import messagebox
import threading
import time
import socket
import subprocess
import sys
import queue
import atexit
from pathlib import Path
import uvicorn
import customtkinter as ctk

from app.frontend.gui.base_page import BasePage
from app.backend.core.ngrok_manager import NgrokManager
from app.backend.core.settings_manager import get_settings_manager

class CloudServicePage(BasePage):
    """云端服务页面"""

    def __init__(self, parent):
        self.settings = get_settings_manager()
        
        # 服务状态
        self.service_process = None
        self.service_thread = None
        self.uvicorn_server = None
        self.service_running = False
        self.service_port = int(self.settings.get("api_port", "8000"))
        self.log_queue = queue.Queue()
        self.log_reader_thread = None
        self.stop_event = threading.Event()
        
        # ngrok 状态
        self.ngrok_manager = None
        self.ngrok_running = False
        self.ngrok_public_url = None
        
        atexit.register(self._cleanup_on_exit)
        
        super().__init__(parent, "云端服务")

    def _cleanup_on_exit(self):
        try:
            if self.ngrok_running and self.ngrok_manager:
                self.ngrok_manager.stop_tunnel(async_mode=True)
            if self.service_running:
                self._stop_service()
        except:
            pass

    def _create_widgets(self):
        # 说明区域
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            self.info_frame, 
            text="云端服务模式说明", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            self.info_frame,
            text="启动 FastAPI 服务，在 Coze 平台配置\"云侧插件 - 基于已有服务\"。\nCoze 通过 HTTP API 直接调用本服务，无需 cozepy SDK 或 Coze Token。",
            justify="left",
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # 服务管理区域
        self.service_frame = ctk.CTkFrame(self)
        self.service_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.service_frame, 
            text="FastAPI 服务管理", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 端口配置
        config_frame = ctk.CTkFrame(self.service_frame, fg_color="transparent")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(config_frame, text="端口:").pack(side="left", padx=(0, 10))
        self.port_var = ctk.StringVar(value=str(self.service_port))
        self.port_entry = ctk.CTkEntry(config_frame, textvariable=self.port_var, width=100)
        self.port_entry.pack(side="left", padx=(0, 10))
        
        self.check_port_btn = ctk.CTkButton(config_frame, text="检测端口", command=self._check_port_available, width=100)
        self.check_port_btn.pack(side="left")
        
        self.port_status_label = ctk.CTkLabel(config_frame, text="未检测", text_color="gray")
        self.port_status_label.pack(side="left", padx=10)

        # 控制按钮
        control_frame = ctk.CTkFrame(self.service_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_service_btn = ctk.CTkButton(
            control_frame, 
            text="启动服务", 
            command=self._start_service,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_service_btn.pack(side="left", padx=(0, 10))
        
        self.stop_service_btn = ctk.CTkButton(
            control_frame, 
            text="停止服务", 
            command=self._stop_service,
            state="disabled",
            fg_color="red",
            hover_color="darkred"
        )
        self.stop_service_btn.pack(side="left")
        
        self.service_status_label = ctk.CTkLabel(control_frame, text="服务未启动", text_color="gray")
        self.service_status_label.pack(side="left", padx=20)

        # 服务日志
        self.log_textbox = ctk.CTkTextbox(self.service_frame, height=150)
        self.log_textbox.pack(fill="x", padx=10, pady=10)
        self.log_textbox.configure(state="disabled")

        # ngrok 管理区域
        self.ngrok_frame = ctk.CTkFrame(self)
        self.ngrok_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.ngrok_frame, 
            text="ngrok 内网穿透", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # ngrok 配置
        ngrok_config_frame = ctk.CTkFrame(self.ngrok_frame, fg_color="transparent")
        ngrok_config_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ngrok_config_frame, text="Authtoken:").pack(side="left", padx=(0, 10))
        self.ngrok_token_var = ctk.StringVar(value=self.settings.get("ngrok_auth_token", ""))
        self.ngrok_token_entry = ctk.CTkEntry(ngrok_config_frame, textvariable=self.ngrok_token_var, show="*", width=300)
        self.ngrok_token_entry.pack(side="left", padx=(0, 10))
        
        self.show_token_var = ctk.BooleanVar(value=False)
        self.show_token_check = ctk.CTkCheckBox(
            ngrok_config_frame, 
            text="显示", 
            variable=self.show_token_var,
            command=self._toggle_token,
            width=60
        )
        self.show_token_check.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(ngrok_config_frame, text="区域:").pack(side="left", padx=(0, 10))
        self.ngrok_region_var = ctk.StringVar(value=self.settings.get("ngrok_region", "us"))
        self.ngrok_region_menu = ctk.CTkOptionMenu(
            ngrok_config_frame,
            variable=self.ngrok_region_var,
            values=["us", "eu", "ap", "au", "sa", "jp", "in"],
            width=80
        )
        self.ngrok_region_menu.pack(side="left")

        # ngrok 控制
        ngrok_control_frame = ctk.CTkFrame(self.ngrok_frame, fg_color="transparent")
        ngrok_control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_ngrok_btn = ctk.CTkButton(
            ngrok_control_frame, 
            text="启动 ngrok", 
            command=self._start_ngrok,
            state="disabled"
        )
        self.start_ngrok_btn.pack(side="left", padx=(0, 10))
        
        self.stop_ngrok_btn = ctk.CTkButton(
            ngrok_control_frame, 
            text="停止 ngrok", 
            command=self._stop_ngrok,
            state="disabled",
            fg_color="red",
            hover_color="darkred"
        )
        self.stop_ngrok_btn.pack(side="left")
        
        self.ngrok_status_label = ctk.CTkLabel(ngrok_control_frame, text="ngrok 未启动", text_color="gray")
        self.ngrok_status_label.pack(side="left", padx=20)

        # 公网地址
        url_frame = ctk.CTkFrame(self.ngrok_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(url_frame, text="公网地址:").pack(side="left", padx=(0, 10))
        self.ngrok_url_entry = ctk.CTkEntry(url_frame, width=400)
        self.ngrok_url_entry.pack(side="left", padx=(0, 10))
        self.ngrok_url_entry.configure(state="readonly")
        
        self.copy_url_btn = ctk.CTkButton(
            url_frame, 
            text="复制", 
            command=self._copy_ngrok_url,
            width=80,
            state="disabled"
        )
        self.copy_url_btn.pack(side="left")

    def _toggle_token(self):
        if self.show_token_var.get():
            self.ngrok_token_entry.configure(show="")
        else:
            self.ngrok_token_entry.configure(show="*")

    def _append_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _check_port_available(self):
        try:
            port = int(self.port_var.get())
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                self.port_status_label.configure(text="端口可用", text_color="green")
                return True
        except ValueError:
            self.port_status_label.configure(text="无效端口", text_color="red")
            return False
        except OSError:
            self.port_status_label.configure(text="端口被占用", text_color="red")
            return False

    def _start_service(self):
        if self.service_running: return
        
        try:
            port = int(self.port_var.get())
            if not self._check_port_available():
                messagebox.showerror("错误", "端口不可用")
                return
                
            self.service_port = port
            self.settings.set("api_port", str(port))
            
            self._append_log(f"正在启动服务 (端口 {port})...")
            
            # 启动服务逻辑 (复用原有逻辑，简化适配)
            is_frozen = getattr(sys, 'frozen', False)
            if is_frozen:
                self._start_embedded_service(port)
            else:
                self._start_uvicorn_service(port)
                
            self.service_running = True
            self.start_service_btn.configure(state="disabled")
            self.stop_service_btn.configure(state="normal")
            self.start_ngrok_btn.configure(state="normal")
            self.service_status_label.configure(text="服务运行中", text_color="green")
            self.port_entry.configure(state="disabled")
            
            self._start_log_processing()
            
        except Exception as e:
            self.logger.error(f"启动服务失败: {e}")
            messagebox.showerror("错误", f"启动服务失败: {e}")

    def _start_embedded_service(self, port):
        from app.backend.api_main import app
        def run_server():
            config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="info")
            self.uvicorn_server = uvicorn.Server(config)
            self.uvicorn_server.run()
            
        self.service_thread = threading.Thread(target=run_server, daemon=True)
        self.service_thread.start()
        self._append_log("嵌入式服务已启动")

    def _start_uvicorn_service(self, port):
        project_root = Path(__file__).parent.parent.parent.parent.resolve()
        cmd = [sys.executable, "-m", "uvicorn", "app.backend.api_main:app", "--host", "127.0.0.1", "--port", str(port)]
        
        self.service_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, bufsize=1, encoding='utf-8', cwd=str(project_root)
        )
        self._append_log(f"服务进程已启动 PID: {self.service_process.pid}")

    def _stop_service(self):
        if not self.service_running: return
        
        self._append_log("正在停止服务...")
        self.stop_event.set()
        
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        
        if self.service_process:
            self.service_process.terminate()
            try:
                self.service_process.wait(timeout=5)
            except:
                self.service_process.kill()
            self.service_process = None

        if self.ngrok_running:
            self._stop_ngrok()

        self.service_running = False
        self.start_service_btn.configure(state="normal")
        self.stop_service_btn.configure(state="disabled")
        self.start_ngrok_btn.configure(state="disabled")
        self.service_status_label.configure(text="服务已停止", text_color="gray")
        self.port_entry.configure(state="normal")
        self._append_log("服务已停止")

    def _start_log_processing(self):
        if not getattr(sys, 'frozen', False):
            self.log_reader_thread = threading.Thread(target=self._read_process_output, daemon=True)
            self.log_reader_thread.start()
        self._update_log_display()

    def _read_process_output(self):
        if not self.service_process: return
        try:
            for line in iter(self.service_process.stdout.readline, ''):
                if not line: break
                self.log_queue.put(line.strip())
                if self.stop_event.is_set(): break
        except: pass

    def _update_log_display(self):
        try:
            while not self.log_queue.empty():
                self._append_log(self.log_queue.get_nowait())
            if self.service_running:
                self.after(100, self._update_log_display)
        except: pass

    def _start_ngrok(self):
        if not self.service_running: return
        
        token = self.ngrok_token_var.get().strip()
        if not token:
            messagebox.showwarning("提示", "请输入 ngrok Authtoken")
            return
            
        self.settings.set("ngrok_auth_token", token)
        self.settings.set("ngrok_region", self.ngrok_region_var.get())
        
        if not self.ngrok_manager:
            self.ngrok_manager = NgrokManager(logger=self.logger)
            
        def start_thread():
            try:
                url = self.ngrok_manager.start_tunnel(
                    port=self.service_port,
                    authtoken=token,
                    region=self.ngrok_region_var.get()
                )
                if url:
                    self.after(0, lambda: self._on_ngrok_started(url))
                else:
                    self.after(0, lambda: messagebox.showerror("错误", "启动 ngrok 失败"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("错误", str(e)))
                
        threading.Thread(target=start_thread, daemon=True).start()
        self._append_log("正在启动 ngrok...")

    def _on_ngrok_started(self, url):
        self.ngrok_running = True
        self.ngrok_public_url = url
        self.ngrok_url_entry.configure(state="normal")
        self.ngrok_url_entry.delete(0, "end")
        self.ngrok_url_entry.insert(0, url)
        self.ngrok_url_entry.configure(state="readonly")
        
        self.start_ngrok_btn.configure(state="disabled")
        self.stop_ngrok_btn.configure(state="normal")
        self.copy_url_btn.configure(state="normal")
        self.ngrok_status_label.configure(text="ngrok 运行中", text_color="green")
        self._append_log(f"ngrok 已启动: {url}")

    def _stop_ngrok(self):
        if not self.ngrok_running: return
        
        def stop_thread():
            self.ngrok_manager.stop_tunnel()
            self.after(0, self._on_ngrok_stopped)
            
        threading.Thread(target=stop_thread, daemon=True).start()
        self._append_log("正在停止 ngrok...")

    def _on_ngrok_stopped(self):
        self.ngrok_running = False
        self.ngrok_public_url = None
        self.ngrok_url_entry.configure(state="normal")
        self.ngrok_url_entry.delete(0, "end")
        self.ngrok_url_entry.configure(state="readonly")
        
        self.start_ngrok_btn.configure(state="normal")
        self.stop_ngrok_btn.configure(state="disabled")
        self.copy_url_btn.configure(state="disabled")
        self.ngrok_status_label.configure(text="ngrok 已停止", text_color="gray")
        self._append_log("ngrok 已停止")

    def _copy_ngrok_url(self):
        if self.ngrok_public_url:
            self.clipboard_clear()
            self.clipboard_append(self.ngrok_public_url)
            messagebox.showinfo("成功", "已复制到剪贴板")

    def update_settings(self):
        """更新页面设置显示"""
        # 重新从 SettingsManager 读取值
        self.service_port = int(self.settings.get("api_port", "8000"))
        
        # 只有在服务未运行时才更新端口显示，避免干扰
        if not self.service_running:
            self.port_var.set(str(self.service_port))
            
        # 更新 ngrok 设置
        self.ngrok_token_var.set(self.settings.get("ngrok_auth_token", ""))
        self.ngrok_region_var.set(self.settings.get("ngrok_region", "us"))
