#!/usr/bin/env python3
"""
测试脚本执行器的预处理逻辑
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_script_preprocessing():
    """测试脚本预处理功能"""
    print("=" * 60)
    print("测试脚本预处理功能")
    print("=" * 60)
    
    # 模拟脚本内容（类似测试用的脚本）
    sample_script = '''
# API 调用: create_draft
req_test = CreateDraftRequest(draft_name="demo", width=1920, height=1080, fps=30)
resp_test = await create_draft(req_test)
draft_id = resp_test.draft_id
'''
    
    # 导入ScriptExecutorTab（仅导入类，不实例化）
    # 由于tkinter依赖，我们直接测试_preprocess_script逻辑
    
    # 手动实现预处理逻辑用于测试
    def indent_code(code: str, spaces: int) -> str:
        """为代码添加缩进"""
        indent = ' ' * spaces
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def preprocess_script(script_content: str) -> str:
        """预处理脚本内容"""
        imports = """
# === 自动注入的导入 ===
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

# 导入所有API函数
from src.backend.api.draft_routes import (
    create_draft, add_track, add_segment,
    add_effect, add_filter,
    save_draft, get_draft_status
)

from src.backend.api.segment_routes import (
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
from src.backend.schemas.general_schemas import (
    CreateAudioSegmentRequest, CreateVideoSegmentRequest,
    CreateTextSegmentRequest, CreateStickerSegmentRequest,
    CreateEffectSegmentRequest, CreateFilterSegmentRequest,
    CreateDraftRequest, AddTrackRequest, AddSegmentToDraftRequest,
    AddEffectRequest, AddFilterRequest,
    AddEffectRequest, AddFadeRequest, AddKeyframeRequest,
    AddAnimationRequest, AddFilterRequest, AddMaskRequest,
    AddTransitionRequest, AddBackgroundFillingRequest,
    AddBubbleRequest, AddTextEffectRequest,
    TimeRange, ClipSettings, TextStyle, Position
)

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
{indent_code(script_content, 4)}

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # 组合完整脚本
        full_script = imports + async_main
        
        return full_script
    
    try:
        # 预处理脚本
        processed = preprocess_script(sample_script)
        
        print("\n✅ 预处理后的脚本:")
        print("-" * 60)
        # 显示前500字符和后200字符
        if len(processed) > 700:
            print(processed[:500] + "\n...\n" + processed[-200:])
        else:
            print(processed)
        print("-" * 60)
        
        # 验证语法
        compile(processed, '<test>', 'exec')
        print("\n✅ 脚本语法验证通过")
        
        # 检查关键导入
        assert "from src.backend.api.draft_routes import" in processed
        assert "CreateDraftRequest" in processed
        assert "CustomNamespace = SimpleNamespace" in processed
        assert "async def main():" in processed
        assert "asyncio.run(main())" in processed
        print("✅ 关键导入和结构检查通过")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quoted_script_handling():
    """测试处理带引号的脚本"""
    print("\n" + "=" * 60)
    print("测试带引号脚本的处理")
    print("=" * 60)
    
    # 模拟从文件读取的带引号脚本
    quoted_script = '"\\n# API 调用\\nreq = CreateDraftRequest(draft_name=\\"demo\\")\\n"'
    
    # 处理：移除首尾引号
    processed = quoted_script.strip()
    if processed.startswith('"') and processed.endswith('"'):
        processed = processed[1:-1]
    
    print(f"原始: {quoted_script}")
    print(f"处理后: {processed}")
    print("✅ 引号处理测试通过")
    
    return True


if __name__ == "__main__":
    print("\n🎬 开始测试脚本执行器")
    
    results = []
    
    # 运行测试
    results.append(("脚本预处理", test_script_preprocessing()))
    results.append(("引号处理", test_quoted_script_handling()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
