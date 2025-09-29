#!/usr/bin/env python3
"""
Practical Example: Complete Video Project With Audio

This demonstrates how add_audios works in a real-world scenario,
similar to how add_images was used in issue #16.
"""

import sys
import os
import json

# Add project root to sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Create mock runtime module for testing
import types
runtime_module = types.ModuleType('runtime')
runtime_module.Args = lambda input_data: type('Args', (), {'input': input_data, 'logger': None})()
sys.modules['runtime'] = runtime_module

# Import handlers
from tools.create_draft.handler import handler as create_draft, Input as CreateInput
from tools.add_images.handler import handler as add_images, Input as ImagesInput  
from tools.add_audios.handler import handler as add_audios, Input as AudiosInput
from tools.export_drafts.handler import handler as export_drafts, Input as ExportInput


def create_complete_video_project():
    """Create a complete video project with both images and audio"""
    print("=== 创建完整的视频项目 ===")
    print("演示：图片 + 音频的完整工作流")
    
    # 1. 创建项目草稿
    print("\n1. 创建视频项目草稿...")
    draft_result = create_draft(runtime_module.Args(CreateInput(
        draft_name="完整视频项目演示",
        width=1920,
        height=1080,
        fps=30,
        video_quality="1080p",
        audio_quality="320k"
    )))
    
    if not draft_result.success:
        print(f"❌ 创建草稿失败: {draft_result.message}")
        return False
    
    draft_id = draft_result.draft_id
    print(f"✅ 草稿创建成功! ID: {draft_id}")
    
    # 2. 添加图片序列 (类似原始issue示例)
    print("\n2. 添加图片序列...")
    image_sequence = [
        {
            "image_url": "https://s.coze.cn/t/intro-scene.jpg",
            "start": 0,
            "end": 4000,  # 4秒
            "width": 1920,
            "height": 1080,
            "in_animation": "轻微放大",
            "in_animation_duration": 500
        },
        {
            "image_url": "https://s.coze.cn/t/main-content-1.jpg", 
            "start": 4000,
            "end": 12000,  # 8秒
            "width": 1920,
            "height": 1080,
            "filter_type": "暖冬",
            "filter_intensity": 0.6
        },
        {
            "image_url": "https://s.coze.cn/t/main-content-2.jpg",
            "start": 12000,
            "end": 20000,  # 8秒
            "width": 1920,
            "height": 1080,
            "in_animation": "轻微缩放",
            "in_animation_duration": 800
        },
        {
            "image_url": "https://s.coze.cn/t/conclusion.jpg",
            "start": 20000,
            "end": 25000,  # 5秒
            "width": 1920,
            "height": 1080,
            "outro_animation": "淡出",
            "outro_animation_duration": 1000
        }
    ]
    
    images_result = add_images(runtime_module.Args(ImagesInput(
        draft_id=draft_id,
        image_infos=image_sequence  # Note: add_images uses image_infos parameter
    )))
    
    if not images_result.success:
        print(f"❌ 添加图片失败: {images_result.message}")
        return False
    
    print(f"✅ 添加了 {len(images_result.segment_ids)} 个图片片段")
    
    # 3. 添加背景音乐轨道
    print("\n3. 添加背景音乐轨道...")
    background_music = [
        {
            "audio_url": "https://example.com/gentle_piano_background.mp3",
            "start": 0,
            "end": 25000,  # 覆盖整个视频
            "volume": 0.4,  # 低音量作为背景
            "fade_in": 2000,
            "fade_out": 3000,
            "effect_type": "reverb",
            "effect_intensity": 0.2
        }
    ]
    
    bg_music_result = add_audios(runtime_module.Args(AudiosInput(
        draft_id=draft_id,
        audio_infos=background_music
    )))
    
    if not bg_music_result.success:
        print(f"❌ 添加背景音乐失败: {bg_music_result.message}")
        return False
    
    print(f"✅ 背景音乐添加成功! 片段ID: {bg_music_result.segment_ids[0]}")
    
    # 4. 添加旁白轨道  
    print("\n4. 添加旁白轨道...")
    narration_track = [
        {
            "audio_url": "https://example.com/intro_narration.wav",
            "start": 1000,   # 1秒后开始
            "end": 5000,     # 持续4秒
            "volume": 1.0,
            "fade_in": 300,
            "fade_out": 300
        },
        {
            "audio_url": "https://example.com/main_explanation.wav", 
            "start": 6000,   # 6秒开始
            "end": 18000,    # 持续12秒
            "volume": 1.1,
            "speed": 0.95,   # 稍慢语速
            "material_start": 500,  # 跳过原音频前0.5秒
            "material_end": 12500
        },
        {
            "audio_url": "https://example.com/conclusion_narration.wav",
            "start": 21000,  # 21秒开始
            "end": 24000,    # 持续3秒
            "volume": 1.0,
            "fade_in": 200,
            "fade_out": 500
        }
    ]
    
    narration_result = add_audios(runtime_module.Args(AudiosInput(
        draft_id=draft_id,
        audio_infos=narration_track
    )))
    
    if not narration_result.success:
        print(f"❌ 添加旁白失败: {narration_result.message}")
        return False
    
    print(f"✅ 旁白轨道添加成功! 片段数量: {len(narration_result.segment_ids)}")
    
    # 5. 添加音效轨道
    print("\n5. 添加音效轨道...")
    sound_effects = [
        {
            "audio_url": "https://example.com/transition_whoosh.wav",
            "start": 3800,   # 第一个转场前
            "end": 4200,     # 0.4秒音效
            "volume": 0.8,
            "effect_type": "echo",
            "effect_intensity": 0.5
        },
        {
            "audio_url": "https://example.com/attention_ding.wav",
            "start": 11800,  # 第二个转场前
            "end": 12200,    # 0.4秒音效
            "volume": 0.9
        },
        {
            "audio_url": "https://example.com/final_chime.wav",
            "start": 24000,  # 结尾处
            "end": 25000,    # 1秒音效
            "volume": 0.7,
            "fade_out": 500
        }
    ]
    
    effects_result = add_audios(runtime_module.Args(AudiosInput(
        draft_id=draft_id,
        audio_infos=sound_effects
    )))
    
    if not effects_result.success:
        print(f"❌ 添加音效失败: {effects_result.message}")
        return False
    
    print(f"✅ 音效轨道添加成功! 片段数量: {len(effects_result.segment_ids)}")
    
    # 6. 导出并分析最终项目结构
    print("\n6. 导出并分析项目结构...")
    export_result = export_drafts(runtime_module.Args(ExportInput(
        draft_ids=[draft_id]
    )))
    
    if not export_result.success:
        print(f"❌ 导出失败: {export_result.message}")
        return False
    
    # 分析项目结构
    project_data = json.loads(export_result.draft_data)
    draft = project_data["drafts"][0]
    
    image_tracks = [t for t in draft["tracks"] if t["track_type"] == "image"]
    audio_tracks = [t for t in draft["tracks"] if t["track_type"] == "audio"]
    
    total_image_segments = sum(len(t["segments"]) for t in image_tracks)
    total_audio_segments = sum(len(t["segments"]) for t in audio_tracks)
    
    print("\n✅ 项目创建完成!")
    print("=" * 50)
    print(f"项目名称: {draft['project']['name']}")
    print(f"项目分辨率: {draft['project']['width']}x{draft['project']['height']}")
    print(f"帧率: {draft['project']['fps']} fps")
    print()
    print("轨道统计:")
    print(f"  📸 图片轨道: {len(image_tracks)} 个")
    print(f"  🎵 音频轨道: {len(audio_tracks)} 个")
    print()
    print("片段统计:")
    print(f"  📸 图片片段总数: {total_image_segments}")
    print(f"  🎵 音频片段总数: {total_audio_segments}")
    print()
    print("音频轨道详情:")
    for i, track in enumerate(audio_tracks, 1):
        print(f"  轨道 {i}: {len(track['segments'])} 个音频片段")
        for j, segment in enumerate(track["segments"], 1):
            start_sec = segment["time_range"]["start"] / 1000
            end_sec = segment["time_range"]["end"] / 1000
            duration = (segment["time_range"]["end"] - segment["time_range"]["start"]) / 1000
            volume = segment["audio"]["volume"]
            print(f"    片段 {j}: {start_sec:.1f}s - {end_sec:.1f}s ({duration:.1f}s), 音量: {volume}")
    
    return True


