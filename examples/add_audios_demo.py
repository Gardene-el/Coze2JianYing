#!/usr/bin/env python3
"""
Add Audios Tool Demonstration

This script demonstrates the add_audios tool functionality with realistic examples,
showing how to add various types of audio segments to a draft.
"""

import sys
import os
import json
import uuid

# Add project root to sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Create mock runtime module for testing
class MockRuntime:
    class Args:
        def __init__(self, input_data):
            self.input = input_data
        
        def logger(self):
            return None

# Add mock to sys.modules
import types
runtime_module = types.ModuleType('runtime')
runtime_module.Args = MockRuntime.Args
sys.modules['runtime'] = runtime_module

# Import handlers
from tools.create_draft.handler import handler as create_draft_handler, Input as CreateDraftInput
from tools.add_audios.handler import handler as add_audios_handler, Input as AddAudiosInput
from tools.export_drafts.handler import handler as export_drafts_handler, Input as ExportDraftsInput


class MockArgs:
    """Mock Args class for testing"""
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def demonstrate_basic_usage():
    """Demonstrate basic add_audios usage"""
    print("=== 基本用法演示 ===")
    
    # 1. 创建草稿
    print("1. 创建新草稿...")
    create_input = CreateDraftInput(
        draft_name="音频演示项目",
        width=1920,
        height=1080,
        fps=30,
        video_quality="1080p",
        audio_quality="320k"
    )
    
    create_result = create_draft_handler(MockArgs(create_input))
    if not create_result.success:
        print(f"❌ 草稿创建失败: {create_result.message}")
        return False
    
    draft_id = create_result.draft_id
    print(f"✅ 草稿创建成功! ID: {draft_id}")
    
    # 2. 添加背景音乐
    print("2. 添加背景音乐...")
    background_music = [{
        "audio_url": "https://example.com/background_music.mp3",
        "start": 0,
        "end": 60000,  # 60秒
        "volume": 0.6,  # 较低音量作为背景
        "fade_in": 2000,  # 2秒淡入
        "fade_out": 3000,  # 3秒淡出
        "effect_type": "reverb",
        "effect_intensity": 0.3
    }]
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=background_music
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if not result.success:
        print(f"❌ 背景音乐添加失败: {result.message}")
        return False
    
    print(f"✅ 背景音乐添加成功! 片段ID: {result.segment_ids[0]}")
    
    # 3. 添加音效
    print("3. 添加音效...")
    sound_effects = [
        {
            "audio_url": "https://example.com/applause.wav",
            "start": 15000,  # 15秒处开始
            "end": 20000,    # 持续5秒
            "volume": 1.0,
            "effect_type": "echo",
            "effect_intensity": 0.7
        },
        {
            "audio_url": "https://example.com/transition.wav",
            "start": 30000,  # 30秒处
            "end": 32000,    # 持续2秒
            "volume": 0.8,
            "fade_in": 100,
            "fade_out": 100
        }
    ]
    
    effects_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=sound_effects
    )
    
    result = add_audios_handler(MockArgs(effects_input))
    if not result.success:
        print(f"❌ 音效添加失败: {result.message}")
        return False
    
    print(f"✅ 音效添加成功! 片段数量: {len(result.segment_ids)}")
    
    # 4. 添加旁白
    print("4. 添加旁白...")
    narration = [{
        "audio_url": "https://example.com/narration.m4a",
        "start": 5000,   # 5秒处开始
        "end": 45000,    # 到45秒结束
        "volume": 1.2,   # 稍高音量确保清晰
        "fade_in": 500,
        "fade_out": 1000,
        "speed": 0.95,   # 稍慢语速
        "material_start": 2000,  # 从原音频2秒处开始
        "material_end": 42000    # 到原音频42秒处结束
    }]
    
    narration_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=narration
    )
    
    result = add_audios_handler(MockArgs(narration_input))
    if not result.success:
        print(f"❌ 旁白添加失败: {result.message}")
        return False
    
    print(f"✅ 旁白添加成功! 片段ID: {result.segment_ids[0]}")
    
    # 5. 导出查看结果
    print("5. 导出草稿查看结果...")
    export_input = ExportDraftsInput(draft_ids=[draft_id])
    export_result = export_drafts_handler(MockArgs(export_input))
    
    if not export_result.success:
        print(f"❌ 导出失败: {export_result.message}")
        return False
    
    # 分析导出结果
    exported_data = json.loads(export_result.draft_data)
    draft_data = exported_data["drafts"][0]
    
    audio_tracks = [track for track in draft_data["tracks"] if track["track_type"] == "audio"]
    total_segments = sum(len(track["segments"]) for track in audio_tracks)
    
    print(f"✅ 导出成功!")
    print(f"   - 音频轨道数量: {len(audio_tracks)}")
    print(f"   - 音频片段总数: {total_segments}")
    print(f"   - 项目总时长: {draft_data.get('total_duration_ms', 0)}ms")
    
    return True


