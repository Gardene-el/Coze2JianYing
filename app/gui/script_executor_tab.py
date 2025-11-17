"""
脚本执行器标签页模块

实现方案三：脚本生成执行
允许用户粘贴或加载从Coze导出的Python脚本，自动注入API依赖并执行
"""
import asyncio
import os
import re
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from types import SimpleNamespace

from app.gui.base_tab import BaseTab
from app.utils.logger import get_logger
from app.utils.draft_path_manager import get_draft_path_manager


class ScriptExecutorTab(BaseTab):
    """脚本执行器标签页
    
    允许执行从Coze导出的Python脚本，自动注入所需的API函数和依赖
    """
    
    def __init__(self, parent: ttk.Notebook, log_callback=None):
        """
        初始化脚本执行器标签页
        
        Args:
            parent: 父Notebook组件
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback
        
        # 执行相关状态（标签页特定）
        self.execution_thread = None
        self.is_executing = False
        
        # 使用全局路径管理器
        self.draft_path_manager = get_draft_path_manager()
        
        # 调用父类初始化
        super().__init__(parent, "脚本执行")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 文件操作区域
        self.file_frame = ttk.LabelFrame(self.frame, text="脚本文件", padding="5")
        
        self.file_label = ttk.Label(self.file_frame, text="脚本文件:")
        self.file_var = tk.StringVar(value="未加载")
        self.file_entry = ttk.Entry(
            self.file_frame, 
            textvariable=self.file_var, 
            state="readonly", 
            width=50
        )
        self.load_file_btn = ttk.Button(
            self.file_frame,
            text="加载文件...",
            command=self._load_script_file
        )
        
        # 输入区域
        self.input_label = ttk.Label(self.frame, text="脚本内容:")
        self.input_text = scrolledtext.ScrolledText(
            self.frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.frame)
        self.execute_btn = ttk.Button(
            self.button_frame,
            text="执行脚本",
            command=self._execute_script
        )
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="清空",
            command=self._clear_input
        )
        self.validate_btn = ttk.Button(
            self.button_frame,
            text="验证脚本",
            command=self._validate_script
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
        # 文件选择区域
        self.file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.file_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.load_file_btn.grid(row=0, column=2)
        self.file_frame.columnconfigure(1, weight=1)
        
        # 输入区域
        self.input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.input_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 按钮区域
        self.button_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态栏
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))
    
    def _load_script_file(self):
        """加载脚本文件"""
        file_path = filedialog.askopenfilename(
            title="选择脚本文件",
            filetypes=[
                ("Python脚本", "*.py"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.file_var.set(file_path)
                self.logger.info(f"已加载脚本文件: {file_path}")
                self.status_var.set(f"已加载: {Path(file_path).name}")
            except Exception as e:
                self.logger.error(f"加载脚本文件失败: {e}", exc_info=True)
                messagebox.showerror("错误", f"加载文件失败:\n{e}")
    
    def _validate_script(self):
        """验证脚本语法"""
        content = self.input_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning("警告", "请输入或加载脚本内容！")
            return
        
        try:
            # 预处理脚本
            processed_script = self._preprocess_script(content)
            
            # 尝试编译（不执行）
            compile(processed_script, '<script>', 'exec')
            
            self.logger.info("脚本语法验证通过")
            messagebox.showinfo("验证成功", "脚本语法验证通过！")
            self.status_var.set("验证通过")
        except SyntaxError as e:
            self.logger.error(f"脚本语法错误: {e}")
            messagebox.showerror("语法错误", f"脚本语法错误:\n行 {e.lineno}: {e.msg}")
        except Exception as e:
            self.logger.error(f"验证失败: {e}", exc_info=True)
            messagebox.showerror("验证失败", f"验证失败:\n{e}")
    
    def _preprocess_script(self, script_content: str) -> str:
        """
        预处理脚本内容，注入必要的导入和依赖
        
        Args:
            script_content: 原始脚本内容
            
        Returns:
            处理后的脚本内容
        """
        # 准备导入语句
        imports = """
# === 自动注入的导入 ===
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent if hasattr(__builtins__, '__file__') else Path.cwd()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入所有API函数
from app.api.draft_routes import (
    create_draft, add_track, add_segment,
    add_global_effect, add_global_filter,
    save_draft, get_draft_status
)

