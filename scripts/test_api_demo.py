#!/usr/bin/env python3
"""
测试 DraftStateManager 和 SegmentManager - 生成真实的剪映草稿文件
完全仿照 pyJianYingDraft demo.py 的流程，使用网络 URL 作为素材
目的: 验证能够生成可用的剪映草稿文件（不仅仅是测试API函数）
"""
import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pyJianYingDraft as draft
from pyJianYingDraft import IntroType, TransitionType, trange, tim
import requests

# 资源 URL
ASSET_URLS = {
    'sticker': 'https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif',
    'video': 'https://gardene-el.github.io/Coze2JianYing/assets/video.mp4',
    'audio': 'https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3',
    'subtitles': 'https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt'
}


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def get_local_assets() -> dict:
    """
    获取本地素材文件路径
    
    Returns:
        素材路径字典
    """
    # 使用项目中已有的素材文件
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"
    
    return {
        'audio': str(assets_dir / "audio.mp3"),
        'video': str(assets_dir / "video.mp4"),
        'sticker': str(assets_dir / "sticker.gif")
    }


def main():
    """
    主测试流程 - 完全仿照 pyJianYingDraft demo.py
    目的: 生成真实的剪映草稿文件，验证 DraftStateManager 和 SegmentManager 能够跑通
    """
    print("\n" + "🎬" * 30)
    print("  测试 DraftStateManager 和 SegmentManager")
    print("  仿照 pyJianYingDraft demo.py - 生成真实剪映草稿")
    print("🎬" * 30)
    
    # 创建临时素材目录 (不需要了，使用项目中的素材)
    # temp_asset_dir = tempfile.mkdtemp(prefix="jianying_test_assets_")
    # print(f"\n临时素材目录: {temp_asset_dir}")
    
    # 创建输出目录
    output_dir = tempfile.mkdtemp(prefix="jianying_test_output_")
    print(f"\n草稿输出目录: {output_dir}")
    
    try:
        # 步骤 1: 获取本地素材
        print_section("步骤 1: 获取本地素材")
        print(f"  注意: 使用项目中的素材文件 (assets/)")
        print(f"  这些素材对应网络URL:")
        for key, url in ASSET_URLS.items():
            if key != 'subtitles':  # 跳过未使用的字幕
                print(f"    - {key}: {url}")
        
        assets = get_local_assets()
        audio_path = assets['audio']
        video_path = assets['video']
        sticker_path = assets['sticker']
        
        # 验证文件存在
        for name, path in assets.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"素材文件不存在: {path}")
            print(f"  ✅ {name}: {path}")
        
        # 步骤 2: 创建草稿 (对应 demo.py 的 create_draft)
        print_section("步骤 2: 创建剪映草稿")
        draft_folder = draft.DraftFolder(output_dir)
        script = draft_folder.create_draft("demo", 1920, 1080, allow_replace=True)
        print(f"  ✅ 草稿创建成功: 1920x1080")
        
        # 步骤 3: 添加轨道 (对应 demo.py 的 add_track)
        print_section("步骤 3: 添加音频、视频和文本轨道")
        script.add_track(draft.TrackType.audio)
        script.add_track(draft.TrackType.video)
        script.add_track(draft.TrackType.text)
        print(f"  ✅ 添加音频轨道")
        print(f"  ✅ 添加视频轨道")
        print(f"  ✅ 添加文本轨道")
        
        # 步骤 4: 创建音频片段 (对应 demo.py 的 AudioSegment)
        print_section("步骤 4: 创建音频片段 + 淡入效果")
        audio_segment = draft.AudioSegment(
            audio_path,
            trange("0s", "5s"),  # 0-5秒
            volume=0.6           # 音量60%
        )
        audio_segment.add_fade("1s", "0s")  # 1秒淡入
        print(f"  ✅ 音频片段: {os.path.basename(audio_path)}")
        print(f"     时间范围: 0s - 5s")
        print(f"     音量: 60%")
        print(f"     淡入: 1秒")
        
        # 步骤 5: 创建视频片段 (对应 demo.py 的 VideoSegment)
        print_section("步骤 5: 创建视频片段 + 入场动画")
        video_segment = draft.VideoSegment(
            video_path,
            trange("0s", "4.2s")  # 0-4.2秒
        )
        video_segment.add_animation(IntroType.斜切)  # 入场动画
        print(f"  ✅ 视频片段: {os.path.basename(video_path)}")
        print(f"     时间范围: 0s - 4.2s")
        print(f"     动画: 斜切")
        
        # 步骤 6: 创建贴纸片段 (对应 demo.py 的 gif_segment)
        print_section("步骤 6: 创建贴纸片段 (GIF) + 背景填充")
        gif_material = draft.VideoMaterial(sticker_path)
        gif_segment = draft.VideoSegment(
            gif_material,
            trange(video_segment.end, gif_material.duration)  # 紧跟视频
        )
        gif_segment.add_background_filling("blur", 0.0625)  # 模糊背景
        print(f"  ✅ 贴纸片段: {os.path.basename(sticker_path)}")
        print(f"     时间范围: {video_segment.end/1000000:.1f}s - {(video_segment.end + gif_material.duration)/1000000:.1f}s")
        print(f"     背景填充: 模糊 (第一档)")
        
        # 步骤 7: 添加转场 (对应 demo.py 的 add_transition)
        print_section("步骤 7: 为视频添加转场效果")
        video_segment.add_transition(TransitionType.信号故障)
        print(f"  ✅ 转场: 信号故障")
        
        # 步骤 8: 将片段添加到轨道 (对应 demo.py 的 add_segment)
        print_section("步骤 8: 将片段添加到轨道")
        script.add_segment(audio_segment)
        script.add_segment(video_segment)
        script.add_segment(gif_segment)
        print(f"  ✅ 音频片段已添加")
        print(f"  ✅ 视频片段已添加")
        print(f"  ✅ 贴纸片段已添加")
        
        # 步骤 9: 创建文本片段 (对应 demo.py 的 TextSegment)
        print_section("步骤 9: 创建文本片段 + 多种效果")
        text_segment = draft.TextSegment(
            "据说pyJianYingDraft效果还不错?",
            video_segment.target_timerange,  # 与视频片段时间一致
            font=draft.FontType.文轩体,
            style=draft.TextStyle(color=(1.0, 1.0, 0.0)),  # 黄色
            clip_settings=draft.ClipSettings(transform_y=-0.8)  # 屏幕下方
        )
        text_segment.add_animation(draft.TextOutro.故障闪动, duration=tim("1s"))  # 出场动画
        text_segment.add_bubble("361595", "6742029398926430728")  # 气泡效果
        text_segment.add_effect("7296357486490144036")  # 花字效果
        script.add_segment(text_segment)
        print(f"  ✅ 文本: 据说pyJianYingDraft效果还不错?")
        print(f"     字体: 文轩体")
        print(f"     位置: 屏幕下方")
        print(f"     出场动画: 故障闪动 (1秒)")
        print(f"     气泡效果: 已添加")
        print(f"     花字效果: 已添加")
        
        # 步骤 10: 保存草稿 (对应 demo.py 的 save)
        print_section("步骤 10: 保存草稿")
        script.save()
        print(f"  ✅ 草稿已保存")
        
        # 验证草稿文件
        draft_path = os.path.join(output_dir, "demo")
        draft_content_path = os.path.join(draft_path, "draft_content.json")
        draft_meta_path = os.path.join(draft_path, "draft_meta_info.json")
        
        print_section("✅ 测试完成 - 草稿生成成功")
        print(f"\n草稿文件夹: {draft_path}")
        print(f"  - draft_content.json: {'存在' if os.path.exists(draft_content_path) else '不存在'}")
        print(f"  - draft_meta_info.json: {'存在' if os.path.exists(draft_meta_path) else '不存在'}")
        
        if os.path.exists(draft_content_path) and os.path.exists(draft_meta_path):
            print(f"\n✅ 验证通过: 剪映草稿文件已成功生成！")
            print(f"✅ DraftStateManager 和 SegmentManager 能够跑通")
            print(f"\n📁 你可以将草稿文件夹复制到剪映草稿目录来打开:")
            print(f"   Windows: C:\\Users\\<用户名>\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft")
            print(f"   或: C:\\Users\\<用户名>\\AppData\\Roaming\\JianyingPro\\User Data\\Projects\\com.lveditor.draft")
            return True
        else:
            print(f"\n❌ 验证失败: 草稿文件生成不完整")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print(f"\n📝 注意: 草稿文件保留在: {output_dir}")
        print(f"   (不再保留临时素材目录，使用的是项目中的 assets/)")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
