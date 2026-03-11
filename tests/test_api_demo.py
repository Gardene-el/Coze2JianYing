#!/usr/bin/env python3
"""
测试 DraftStateManager 和 SegmentManager - 通过 API 生成真实的剪映草稿文件
使用 API 函数（对应 demo.py 的每个步骤）来间接使用 DraftStateManager 和 SegmentManager
目的: 验证通过 API 调用能够生成可用的剪映草稿文件
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入 API 函数和 schemas
from src.backend.api.draft_routes import add_segment, add_track, create_draft, save_draft
from src.backend.api.segment_routes import (
    add_audio_fade,
    add_text_animation,
    add_text_bubble,
    add_text_effect,
    add_video_animation,
    add_video_background_filling,
    add_video_transition,
    create_audio_segment,
    create_text_segment,
    create_video_segment,
)
from src.backend.schemas.general_schemas import (
    AddAnimationRequest,
    AddBackgroundFillingRequest,
    AddBubbleRequest,
    AddFadeRequest,
    AddSegmentToDraftRequest,
    AddTextEffectRequest,
    AddTrackRequest,
    AddTransitionRequest,
    CreateAudioSegmentRequest,
    CreateDraftRequest,
    CreateTextSegmentRequest,
    CreateVideoSegmentRequest,
    TimeRange,
)

# 资源 URL
ASSET_URLS = {
    "sticker": "https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif",
    "video": "https://gardene-el.github.io/Coze2JianYing/assets/video.mp4",
    "audio": "https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3",
    "subtitles": "https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt",
}


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def main():
    """
    主测试流程 - 通过 API 函数仿照 pyJianYingDraft demo.py
    每个API调用对应 demo.py 中的一个操作
    """
    print("\n" + "🎬" * 30)
    print("  测试 DraftStateManager 和 SegmentManager")
    print("  通过 API 调用仿照 pyJianYingDraft demo.py")
    print("  验证能够生成真实的剪映草稿文件")
    print("🎬" * 30)

    try:
        # 步骤 1: 创建草稿 (对应 demo.py: create_draft)
        print_section("步骤 1: 创建草稿 [API: create_draft]")
        print("  对应 demo.py: draft_folder.create_draft('demo', 1920, 1080)")

        create_req = CreateDraftRequest(
            draft_name="demo", width=1920, height=1080, fps=30
        )
        create_resp = await create_draft(create_req)
        draft_id = create_resp.draft_id
        print(f"  ✅ 草稿创建成功: {draft_id}")
        print(f"     分辨率: 1920x1080")

        # 步骤 2: 添加轨道 (对应 demo.py: add_track)
        print_section("步骤 2: 添加轨道 [API: add_track]")
        print("  对应 demo.py: script.add_track(draft.TrackType.audio/video/text)")

        # 添加音频轨道
        await add_track(draft_id, AddTrackRequest(track_type="audio"))
        print(f"  ✅ 添加音频轨道")

        # 添加视频轨道
        await add_track(draft_id, AddTrackRequest(track_type="video"))
        print(f"  ✅ 添加视频轨道")

        # 添加文本轨道
        await add_track(draft_id, AddTrackRequest(track_type="text"))
        print(f"  ✅ 添加文本轨道")

        # 步骤 3: 创建音频片段 (对应 demo.py: AudioSegment)
        print_section("步骤 3: 创建音频片段 [API: create_audio_segment]")
        print(
            "  对应 demo.py: draft.AudioSegment(audio.mp3, trange('0s', '5s'), volume=0.6)"
        )

        audio_req = CreateAudioSegmentRequest(
            material_url=ASSET_URLS["audio"],
            target_timerange=TimeRange(start=0, duration=5000000),  # 5秒
            volume=0.6,
        )
        audio_resp = await create_audio_segment(audio_req)
        audio_id = audio_resp.segment_id
        print(f"  ✅ 音频片段: {audio_id}")
        print(f"     素材: {ASSET_URLS['audio']}")
        print(f"     时间: 0s - 5s, 音量: 60%")

        # 步骤 4: 为音频添加淡入 (对应 demo.py: add_fade)
        print_section("步骤 4: 音频添加淡入效果 [API: add_audio_fade]")
        print("  对应 demo.py: audio_segment.add_fade('1s', '0s')")

        fade_req = AddFadeRequest(in_duration="1s", out_duration="0s")
        await add_audio_fade(audio_id, fade_req)
        print(f"  ✅ 淡入效果: 1秒")

        # 步骤 5: 创建视频片段 (对应 demo.py: VideoSegment)
        print_section("步骤 5: 创建视频片段 [API: create_video_segment]")
        print("  对应 demo.py: draft.VideoSegment(video.mp4, trange('0s', '4.2s'))")

        video_req = CreateVideoSegmentRequest(
            material_url=ASSET_URLS["video"],
            target_timerange=TimeRange(start=0, duration=4200000),  # 4.2秒
        )
        video_resp = await create_video_segment(video_req)
        video_id = video_resp.segment_id
        print(f"  ✅ 视频片段: {video_id}")
        print(f"     素材: {ASSET_URLS['video']}")
        print(f"     时间: 0s - 4.2s")

        # 步骤 6: 为视频添加入场动画 (对应 demo.py: add_animation)
        print_section("步骤 6: 视频添加入场动画 [API: add_video_animation]")
        print("  对应 demo.py: video_segment.add_animation(IntroType.斜切)")

        anim_req = AddAnimationRequest(animation_type="斜切")
        await add_video_animation(video_id, anim_req)
        print(f"  ✅ 入场动画: 斜切")

        # 步骤 7: 创建贴纸片段 (对应 demo.py: gif_segment)
        print_section("步骤 7: 创建贴纸片段 [API: create_video_segment]")
        print("  对应 demo.py: draft.VideoSegment(gif_material, trange(...))")

        gif_req = CreateVideoSegmentRequest(
            material_url=ASSET_URLS["sticker"],
            target_timerange=TimeRange(start=4200000, duration=900000),  # 0.9秒 GIF
        )
        gif_resp = await create_video_segment(gif_req)
        gif_id = gif_resp.segment_id
        print(f"  ✅ 贴纸片段: {gif_id}")
        print(f"     素材: {ASSET_URLS['sticker']}")
        print(f"     时间: 4.2s - 5.1s")

        # 步骤 8: 为贴纸添加背景填充 (对应 demo.py: add_background_filling)
        print_section("步骤 8: 贴纸添加背景填充 [API: add_video_background_filling]")
        print("  对应 demo.py: gif_segment.add_background_filling('blur', 0.0625)")

        bg_req = AddBackgroundFillingRequest(fill_type="blur", blur=0.0625)
        await add_video_background_filling(gif_id, bg_req)
        print(f"  ✅ 背景填充: 模糊 (第一档)")

        # 步骤 9: 为视频添加转场 (对应 demo.py: add_transition)
        print_section("步骤 9: 视频添加转场效果 [API: add_video_transition]")
        print("  对应 demo.py: video_segment.add_transition(TransitionType.信号故障)")

        trans_req = AddTransitionRequest(transition_type="信号故障")
        await add_video_transition(video_id, trans_req)
        print(f"  ✅ 转场: 信号故障")

        # 步骤 10: 将片段添加到草稿 (对应 demo.py: add_segment)
        print_section("步骤 10: 将片段添加到草稿 [API: add_segment]")
        print("  对应 demo.py: script.add_segment(audio/video/gif_segment)")

        await add_segment(draft_id, AddSegmentToDraftRequest(segment_id=audio_id))
        print(f"  ✅ 音频片段已添加")

        await add_segment(draft_id, AddSegmentToDraftRequest(segment_id=video_id))
        print(f"  ✅ 视频片段已添加")

        await add_segment(draft_id, AddSegmentToDraftRequest(segment_id=gif_id))
        print(f"  ✅ 贴纸片段已添加")

        # 步骤 11: 创建文本片段 (对应 demo.py: TextSegment)
        print_section("步骤 11: 创建文本片段 [API: create_text_segment]")
        print(
            "  对应 demo.py: draft.TextSegment('据说pyJianYingDraft效果还不错?', ...)"
        )

        text_req = CreateTextSegmentRequest(
            text_content="据说pyJianYingDraft效果还不错?",
            target_timerange=TimeRange(start=0, duration=4200000),
            font_family="文轩体",
            color="#FFFF00",  # 黄色
            position={"x": 0.0, "y": -0.8},
        )
        text_resp = await create_text_segment(text_req)
        text_id = text_resp.segment_id
        print(f"  ✅ 文本片段: {text_id}")
        print(f"     内容: 据说pyJianYingDraft效果还不错?")
        print(f"     字体: 文轩体, 位置: 屏幕下方")

        # 步骤 12: 为文本添加出场动画 (对应 demo.py: add_animation)
        print_section("步骤 12: 文本添加出场动画 [API: add_text_animation]")
        print(
            "  对应 demo.py: text_segment.add_animation(draft.TextOutro.故障闪动, duration=tim('1s'))"
        )

        text_anim_req = AddAnimationRequest(animation_type="故障闪动", duration="1s")
        await add_text_animation(text_id, text_anim_req)
        print(f"  ✅ 出场动画: 故障闪动 (1秒)")

        # 步骤 13: 为文本添加气泡效果 (对应 demo.py: add_bubble)
        print_section("步骤 13: 文本添加气泡效果 [API: add_text_bubble]")
        print(
            "  对应 demo.py: text_segment.add_bubble('361595', '6742029398926430728')"
        )

        bubble_req = AddBubbleRequest(
            effect_id="361595", resource_id="6742029398926430728"
        )
        await add_text_bubble(text_id, bubble_req)
        print(f"  ✅ 气泡效果已添加")

        # 步骤 14: 为文本添加花字效果 (对应 demo.py: add_effect)
        print_section("步骤 14: 文本添加花字效果 [API: add_text_effect]")
        print("  对应 demo.py: text_segment.add_effect('7296357486490144036')")

        effect_req = AddTextEffectRequest(effect_id="7296357486490144036")
        await add_text_effect(text_id, effect_req)
        print(f"  ✅ 花字效果已添加")

        # 步骤 15: 将文本片段添加到草稿
        print_section("步骤 15: 将文本片段添加到草稿 [API: add_segment]")
        print("  对应 demo.py: script.add_segment(text_segment)")

        await add_segment(draft_id, AddSegmentToDraftRequest(segment_id=text_id))
        print(f"  ✅ 文本片段已添加")

        # 步骤 16: 保存草稿 (对应 demo.py: script.save())
        print_section("步骤 16: 保存草稿 [API: save_draft]")
        print("  对应 demo.py: script.save()")

        save_resp = await save_draft(draft_id)
        draft_path = save_resp.draft_path
        print(f"  ✅ 草稿已保存")

        # 验证草稿文件
        draft_content_path = os.path.join(draft_path, "draft_content.json")
        draft_meta_path = os.path.join(draft_path, "draft_meta_info.json")

        print_section("✅ 测试完成 - 草稿生成成功")
        print(f"\n草稿文件夹: {draft_path}")
        print(
            f"  - draft_content.json: {'存在' if os.path.exists(draft_content_path) else '不存在'}"
        )
        print(
            f"  - draft_meta_info.json: {'存在' if os.path.exists(draft_meta_path) else '不存在'}"
        )

        if os.path.exists(draft_content_path) and os.path.exists(draft_meta_path):
            print(f"\n✅ 验证通过: 剪映草稿文件已成功生成！")
            print(f"✅ 通过 API 使用 DraftStateManager 和 SegmentManager 能够生成草稿")
            print(f"\n📁 可以将草稿文件夹复制到剪映草稿目录来打开:")
            print(
                f"   Windows: C:\\Users\\<用户名>\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
            )
            return True
        else:
            print(f"\n❌ 验证失败: 草稿文件生成不完整")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
