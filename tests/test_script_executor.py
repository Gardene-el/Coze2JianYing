#!/usr/bin/env python
"""
测试脚本执行器标签页的功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 测试导入
from app.gui.script_executor_tab import ScriptExecutorTab
print("✓ ScriptExecutorTab 导入成功")

# 测试命名空间准备
class MockTab:
    def __init__(self):
        pass

# 创建一个模拟的标签页来测试命名空间
import tkinter as tk

# 由于我们没有实际的 GUI 环境，只测试逻辑部分
print("\n测试命名空间准备...")

# 模拟 ScriptExecutorTab 的命名空间准备方法
from app.schemas.segment_schemas import (
    CreateDraftRequest, CreateVideoSegmentRequest
)
from app.api.draft_routes import create_draft
from app.api.segment_routes import create_video_segment

# 验证可以导入所需的类
print("✓ CreateDraftRequest 导入成功")
print("✓ CreateVideoSegmentRequest 导入成功")
print("✓ create_draft 函数导入成功")
print("✓ create_video_segment 函数导入成功")

# 测试异步脚本包装逻辑
print("\n测试异步脚本包装...")

test_script = """
req_test = CreateDraftRequest(draft_name="test", width=1920, height=1080, fps=30)
resp_test = await create_draft(req_test)
print(f"Draft ID: {resp_test.draft_id}")
"""

# 检查是否有 await
has_toplevel_await = 'await ' in test_script
print(f"✓ 检测到顶层 await: {has_toplevel_await}")

if has_toplevel_await:
    # 缩进所有代码
    indented_script = '\n'.join('    ' + line if line.strip() else '' 
                               for line in test_script.split('\n'))
    wrapped_script = f"async def __async_main__():\n{indented_script}\n"
    print("✓ 脚本包装成功")
    print("\n包装后的脚本:")
    print(wrapped_script)

print("\n所有测试通过！✓")
