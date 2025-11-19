"""
脚本执行器标签页模块

实现方案三：脚本生成执行
允许用户粘贴或加载从Coze导出的Python脚本，自动注入API依赖并执行
"""

import asyncio
import json
import os
import re
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from types import SimpleNamespace

from app.gui.base_tab import BaseTab
from app.utils.draft_path_manager import get_draft_path_manager
from app.utils.logger import get_logger


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
        super().__init__(parent, "手动草稿生成(新版)")

    def _create_widgets(self):
        """创建UI组件"""
        # 输入区域
        self.input_label = ttk.Label(self.frame, text="脚本内容:")
        self.input_text = scrolledtext.ScrolledText(
            self.frame, height=10, wrap=tk.WORD, font=("Consolas", 9)
        )

        # 按钮区域
        self.button_frame = ttk.Frame(self.frame)
        self.execute_btn = ttk.Button(
            self.button_frame, text="执行脚本", command=self._execute_script
        )
        self.clear_btn = ttk.Button(
            self.button_frame, text="清空", command=self._clear_input
        )
        self.validate_btn = ttk.Button(
            self.button_frame, text="验证脚本", command=self._validate_script
        )
        self.format_btn = ttk.Button(
            self.button_frame, text="格式化输入", command=self._format_input
        )

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )

        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=0)  # 不扩展输入框所在行

    def _setup_layout(self):
        """设置布局"""
        # 输入区域
        self.input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.input_text.grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
        )  # 移除N,S避免垂直拉伸

        # 按钮区域
        self.button_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.format_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 状态栏
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))

    def _format_input(self):
        """格式化输入内容，自动处理从Coze复制的JSON格式"""
        content = self.input_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        try:
            # 尝试提取和格式化脚本
            formatted_script = self._extract_script_from_input(content)
            
            # 替换文本框内容
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", formatted_script)
            
            self.logger.info("输入格式化成功")
            self.status_var.set("格式化成功")
            messagebox.showinfo("成功", "输入已成功格式化！\n\n可以点击'验证脚本'检查语法，或直接'执行脚本'。")
        except Exception as e:
            self.logger.error(f"格式化失败: {e}", exc_info=True)
            messagebox.showerror("格式化失败", f"无法格式化输入内容:\n\n{e}\n\n请确保输入的是有效的Coze输出或Python脚本。")

    def _extract_script_from_input(self, content: str) -> str:
        """
        从输入内容中提取脚本
        支持多种格式：
        1. Coze的JSON输出格式: {"output": "..."}
        2. 纯脚本内容（带literal \n）
        3. 已经格式化的脚本
        
        Args:
            content: 原始输入内容
            
        Returns:
            提取并清理后的脚本内容
        """
        content = content.strip()
        
        # 方式1: 尝试作为JSON解析（Coze的完整输出）
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "output" in data:
                script_content = data["output"]
                self.logger.info("检测到JSON格式输入，提取output字段")
                # 处理literal \n
                script_content = self._decode_escaped_string(script_content)
                return script_content
        except json.JSONDecodeError:
            pass
        
        # 方式2: 检查是否包含literal \n（未转义的换行符字符串）
        if r'\n' in content or '\\n' in content:
            self.logger.info("检测到literal \\n，进行解码")
            # 处理literal \n
            script_content = self._decode_escaped_string(content)
            return script_content
        
        # 方式3: 已经是正常格式的脚本
        self.logger.info("输入已是正常格式")
        return content
    
    def _decode_escaped_string(self, s: str) -> str:
        """
        解码包含literal escape序列的字符串
        
        Args:
            s: 包含literal \n, \t等的字符串
            
        Returns:
            解码后的字符串
        """
        # 处理常见的转义序列
        # 注意：必须按照正确的顺序替换，避免重复替换
        replacements = [
            (r'\n', '\n'),    # 换行
            (r'\t', '\t'),    # 制表符
            (r'\r', '\r'),    # 回车
            (r'\"', '"'),     # 双引号
            (r"\'", "'"),     # 单引号
        ]
        
        result = s
        # 处理转义序列
        for escaped, unescaped in replacements:
            result = result.replace(escaped, unescaped)
        
        # 修复脚本中的常见问题
        result = self._fix_script_issues(result)
            
        return result
    
    def _fix_script_issues(self, script: str) -> str:
        """
        修复脚本中的常见问题
        
        Args:
            script: 脚本内容
            
        Returns:
            修复后的脚本
        """
        lines = script.split('\n')
        fixed_lines = []
        draft_id_var = None
        
        for line in lines:
            # 问题1: 修复draft_变量引用
            # 找到第一次定义draft_id的地方
            if 'draft_id' in line and '=' in line and 'resp_' in line:
                # 例如: draft_af21f036 = resp_af21f036.draft_id
                match = re.search(r'(draft_[\w]+)\s*=\s*resp_[\w]+\.draft_id', line)
                if match:
                    draft_id_var = match.group(1)
                    self.logger.debug(f"Found draft_id variable: {draft_id_var}")
            
            # 替换所有的draft_（不带后缀）为找到的draft_id变量
            if draft_id_var and re.search(r'\bdraft_\b(?![\w])', line):
                line = re.sub(r'\bdraft_\b(?![\w])', draft_id_var, line)
                self.logger.debug(f"Fixed draft_ reference in: {line.strip()}")
            
            # 问题2: 修复空的segment_id
            # 跟踪segment_id变量，类似处理draft_id
            if 'segment_id' in line and '=' in line and 'resp_' in line:
                # 例如: segment_591ab9ac = resp_591ab9ac.segment_id
                match = re.search(r'(segment_[\w]+)\s*=\s*resp_[\w]+\.segment_id', line)
                if match:
                    segment_var = match.group(1)
                    # 查找下一个使用空segment_id的地方，并替换
                    # 这个需要在后续行中查找，我们先记录
                    
            # 问题3: 修复包含错误JSON字符串的行
            # 例如: req_params['target_timerange'] = "{\"duration\":4200000,\"start\":0}"
            # 这种应该是TimeRange对象，不是字符串
            if 'target_timerange' in line and '= "' in line:
                # 尝试提取JSON并转换为TimeRange调用
                # 支持转义和非转义的JSON字符串
                patterns = [
                    r'= "(\\{[^}]+\\})"',  # Escaped: "{\"duration\":...}"
                    r'= "(\{[^}]+\})"',    # Unescaped: "{"duration":...}"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        json_str = match.group(1)
                        # 移除转义字符
                        json_str = json_str.replace('\\"', '"').replace('\\{', '{').replace('\\}', '}')
                        try:
                            import json as json_lib
                            data = json_lib.loads(json_str)
                            # 重构为TimeRange对象
                            params = ', '.join([f"{k}={v}" for k, v in data.items()])
                            line = re.sub(r'= ".*"', f'= TimeRange({params})', line)
                            self.logger.debug(f"Fixed TimeRange JSON string in: {line.strip()}")
                            break
                        except Exception as e:
                            self.logger.debug(f"Failed to parse TimeRange JSON: {e}")
                            pass
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

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
            compile(processed_script, "<script>", "exec")

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

# 添加CropSettings（如果脚本中使用了它）
try:
    from app.schemas.segment_schemas import CropSettings
except ImportError:
    # 如果不存在，创建一个简单的类
    class CropSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# === 用户脚本开始 ===
"""

        # 清理脚本内容
        script_content = script_content.strip()
        
        # 移除脚本开头和结尾的引号（如果存在）
        if script_content.startswith('"') and script_content.endswith('"'):
            script_content = script_content[1:-1]
        elif script_content.startswith("'") and script_content.endswith("'"):
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
        indent = " " * spaces
        lines = code.split("\n")
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return "\n".join(indented_lines)

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
            target=self._execute_script_worker, args=(content,), daemon=True
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
                "__name__": "__main__",
                "__file__": "<script>",
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

        messagebox.showerror(
            "执行失败", f"脚本执行失败:\n\n{error_msg}\n\n详细信息请查看日志。"
        )

    def _clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", tk.END)
        self.logger.info("已清空输入")
        self.status_var.set("已清空")

    def cleanup(self):
        """清理标签页资源"""
        super().cleanup()
        # 清理标签页特定的资源
        self.execution_thread = None
