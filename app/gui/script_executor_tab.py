"""
脚本执行器标签页模块

提供执行脚本的功能，自动注入项目的 API 依赖项
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import asyncio
import threading
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from types import SimpleNamespace

from app.gui.base_tab import BaseTab
from app.utils.logger import get_logger

# 导入所有需要的 API schemas 和函数
from app.schemas.segment_schemas import (
    # Draft 操作
    CreateDraftRequest, CreateDraftResponse,
    AddTrackRequest, AddTrackResponse,
    AddSegmentToDraftRequest, AddSegmentToDraftResponse,
    AddGlobalEffectRequest, AddGlobalEffectResponse,
    AddGlobalFilterRequest, AddGlobalFilterResponse,
    SaveDraftResponse,
    # Segment 创建
    CreateAudioSegmentRequest, CreateVideoSegmentRequest,
    CreateTextSegmentRequest, CreateStickerSegmentRequest,
    CreateEffectSegmentRequest, CreateFilterSegmentRequest,
    CreateSegmentResponse,
    # Segment 操作
    AddEffectRequest, AddEffectResponse,
    AddFadeRequest, AddFadeResponse,
    AddKeyframeRequest, AddKeyframeResponse,
    AddAnimationRequest, AddAnimationResponse,
    AddFilterRequest, AddFilterResponse,
    AddMaskRequest, AddMaskResponse,
    AddTransitionRequest, AddTransitionResponse,
    AddBackgroundFillingRequest, AddBackgroundFillingResponse,
    AddBubbleRequest, AddBubbleResponse,
    AddTextEffectRequest, AddTextEffectResponse,
    # 查询
    DraftStatusResponse, TrackInfo, SegmentInfo, DownloadStatusInfo,
    SegmentDetailResponse,
)

# 导入 API 路由函数
from app.api.draft_routes import (
    create_draft, add_track, add_segment,
    add_global_effect, add_global_filter,
    save_draft, get_draft_status,
)
from app.api.segment_routes import (
    create_audio_segment, create_video_segment,
    create_text_segment, create_sticker_segment,
    create_effect_segment, create_filter_segment,
    add_effect, add_fade, add_keyframe,
    add_animation, add_filter, add_mask,
    add_transition, add_background_filling,
    add_bubble, add_text_effect,
    # Segment 特定函数
    add_audio_fade, add_audio_volume_change,
    add_video_fade, add_video_animation,
    add_video_keyframe, add_video_clip_settings,
    get_segment_detail,
)


class ScriptExecutorTab(BaseTab):
    """脚本执行器标签页
    
    允许用户输入和执行脚本，自动注入 API 依赖项
    """
    
    def __init__(self, parent: ttk.Notebook, log_callback=None):
        """
        初始化脚本执行器标签页
        
        Args:
            parent: 父Notebook组件
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback
        
        # 执行相关状态
        self.execution_thread = None
        self.is_executing = False
        
        # 调用父类初始化
        super().__init__(parent, "脚本执行器")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 顶部工具栏
        self.toolbar_frame = ttk.Frame(self.frame)
        
        self.load_btn = ttk.Button(
            self.toolbar_frame,
            text="加载脚本...",
            command=self._load_script
        )
        self.clear_btn = ttk.Button(
            self.toolbar_frame,
            text="清空",
            command=self._clear_script
        )
        self.execute_btn = ttk.Button(
            self.toolbar_frame,
            text="执行脚本",
            command=self._execute_script,
            style="Accent.TButton"
        )
        
        # 脚本输入区域
        self.script_frame = ttk.LabelFrame(self.frame, text="脚本内容", padding="5")
        
        self.script_text = scrolledtext.ScrolledText(
            self.script_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        
        # 输出区域
        self.output_frame = ttk.LabelFrame(self.frame, text="执行结果", padding="5")
        
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        
        # 配置输出文本标签（不同类型使用不同颜色）
        self.output_text.tag_config("INFO", foreground="black")
        self.output_text.tag_config("SUCCESS", foreground="green")
        self.output_text.tag_config("ERROR", foreground="red")
        self.output_text.tag_config("OUTPUT", foreground="blue")
        
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
        self.frame.rowconfigure(1, weight=2)  # 脚本区域
        self.frame.rowconfigure(2, weight=1)  # 输出区域
    
    def _setup_layout(self):
        """设置布局"""
        # 工具栏
        self.toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 脚本区域
        self.script_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.script_text.pack(fill=tk.BOTH, expand=True)
        
        # 输出区域
        self.output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
    
    def _load_script(self):
        """加载脚本文件"""
        filename = filedialog.askopenfilename(
            title="选择脚本文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("Python文件", "*.py"),
                ("文本文件", "*.txt"),
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.script_text.delete("1.0", tk.END)
                self.script_text.insert("1.0", content)
                
                self.logger.info(f"已加载脚本: {filename}")
                self.status_var.set(f"已加载: {filename}")
                self._append_to_output(f"✓ 已加载脚本: {filename}\n", "SUCCESS")
            except Exception as e:
                self.logger.error(f"加载脚本失败: {e}", exc_info=True)
                messagebox.showerror("错误", f"加载脚本失败:\n{e}")
    
    def _clear_script(self):
        """清空脚本"""
        if self.script_text.get("1.0", tk.END).strip():
            if messagebox.askyesno("确认", "确定要清空脚本内容吗？"):
                self.script_text.delete("1.0", tk.END)
                self.logger.info("已清空脚本")
                self.status_var.set("已清空")
        else:
            self.logger.info("脚本已为空")
    
    def _execute_script(self):
        """执行脚本"""
        # 如果正在执行，提示用户
        if self.is_executing:
            messagebox.showwarning("警告", "正在执行脚本，请稍候...")
            return
        
        script_content = self.script_text.get("1.0", tk.END).strip()
        
        if not script_content:
            messagebox.showwarning("警告", "请输入脚本内容！")
            return
        
        self.logger.info("开始执行脚本")
        self.status_var.set("正在执行...")
        self.execute_btn.config(state=tk.DISABLED)
        self.is_executing = True
        
        # 清空输出
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self._append_to_output("=" * 60 + "\n", "INFO")
        self._append_to_output("开始执行脚本...\n", "INFO")
        self._append_to_output("=" * 60 + "\n", "INFO")
        
        # 在后台线程中执行脚本
        self.execution_thread = threading.Thread(
            target=self._execute_script_worker,
            args=(script_content,),
            daemon=True
        )
        self.execution_thread.start()
        
        # 定期检查线程状态
        self._check_execution_status()
    
    def _execute_script_worker(self, script_content: str):
        """后台线程工作函数"""
        try:
            # 准备执行环境
            global_namespace = self._prepare_execution_namespace()
            
            # 捕获标准输出和错误
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 检查脚本是否包含顶层 await
                has_toplevel_await = 'await ' in script_content
                
                # 在重定向输出的上下文中执行
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    if has_toplevel_await:
                        # 如果有顶层 await，包装成异步函数
                        # 缩进所有代码
                        indented_script = '\n'.join('    ' + line if line.strip() else '' 
                                                   for line in script_content.split('\n'))
                        wrapped_script = f"async def __async_main__():\n{indented_script}\n"
                        
                        # 编译并执行包装后的脚本
                        code = compile(wrapped_script, '<script>', 'exec')
                        exec(code, global_namespace)
                        
                        # 运行异步主函数
                        loop.run_until_complete(global_namespace['__async_main__']())
                    else:
                        # 没有顶层 await，正常执行
                        code = compile(script_content, '<script>', 'exec')
                        exec(code, global_namespace)
                        
                        # 检查是否有定义了 main 协程
                        if 'main' in global_namespace and asyncio.iscoroutinefunction(global_namespace['main']):
                            loop.run_until_complete(global_namespace['main']())
                
                # 获取输出
                stdout_output = stdout_capture.getvalue()
                stderr_output = stderr_capture.getvalue()
                
                # 使用 after 方法在主线程中更新 GUI
                self.frame.after(0, self._on_execution_success, stdout_output, stderr_output, global_namespace)
                
            finally:
                loop.close()
                
        except Exception as e:
            # 使用 after 方法在主线程中更新 GUI
            import traceback
            error_msg = traceback.format_exc()
            self.frame.after(0, self._on_execution_error, error_msg)
    
    def _prepare_execution_namespace(self):
        """准备脚本执行的命名空间，注入所有必要的依赖"""
        namespace = {
            # Python 内置
            '__builtins__': __builtins__,
            'print': print,
            
            # 异步支持
            'asyncio': asyncio,
            
            # SimpleNamespace for CustomNamespace-like objects
            'CustomNamespace': SimpleNamespace,
            
            # Draft 操作请求类
            'CreateDraftRequest': CreateDraftRequest,
            'AddTrackRequest': AddTrackRequest,
            'AddSegmentToDraftRequest': AddSegmentToDraftRequest,
            'AddGlobalEffectRequest': AddGlobalEffectRequest,
            'AddGlobalFilterRequest': AddGlobalFilterRequest,
            
            # Segment 创建请求类
            'CreateAudioSegmentRequest': CreateAudioSegmentRequest,
            'CreateVideoSegmentRequest': CreateVideoSegmentRequest,
            'CreateTextSegmentRequest': CreateTextSegmentRequest,
            'CreateStickerSegmentRequest': CreateStickerSegmentRequest,
            'CreateEffectSegmentRequest': CreateEffectSegmentRequest,
            'CreateFilterSegmentRequest': CreateFilterSegmentRequest,
            
            # Segment 操作请求类
            'AddEffectRequest': AddEffectRequest,
            'AddFadeRequest': AddFadeRequest,
            'AddKeyframeRequest': AddKeyframeRequest,
            'AddAnimationRequest': AddAnimationRequest,
            'AddFilterRequest': AddFilterRequest,
            'AddMaskRequest': AddMaskRequest,
            'AddTransitionRequest': AddTransitionRequest,
            'AddBackgroundFillingRequest': AddBackgroundFillingRequest,
            'AddBubbleRequest': AddBubbleRequest,
            'AddTextEffectRequest': AddTextEffectRequest,
            
            # Draft API 函数
            'create_draft': create_draft,
            'add_track': add_track,
            'add_segment': add_segment,
            'add_global_effect': add_global_effect,
            'add_global_filter': add_global_filter,
            'save_draft': save_draft,
            'get_draft_status': get_draft_status,
            
            # Segment 创建 API 函数
            'create_audio_segment': create_audio_segment,
            'create_video_segment': create_video_segment,
            'create_text_segment': create_text_segment,
            'create_sticker_segment': create_sticker_segment,
            'create_effect_segment': create_effect_segment,
            'create_filter_segment': create_filter_segment,
            
            # Segment 操作 API 函数 (通用)
            'add_effect': add_effect,
            'add_fade': add_fade,
            'add_keyframe': add_keyframe,
            'add_animation': add_animation,
            'add_filter': add_filter,
            'add_mask': add_mask,
            'add_transition': add_transition,
            'add_background_filling': add_background_filling,
            'add_bubble': add_bubble,
            'add_text_effect': add_text_effect,
            
            # Segment 特定操作 API 函数
            'add_audio_fade': add_audio_fade,
            'add_audio_volume_change': add_audio_volume_change,
            'add_video_fade': add_video_fade,
            'add_video_animation': add_video_animation,
            'add_video_keyframe': add_video_keyframe,
            'add_video_clip_settings': add_video_clip_settings,
            
            # 查询 API 函数
            'get_segment_detail': get_segment_detail,
        }
        
        return namespace
    
    def _check_execution_status(self):
        """定期检查执行状态"""
        if self.execution_thread and self.execution_thread.is_alive():
            # 线程仍在运行，100ms 后再次检查
            self.frame.after(100, self._check_execution_status)
        else:
            # 线程已结束
            self.is_executing = False
    
    def _on_execution_success(self, stdout_output: str, stderr_output: str, namespace: dict):
        """执行成功的回调"""
        self.logger.info("脚本执行完成")
        self.status_var.set("执行完成")
        self.execute_btn.config(state=tk.NORMAL)
        
        self._append_to_output("\n" + "=" * 60 + "\n", "INFO")
        self._append_to_output("✓ 脚本执行完成\n", "SUCCESS")
        self._append_to_output("=" * 60 + "\n", "INFO")
        
        # 显示标准输出
        if stdout_output:
            self._append_to_output("\n--- 标准输出 ---\n", "INFO")
            self._append_to_output(stdout_output, "OUTPUT")
        
        # 显示标准错误（如果有）
        if stderr_output:
            self._append_to_output("\n--- 标准错误 ---\n", "INFO")
            self._append_to_output(stderr_output, "ERROR")
        
        # 显示一些有用的变量（如果存在）
        self._append_to_output("\n--- 执行结果 ---\n", "INFO")
        interesting_vars = {k: v for k, v in namespace.items() 
                           if not k.startswith('_') and k not in ['__builtins__', 'asyncio', 'print']}
        
        if interesting_vars:
            for key, value in interesting_vars.items():
                # 只显示简单类型和字符串表示不太长的对象
                value_str = str(value)
                if len(value_str) < 200:
                    self._append_to_output(f"{key} = {value_str}\n", "OUTPUT")
        else:
            self._append_to_output("(无可显示的变量)\n", "INFO")
    
    def _on_execution_error(self, error_msg: str):
        """执行失败的回调"""
        self.logger.error(f"脚本执行失败:\n{error_msg}")
        self.status_var.set("执行失败")
        self.execute_btn.config(state=tk.NORMAL)
        
        self._append_to_output("\n" + "=" * 60 + "\n", "INFO")
        self._append_to_output("✗ 脚本执行失败\n", "ERROR")
        self._append_to_output("=" * 60 + "\n", "INFO")
        self._append_to_output("\n" + error_msg, "ERROR")
        
        messagebox.showerror("执行错误", "脚本执行失败，请查看输出区域了解详情。")
    
    def _append_to_output(self, message: str, tag: str = "INFO"):
        """添加消息到输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message, tag)
        self.output_text.config(state=tk.DISABLED)
        
        # 自动滚动到底部
        self.output_text.see(tk.END)
        
        # 强制更新显示
        self.output_text.update_idletasks()
    
    def cleanup(self):
        """清理标签页资源"""
        super().cleanup()
        # 清理标签页特定的资源
        self.execution_thread = None
