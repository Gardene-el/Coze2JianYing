import asyncio
import json
import re
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import customtkinter as ctk

from app.frontend.gui.base_page import BasePage

class ScriptExecutorPage(BasePage):
    """脚本执行页面"""

    def __init__(self, parent):
        self.execution_thread = None
        self.is_executing = False
        
        super().__init__(parent, "脚本执行")

    def _create_widgets(self):
        # 标题
        ctk.CTkLabel(
            self, 
            text="脚本执行 (新版)", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self,
            text="在此处粘贴 Coze 导出的 Python 脚本",
            text_color="gray"
        ).pack(pady=(0, 20))

        # 输入区域
        self.input_textbox = ctk.CTkTextbox(self, height=300, font=("Consolas", 12))
        self.input_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 按钮区域
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.format_btn = ctk.CTkButton(
            btn_frame, 
            text="格式化输入", 
            command=self._format_input,
            width=100
        )
        self.format_btn.pack(side="left", padx=(0, 10))
        
        self.validate_btn = ctk.CTkButton(
            btn_frame, 
            text="验证脚本", 
            command=self._validate_script,
            width=100
        )
        self.validate_btn.pack(side="left", padx=(0, 10))
        
        self.execute_btn = ctk.CTkButton(
            btn_frame, 
            text="执行脚本", 
            command=self._execute_script,
            fg_color="green",
            hover_color="darkgreen",
            width=120
        )
        self.execute_btn.pack(side="left", padx=(0, 10))
        
        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="清空", 
            command=self._clear_input,
            fg_color="gray",
            hover_color="darkgray",
            width=80
        )
        self.clear_btn.pack(side="left")

        # 状态显示
        self.status_label = ctk.CTkLabel(self, text="就绪", text_color="gray")
        self.status_label.pack(pady=(0, 10))

    def _format_input(self):
        content = self.input_textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        try:
            formatted_script = self._extract_script_from_input(content)
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.insert("1.0", formatted_script)
            self.status_label.configure(text="格式化成功", text_color="green")
            messagebox.showinfo("成功", "输入已成功格式化！")
        except Exception as e:
            self.logger.error(f"格式化失败: {e}")
            messagebox.showerror("格式化失败", f"无法格式化输入内容:\n{e}")

    def _extract_script_from_input(self, content: str) -> str:
        content = content.strip()
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "output" in data:
                return self._decode_escaped_string(data["output"])
        except json.JSONDecodeError:
            pass
        
        if r'\n' in content or '\\n' in content:
            return self._decode_escaped_string(content)
            
        return content
    
    def _decode_escaped_string(self, s: str) -> str:
        replacements = [
            (r'\n', '\n'), (r'\t', '\t'), (r'\r', '\r'),
            (r'\"', '"'), (r"\'", "'"),
        ]
        result = s
        for escaped, unescaped in replacements:
            result = result.replace(escaped, unescaped)
        return self._fix_script_issues(result)
    
    def _fix_script_issues(self, script: str) -> str:
        lines = script.split('\n')
        fixed_lines = []
        draft_id_var = None
        
        for line in lines:
            if 'draft_id' in line and '=' in line and 'resp_' in line:
                match = re.search(r'(draft_[\w]+)\s*=\s*resp_[\w]+\.draft_id', line)
                if match:
                    draft_id_var = match.group(1)
            
            if draft_id_var and re.search(r'\bdraft_\b(?![\w])', line):
                line = re.sub(r'\bdraft_\b(?![\w])', draft_id_var, line)
            
            if ('target_timerange' in line or 'timerange' in line) and '= "' in line and ('{' in line or '\\{' in line):
                match = re.search(r'= "(\\?\{[^}]+\\?\})"', line)
                if match:
                    json_str = match.group(1).replace('\\"', '"').replace('\\{', '{').replace('\\}', '}')
                    try:
                        data = json.loads(json_str)
                        params = ', '.join([f"{k}={v}" for k, v in data.items()])
                        line = re.sub(r'= ".*"', f'= TimeRange({params})', line)
                    except: pass
            
            fixed_lines.append(line)
        return '\n'.join(fixed_lines)

    def _validate_script(self):
        content = self.input_textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        try:
            processed_script = self._preprocess_script(content)
            compile(processed_script, "<script>", "exec")
            self.status_label.configure(text="验证通过", text_color="green")
            messagebox.showinfo("成功", "脚本语法验证通过！")
        except SyntaxError as e:
            messagebox.showerror("语法错误", f"行 {e.lineno}: {e.msg}")
        except Exception as e:
            messagebox.showerror("验证失败", str(e))

    def _preprocess_script(self, script_content: str) -> str:
        imports = """
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

project_root = Path(__file__).parent.parent if hasattr(__builtins__, '__file__') else Path.cwd()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.backend.api.easy import *
from app.backend.api.basic import *


CustomNamespace = SimpleNamespace
"""
        script_content = script_content.strip()
        if script_content.startswith('"') and script_content.endswith('"'):
            script_content = script_content[1:-1]
        elif script_content.startswith("'") and script_content.endswith("'"):
            script_content = script_content[1:-1]

        user_imports, user_code = self._extract_imports(script_content)
        if user_imports:
            imports += "\n" + user_imports + "\n"

        async_main = f"""
async def main():
{self._indent_code(user_code, 4)}

if __name__ == "__main__":
    asyncio.run(main())
"""
        return imports + async_main
    
    def _extract_imports(self, script_content: str):
        lines = script_content.split('\n')
        import_lines = []
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append(line)
            elif not stripped or stripped.startswith('#'):
                if not code_lines: import_lines.append(line)
                else: code_lines.append(line)
            else:
                code_lines.append(line)
        return '\n'.join(import_lines), '\n'.join(code_lines)

    def _indent_code(self, code: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join([indent + line if line.strip() else line for line in code.split("\n")])

    def _execute_script(self):
        if self.is_executing: return
        
        content = self.input_textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("警告", "请输入内容！")
            return

        self.status_label.configure(text="正在执行脚本...", text_color="blue")
        self.execute_btn.configure(state="disabled")
        self.is_executing = True

        self.execution_thread = threading.Thread(
            target=self._execute_script_worker, args=(content,), daemon=True
        )
        self.execution_thread.start()
        self._check_execution_status()

    def _execute_script_worker(self, script_content: str):
        try:
            processed_script = self._preprocess_script(script_content)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            exec(processed_script, {"__name__": "__main__", "__file__": "<script>"})
            loop.close()
            self.after(0, self._on_execution_success)
        except Exception as e:
            self.after(0, self._on_execution_error, e)

    def _check_execution_status(self):
        if self.execution_thread and self.execution_thread.is_alive():
            self.after(100, self._check_execution_status)
        else:
            self.is_executing = False

    def _on_execution_success(self):
        self.status_label.configure(text="脚本执行成功", text_color="green")
        self.execute_btn.configure(state="normal")
        messagebox.showinfo("成功", "脚本执行成功！")

    def _on_execution_error(self, error):
        self.logger.error(f"脚本执行失败: {error}", exc_info=True)
        self.status_label.configure(text="脚本执行失败", text_color="red")
        self.execute_btn.configure(state="normal")
        messagebox.showerror("执行失败", f"脚本执行失败:\n{error}")

    def _clear_input(self):
        self.input_textbox.delete("1.0", "end")
        self.status_label.configure(text="已清空", text_color="gray")