def demonstrate_json_string_format():
    """Demonstrate the exact JSON string format like in the original issue"""
    print("\n\n=== JSON字符串格式演示 ===")
    print("演示类似原始issue #16的JSON字符串输入格式")
    
    # Create draft
    draft_result = create_draft(runtime_module.Args(CreateInput(
        draft_name="JSON格式演示项目"
    )))
    draft_id = draft_result.draft_id
    
    # Use JSON string format exactly like the original add_images issue
    audio_json_string = '[{"audio_url":"https://example.com/track1.mp3","start":0,"end":15000,"volume":0.8,"fade_in":1000,"fade_out":1000},{"audio_url":"https://example.com/track2.wav","start":15000,"end":30000,"volume":0.7,"effect_type":"reverb","effect_intensity":0.5},{"audio_url":"https://example.com/track3.aac","start":30000,"end":45000,"volume":0.9,"speed":1.05,"material_start":2000,"material_end":17000}]'
    
    print("\n输入格式示例:")
    print(f'audio_infos = "{audio_json_string[:80]}..."')
    
    result = add_audios(runtime_module.Args(AudiosInput(
        draft_id=draft_id,
        audio_infos=audio_json_string
    )))
    
    if not result.success:
        print(f"❌ JSON字符串处理失败: {result.message}")
        return False
    
    print("\n输出格式:")
    output = {
        "segment_ids": result.segment_ids,
        "segment_infos": result.segment_infos,
        "success": result.success,
        "message": result.message
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))
    
    print("\n✅ JSON字符串格式演示完成!")
    print("说明: add_audios完全支持与add_images相同的JSON字符串输入格式")
    
    return True


def main():
    """Run practical examples"""
    print("🎬 Add Audios 实用示例演示")
    print("基于add_images (issue #16) 的设计模式")
    
    examples = [
        create_complete_video_project,
        demonstrate_json_string_format
    ]
    
    results = []
    for example in examples:
        try:
            results.append(example())
        except Exception as e:
            print(f"❌ 示例 {example.__name__} 出错: {e}")
            results.append(False)
    
    print(f"\n=== 实用示例总结 ===")
    print(f"成功示例: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 所有实用示例都成功完成!")
        print("\n📝 总结:")
        print("✅ add_audios 工具完全遵循 add_images 的设计模式")
        print("✅ 支持相同的JSON字符串和数组对象输入格式")
        print("✅ 提供了丰富的音频处理参数和特效控制")
        print("✅ 与现有工具(create_draft, export_drafts)完美集成")
        print("✅ 支持多轨道音频的复杂项目需求")
        
        print("\n🚀 add_audios 工具已准备好在 Coze 平台上使用!")
        return True
    else:
        print("❌ 部分示例失败!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)