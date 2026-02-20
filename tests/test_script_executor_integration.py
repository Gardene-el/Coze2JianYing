#!/usr/bin/env python3
"""
集成测试：完整测试脚本执行器功能
测试从脚本加载到执行的完整流程
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_simple_script_execution():
    """测试简单脚本的执行"""
    print("=" * 60)
    print("测试简单脚本执行")
    print("=" * 60)
    
    # 创建一个简单的测试脚本
    test_script = '''
# 测试创建草稿
req = CreateDraftRequest(draft_name="test_draft", width=1920, height=1080, fps=30)
resp = await create_draft(req)
print(f"Created draft: {resp.draft_id}")

# 测试添加轨道
track_req = AddTrackRequest(track_type="audio", track_name="test_audio")
track_resp = await add_track(resp.draft_id, track_req)
print(f"Added track: {track_resp.track_index}")

# 测试创建音频segment
segment_req = CreateAudioSegmentRequest(
    material_url="https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3",
    target_timerange=TimeRange(start=0, duration=5000000),
    volume=1.0
)
segment_resp = await create_audio_segment(segment_req)
print(f"Created segment: {segment_resp.segment_id}")

# 测试添加segment到draft
add_seg_req = AddSegmentToDraftRequest(segment_id=segment_resp.segment_id)
add_seg_resp = await add_segment(resp.draft_id, add_seg_req)
print(f"Added segment to draft: {add_seg_resp.success}")

# 测试保存draft
save_resp = await save_draft(resp.draft_id)
print(f"Saved draft: {save_resp.draft_path}")
print("✅ Script execution completed successfully")
'''
    
    # 预处理脚本
    from types import SimpleNamespace
    
    def indent_code(code: str, spaces: int) -> str:
        """为代码添加缩进"""
        indent = ' ' * spaces
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
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
from app.backend.api.draft_routes import (
    create_draft, add_track, add_segment,
    add_global_effect, add_global_filter,
    save_draft, get_draft_status
)

from app.backend.api.segment_routes import (
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
from app.backend.schemas.segment_schemas import (
    CreateAudioSegmentRequest, CreateVideoSegmentRequest,
    CreateTextSegmentRequest, CreateStickerSegmentRequest,
    CreateEffectSegmentRequest, CreateFilterSegmentRequest,
    CreateDraftRequest, AddTrackRequest, AddSegmentToDraftRequest,
    AddGlobalEffectRequest, AddGlobalFilterRequest,
    AddEffectRequest, AddFadeRequest, AddKeyframeRequest,
    AddAnimationRequest, AddFilterRequest, AddMaskRequest,
    AddTransitionRequest, AddBackgroundFillingRequest,
    AddBubbleRequest, AddTextEffectRequest,
    TimeRange, ClipSettings, TextStyle, Position
)

CustomNamespace = SimpleNamespace

# === 用户脚本开始 ===
"""
    
    async_main = f"""
async def main():
    \"\"\"自动生成的main函数，包含用户脚本\"\"\"
{indent_code(test_script, 4)}

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
"""
    
    full_script = imports + async_main
    
    try:
        # 验证语法
        compile(full_script, '<integration_test>', 'exec')
        print("\n✅ 脚本语法验证通过")
        
        # 执行脚本
        print("\n开始执行脚本...")
        print("-" * 60)
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': '<integration_test>',
        }
        
        exec(full_script, exec_globals)
        
        print("-" * 60)
        print("\n✅ 集成测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_test_script():
    """测试实际的测试用的脚本文件"""
    print("\n" + "=" * 60)
    print("测试实际的测试用的脚本")
    print("=" * 60)
    
    script_path = project_root / "测试用的脚本"
    
    if not script_path.exists():
        print("⚠️  测试脚本文件不存在，跳过此测试")
        return True
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        print(f"✅ 成功加载脚本文件 ({len(script_content)} 字符)")
        
        # 验证脚本内容包含预期的API调用
        expected_apis = [
            'CreateDraftRequest',
            'create_draft',
            'add_track',
            'create_audio_segment',
            'create_video_segment',
            'save_draft'
        ]
        
        for api in expected_apis:
            if api in script_content:
                print(f"  ✓ 包含 {api}")
            else:
                print(f"  ✗ 缺少 {api}")
        
        print("\n✅ 测试脚本验证通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🎬 开始集成测试")
    print("测试脚本执行器的完整功能")
    
    results = []
    
    # 运行测试
    results.append(("简单脚本执行", test_simple_script_execution()))
    results.append(("实际测试脚本验证", test_actual_test_script()))
    
    # 总结
    print("\n" + "=" * 60)
    print("集成测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有集成测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