from app.api.segment_routes import (
    create_audio_segment, create_video_segment,
    create_text_segment, create_sticker_segment,
    create_effect_segment, create_filter_segment,
    add_audio_effect, add_audio_fade, add_audio_keyframe,
    add_video_animation, add_video_effect, add_video_fade,
    add_video_filter, add_video_mask, add_video_transition,
    add_video_background_filling, add_video_keyframe,
    add_sticker_keyframe,
    add_text_animation, add_text_bubble, add_text_effect, add_text_keyframe,
    get_segment_detail
)

# 导入所有Request模型
from app.schemas.segment_schemas import (
    # Segment创建请求
    CreateAudioSegmentRequest, CreateVideoSegmentRequest,
    CreateTextSegmentRequest, CreateStickerSegmentRequest,
    CreateEffectSegmentRequest, CreateFilterSegmentRequest,
    # Draft操作请求
    CreateDraftRequest, AddTrackRequest, AddSegmentToDraftRequest,
    AddGlobalEffectRequest, AddGlobalFilterRequest,
    # Segment操作请求
    AddEffectRequest, AddFadeRequest, AddKeyframeRequest,
    AddAnimationRequest, AddFilterRequest, AddMaskRequest,
    AddTransitionRequest, AddBackgroundFillingRequest,
    AddBubbleRequest, AddTextEffectRequest,
    # 辅助模型
    TimeRange, ClipSettings, TextStyle, Position
)

# 兼容CustomNamespace（脚本中可能使用）
CustomNamespace = SimpleNamespace

# === 用户脚本开始 ===
"""
        
        # 移除脚本开头的引号（如果存在）
        script_content = script_content.strip()
        if script_content.startswith('"') and script_content.endswith('"'):
            script_content = script_content[1:-1]
        
        # 将用户脚本包装在async main函数中
        async_main = f"""
async def main():
    \"\"\"自动生成的main函数，包含用户脚本\"\"\"
{self._indent_code(script_content, 4)}

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # 组合完整脚本
        full_script = imports + async_main
        
        return full_script
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """
        为代码添加缩进
        
        Args:
            code: 原始代码
            spaces: 缩进空格数
            
        Returns:
            缩进后的代码
        """
        indent = ' ' * spaces
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def _execute_script(self):
        """执行脚本"""
        # 如果正在执行，提示用户
        if self.is_executing:
            messagebox.showwarning("警告", "正在执行脚本，请稍候...")
            return
        
        content = self.input_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning("警告", "请输入或加载脚本内容！")
            return
        
        self.logger.info("开始执行脚本")
        self.status_var.set("正在执行脚本...")
        self.execute_btn.config(state=tk.DISABLED)
        self.is_executing = True
        
        # 在后台线程中执行脚本
        self.execution_thread = threading.Thread(
            target=self._execute_script_worker,
            args=(content,),
            daemon=True
        )
        self.execution_thread.start()
        
        # 定期检查线程状态
        self._check_execution_status()
    
    def _execute_script_worker(self, script_content: str):
        """后台线程工作函数"""
        try:
            # 预处理脚本
            processed_script = self._preprocess_script(script_content)
            
            # 创建新的事件循环（在新线程中）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 准备执行环境
            exec_globals = {
                '__name__': '__main__',
                '__file__': '<script>',
            }
            
            # 执行脚本（包含asyncio.run(main())）
            exec(processed_script, exec_globals)
            
            loop.close()
            
            # 使用after方法在主线程中更新GUI
            self.frame.after(0, self._on_execution_success)
        except Exception as e:
            # 使用after方法在主线程中更新GUI
            self.frame.after(0, self._on_execution_error, e)
    
    def _check_execution_status(self):
        """定期检查执行状态"""
        if self.execution_thread and self.execution_thread.is_alive():
            # 线程仍在运行，100ms后再次检查
            self.frame.after(100, self._check_execution_status)
        else:
            # 线程已结束
            self.is_executing = False
    
    def _on_execution_success(self):
        """执行成功的回调"""
        self.logger.info("脚本执行成功")
        self.status_var.set("脚本执行成功")
        self.execute_btn.config(state=tk.NORMAL)
        messagebox.showinfo("成功", "脚本执行成功！\n\n草稿已生成到剪映草稿文件夹。")
    
    def _on_execution_error(self, error):
        """执行失败的回调"""
        self.logger.error(f"脚本执行失败: {error}", exc_info=True)
        self.status_var.set("脚本执行失败")
        self.execute_btn.config(state=tk.NORMAL)
        
        # 格式化错误信息
        error_msg = str(error)
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + "..."
        
    
    def cleanup(self):
        """清理标签页资源"""
        super().cleanup()
        # 清理标签页特定的资源
        self.execution_thread = None
