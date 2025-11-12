#!/usr/bin/env python
"""
测试脚本执行器的核心逻辑（不需要 tkinter）
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("测试脚本执行器核心逻辑")
print("=" * 60)

# 测试导入所需的类和函数
print("\n1. 测试导入 API schemas...")
try:
    from app.schemas.segment_schemas import (
        CreateDraftRequest, CreateVideoSegmentRequest,
        AddTrackRequest, CreateAudioSegmentRequest
    )
    print("✓ API schemas 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试导入 API 函数
print("\n2. 测试导入 API 函数...")
try:
    from app.api.draft_routes import (
        create_draft, add_track, save_draft
    )
    from app.api.segment_routes import (
        create_video_segment, create_audio_segment
    )
    print("✓ API 函数导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试异步脚本包装逻辑
print("\n3. 测试异步脚本包装逻辑...")

test_script = """
req_test = CreateDraftRequest(draft_name="test", width=1920, height=1080, fps=30)
resp_test = await create_draft(req_test)
print(f"Draft ID: {resp_test.draft_id}")
"""

# 检查是否有 await
has_toplevel_await = 'await ' in test_script
print(f"   检测到顶层 await: {has_toplevel_await}")

if has_toplevel_await:
    # 缩进所有代码
    indented_script = '\n'.join('    ' + line if line.strip() else '' 
                               for line in test_script.split('\n'))
    wrapped_script = f"async def __async_main__():\n{indented_script}\n"
    print("✓ 脚本包装成功")
    print("\n   包装后的脚本:")
    for line in wrapped_script.split('\n')[:5]:  # 只显示前5行
        print(f"   {line}")

# 测试创建请求对象
print("\n4. 测试创建请求对象...")
try:
    req = CreateDraftRequest(
        draft_name="test_draft",
        width=1920,
        height=1080,
        fps=30
    )
    print(f"✓ CreateDraftRequest 创建成功: {req.draft_name}")
    
    req2 = AddTrackRequest(
        track_type="audio",
        track_name=None
    )
    print(f"✓ AddTrackRequest 创建成功: {req2.track_type}")
except Exception as e:
    print(f"✗ 创建失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("所有测试通过！✓")
print("=" * 60)