def demonstrate_json_string_input():
    """Demonstrate using JSON string input (similar to the original add_images example)"""
    print("\n=== JSON字符串输入演示 ===")
    
    # 创建草稿
    create_input = CreateDraftInput(draft_name="JSON演示项目")
    create_result = create_draft_handler(MockArgs(create_input))
    draft_id = create_result.draft_id
    
    # 使用JSON字符串格式（类似原始add_images示例）
    json_input = '[{"audio_url":"https://example.com/music1.mp3","start":0,"end":15000,"volume":0.8,"fade_in":1000,"fade_out":1000},{"audio_url":"https://example.com/music2.wav","start":15000,"end":30000,"volume":0.7,"effect_type":"reverb","effect_intensity":0.4},{"audio_url":"https://example.com/music3.aac","start":30000,"end":45000,"volume":0.9,"speed":1.1}]'
    
    print("输入示例:")
    print(f'audio_infos = "{json_input[:100]}..."')
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=json_input
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if not result.success:
        print(f"❌ JSON字符串输入失败: {result.message}")
        return False
    
    print("输出示例:")
    output_dict = {
        "segment_ids": result.segment_ids,
        "segment_infos": result.segment_infos,
        "success": result.success,
        "message": result.message
    }
    
    print(json.dumps(output_dict, ensure_ascii=False, indent=2))
    
    print("✅ JSON字符串输入演示成功!")
    return True


def demonstrate_advanced_features():
    """Demonstrate advanced audio features"""
    print("\n=== 高级功能演示 ===")
    
    # 创建草稿
    create_input = CreateDraftInput(draft_name="高级音频功能演示")
    create_result = create_draft_handler(MockArgs(create_input))
    draft_id = create_result.draft_id
    
    # 展示高级音频参数
    advanced_audio = [
        {
            "audio_url": "https://example.com/complex_audio.wav",
            "start": 0,
            "end": 30000,
            "volume": 1.0,
            "fade_in": 2000,
            "fade_out": 2000,
            "effect_type": "chorus",
            "effect_intensity": 0.6,
            "speed": 1.05,
            "material_start": 5000,  # 音频裁剪
            "material_end": 35000
        },
        {
            "audio_url": "https://example.com/layered_sound.mp3",
            "start": 10000,
            "end": 25000,
            "volume": 0.7,
            "effect_type": "flanger",
            "effect_intensity": 0.8,
            "speed": 0.9
        }
    ]
    
    add_input = AddAudiosInput(
        draft_id=draft_id,
        audio_infos=advanced_audio
    )
    
    result = add_audios_handler(MockArgs(add_input))
    if not result.success:
        print(f"❌ 高级功能演示失败: {result.message}")
        return False
    
    print("✅ 高级功能演示成功!")
    print("支持的高级功能:")
    print("  - 音频裁剪 (material_start/end)")
    print("  - 播放速度调节 (speed)")
    print("  - 多种音频特效 (effect_type)")
    print("  - 特效强度控制 (effect_intensity)")
    print("  - 精确的淡入淡出控制")
    
    return True


def main():
    """运行所有演示"""
    print("🎵 Add Audios Tool 功能演示\n")
    
    demonstrations = [
        demonstrate_basic_usage,
        demonstrate_json_string_input,
        demonstrate_advanced_features
    ]
    
    results = []
    for demo in demonstrations:
        try:
            results.append(demo())
        except Exception as e:
            print(f"❌ 演示 {demo.__name__} 出错: {e}")
            results.append(False)
    
    print(f"\n=== 演示总结 ===")
    print(f"成功演示: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 所有演示都成功完成!")
        print("\nadd_audios 工具已准备就绪，具备以下功能:")
        print("✅ 多种音频格式支持 (MP3, WAV, AAC, M4A)")
        print("✅ 灵活的输入格式 (数组对象, JSON字符串)")
        print("✅ 丰富的音频参数控制")
        print("✅ 音频特效和速度调节")
        print("✅ 音频裁剪和时间轴管理")
        print("✅ 多轨道音频支持")
        print("✅ 完整的错误处理和验证")
        
        return True
    else:
        print("❌ 部分演示失败!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)