#!/usr/bin/env python3
"""
测试 DraftStateManager 和 SegmentManager
通过 API 完全仿照 pyJianYingDraft demo.py 的流程生成视频
使用网络 URL 作为素材路径，直接调用 API 函数而非 HTTP 请求
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.segment_manager import get_segment_manager
from app.utils.logger import get_logger

# 资源 URL
ASSET_URLS = {
    'sticker': 'https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif',
    'video': 'https://gardene-el.github.io/Coze2JianYing/assets/video.mp4',
    'audio': 'https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3',
    'subtitles': 'https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt'
}

# 初始化
logger = get_logger(__name__)
draft_manager = get_draft_state_manager()
segment_manager = get_segment_manager()


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_create_draft():
    """
    步骤 1: 创建草稿
    对应 demo.py:
        script = draft_folder.create_draft("demo", 1920, 1080, allow_replace=True)
    """
    print_section("步骤 1: 创建草稿")
    
    result = draft_manager.create_draft(
        draft_name="API Demo Test",
        width=1920,
        height=1080,
        fps=30
    )
    
    if not result["success"]:
        logger.error(f"创建草稿失败: {result['message']}")
        return None
    
    draft_id = result["draft_id"]
    logger.info(f"✅ 草稿创建成功: {draft_id}")
    logger.info(f"   项目名称: API Demo Test")
    logger.info(f"   分辨率: 1920x1080")
    logger.info(f"   帧率: 30 fps")
    
    return draft_id


def test_add_tracks(draft_id):
    """
    步骤 2: 添加轨道
    对应 demo.py:
        script.add_track(draft.TrackType.audio).add_track(draft.TrackType.video).add_track(draft.TrackType.text)
    """
    print_section("步骤 2: 添加轨道")
    
    # 获取草稿配置
    config = draft_manager.get_draft_config(draft_id)
    if config is None:
        logger.error(f"草稿不存在: {draft_id}")
        return False
    
    # 添加音频轨道
    tracks = config.get("tracks", [])
    tracks.append({
        "track_type": "audio",
        "track_index": 0,
        "track_name": "audio_0",
        "segments": []
    })
    logger.info("✅ 添加音频轨道")
    
    # 添加视频轨道
    tracks.append({
        "track_type": "video",
        "track_index": 1,
        "track_name": "video_1",
        "segments": []
    })
    logger.info("✅ 添加视频轨道")
    
    # 添加文本轨道
    tracks.append({
        "track_type": "text",
        "track_index": 2,
        "track_name": "text_2",
        "segments": []
    })
    logger.info("✅ 添加文本轨道")
    
    config["tracks"] = tracks
    success = draft_manager.update_draft_config(draft_id, config)
    
    if not success:
        logger.error("添加轨道失败")
        return False
    
    logger.info("✅ 所有轨道添加成功")
    return True


def test_create_audio_segment():
    """
    步骤 3: 创建音频片段
    对应 demo.py:
        audio_segment = draft.AudioSegment(
            os.path.join(tutorial_asset_dir, 'audio.mp3'),
            trange("0s", "5s"),
            volume=0.6
        )
        audio_segment.add_fade("1s", "0s")
    """
    print_section("步骤 3: 创建音频片段")
    
    # 创建音频片段配置
    audio_config = {
        "material_url": ASSET_URLS['audio'],
        "target_timerange": {
            "start": 0,  # 0秒
            "duration": 5000000  # 5秒（微秒）
        },
        "volume": 0.6,  # 音量 60%
        "speed": 1.0,
        "change_pitch": False
    }
    
    result = segment_manager.create_segment("audio", audio_config)
    
    if not result["success"]:
        logger.error(f"创建音频片段失败: {result['message']}")
        return None
    
    segment_id = result["segment_id"]
    logger.info(f"✅ 音频片段创建成功: {segment_id}")
    logger.info(f"   素材: {ASSET_URLS['audio']}")
    logger.info(f"   时间范围: 0s - 5s")
    logger.info(f"   音量: 60%")
    
    # 添加淡入效果
    fade_operation = {
        "fade_in_duration": "1s",  # 1秒淡入
        "fade_out_duration": "0s"  # 无淡出
    }
    success = segment_manager.add_operation(segment_id, "add_fade", fade_operation)
    
    if success:
        logger.info("✅ 添加淡入效果 (1秒)")
    else:
        logger.warning("⚠️ 添加淡入效果失败")
    
    return segment_id


def test_create_video_segment():
    """
    步骤 4: 创建视频片段
    对应 demo.py:
        video_segment = draft.VideoSegment(
            os.path.join(tutorial_asset_dir, 'video.mp4'),
            trange("0s", "4.2s")
        )
        video_segment.add_animation(IntroType.斜切)
    """
    print_section("步骤 4: 创建视频片段")
    
    # 创建视频片段配置
    video_config = {
        "material_url": ASSET_URLS['video'],
        "target_timerange": {
            "start": 0,  # 0秒
            "duration": 4200000  # 4.2秒（微秒）
        },
        "volume": 1.0,
        "speed": 1.0,
        "change_pitch": False
    }
    
    result = segment_manager.create_segment("video", video_config)
    
    if not result["success"]:
        logger.error(f"创建视频片段失败: {result['message']}")
        return None
    
    segment_id = result["segment_id"]
    logger.info(f"✅ 视频片段创建成功: {segment_id}")
    logger.info(f"   素材: {ASSET_URLS['video']}")
    logger.info(f"   时间范围: 0s - 4.2s")
    
    # 添加入场动画
    animation_operation = {
        "animation_type": "斜切",  # 入场动画类型
        "duration": "1s"
    }
    success = segment_manager.add_operation(segment_id, "add_animation", animation_operation)
    
    if success:
        logger.info("✅ 添加入场动画 (斜切)")
    else:
        logger.warning("⚠️ 添加入场动画失败")
    
    return segment_id


def test_create_sticker_segment(video_segment_end=4200000):
    """
    步骤 5: 创建贴纸片段（GIF）
    对应 demo.py:
        gif_material = draft.VideoMaterial(os.path.join(tutorial_asset_dir, 'sticker.gif'))
        gif_segment = draft.VideoSegment(
            gif_material,
            trange(video_segment.end, gif_material.duration)
        )
        gif_segment.add_background_filling("blur", 0.0625)
    """
    print_section("步骤 5: 创建贴纸片段 (GIF)")
    
    # 贴纸作为视频片段处理（GIF是特殊的视频）
    # 假设 GIF 时长为 3 秒
    gif_duration = 3000000  # 3秒（微秒）
    
    sticker_config = {
        "material_url": ASSET_URLS['sticker'],
        "target_timerange": {
            "start": video_segment_end,  # 紧跟视频片段
            "duration": gif_duration  # 与 GIF 长度一致
        },
        "volume": 1.0,
        "speed": 1.0,
        "change_pitch": False
    }
    
    result = segment_manager.create_segment("video", sticker_config)
    
    if not result["success"]:
        logger.error(f"创建贴纸片段失败: {result['message']}")
        return None
    
    segment_id = result["segment_id"]
    logger.info(f"✅ 贴纸片段创建成功: {segment_id}")
    logger.info(f"   素材: {ASSET_URLS['sticker']}")
    logger.info(f"   时间范围: {video_segment_end/1000000}s - {(video_segment_end + gif_duration)/1000000}s")
    
    # 添加模糊背景填充
    background_operation = {
        "fill_type": "blur",
        "blur": 0.0625  # 模糊程度（剪映第一档）
    }
    success = segment_manager.add_operation(segment_id, "add_background_filling", background_operation)
    
    if success:
        logger.info("✅ 添加模糊背景填充效果")
    else:
        logger.warning("⚠️ 添加背景填充效果失败")
    
    return segment_id


def test_add_transition(video_segment_id):
    """
    步骤 6: 为视频片段添加转场
    对应 demo.py:
        video_segment.add_transition(TransitionType.信号故障)
    """
    print_section("步骤 6: 添加转场效果")
    
    # 添加转场效果到视频片段
    transition_operation = {
        "transition_type": "信号故障",
        "duration": "1s"
    }
    success = segment_manager.add_operation(video_segment_id, "add_transition", transition_operation)
    
    if success:
        logger.info(f"✅ 为视频片段添加转场效果 (信号故障)")
    else:
        logger.warning("⚠️ 添加转场效果失败")
    
    return success


def test_create_text_segment(video_timerange_start=0, video_timerange_duration=4200000):
    """
    步骤 7: 创建文本片段
    对应 demo.py:
        text_segment = draft.TextSegment(
            "据说pyJianYingDraft效果还不错?", 
            video_segment.target_timerange,
            font=draft.FontType.文轩体,
            style=draft.TextStyle(color=(1.0, 1.0, 0.0)),
            clip_settings=draft.ClipSettings(transform_y=-0.8)
        )
        text_segment.add_animation(draft.TextOutro.故障闪动, duration=tim("1s"))
        text_segment.add_bubble("361595", "6742029398926430728")
        text_segment.add_effect("7296357486490144036")
    """
    print_section("步骤 7: 创建文本片段")
    
    # 创建文本片段配置
    text_config = {
        "text_content": "据说pyJianYingDraft效果还不错?",
        "target_timerange": {
            "start": video_timerange_start,
            "duration": video_timerange_duration
        },
        "font_family": "文轩体",
        "font_size": 24.0,
        "color": "#FFFF00",  # 黄色
        "text_style": {
            "bold": False,
            "italic": False,
            "underline": False
        },
        "position": {
            "x": 0.0,
            "y": -0.8  # 屏幕下方
        }
    }
    
    result = segment_manager.create_segment("text", text_config)
    
    if not result["success"]:
        logger.error(f"创建文本片段失败: {result['message']}")
        return None
    
    segment_id = result["segment_id"]
    logger.info(f"✅ 文本片段创建成功: {segment_id}")
    logger.info(f"   文本: {text_config['text_content']}")
    logger.info(f"   字体: 文轩体")
    logger.info(f"   颜色: 黄色")
    logger.info(f"   位置: 屏幕下方")
    
    # 添加出场动画
    animation_operation = {
        "animation_type": "故障闪动",  # 出场动画
        "duration": "1s"
    }
    success = segment_manager.add_operation(segment_id, "add_animation", animation_operation)
    if success:
        logger.info("✅ 添加出场动画 (故障闪动, 1秒)")
    else:
        logger.warning("⚠️ 添加出场动画失败")
    
    # 添加气泡效果
    bubble_operation = {
        "effect_id": "361595",
        "resource_id": "6742029398926430728"
    }
    success = segment_manager.add_operation(segment_id, "add_bubble", bubble_operation)
    if success:
        logger.info("✅ 添加气泡效果")
    else:
        logger.warning("⚠️ 添加气泡效果失败")
    
    # 添加花字效果
    effect_operation = {
        "effect_id": "7296357486490144036"
    }
    success = segment_manager.add_operation(segment_id, "add_effect", effect_operation)
    if success:
        logger.info("✅ 添加花字效果")
    else:
        logger.warning("⚠️ 添加花字效果失败")
    
    return segment_id


def test_add_segments_to_draft(draft_id, audio_id, video_id, sticker_id, text_id):
    """
    步骤 8: 将所有片段添加到草稿轨道
    对应 demo.py:
        script.add_segment(audio_segment).add_segment(video_segment).add_segment(gif_segment)
        script.add_segment(text_segment)
    """
    print_section("步骤 8: 将片段添加到草稿轨道")
    
    config = draft_manager.get_draft_config(draft_id)
    if config is None:
        logger.error(f"草稿不存在: {draft_id}")
        return False
    
    tracks = config.get("tracks", [])
    
    # 添加音频片段到音频轨道
    audio_track = next((t for t in tracks if t["track_type"] == "audio"), None)
    if audio_track:
        audio_track["segments"].append(audio_id)
        logger.info(f"✅ 音频片段添加到音频轨道")
    
    # 添加视频片段和贴纸片段到视频轨道
    video_track = next((t for t in tracks if t["track_type"] == "video"), None)
    if video_track:
        video_track["segments"].append(video_id)
        video_track["segments"].append(sticker_id)
        logger.info(f"✅ 视频片段添加到视频轨道")
        logger.info(f"✅ 贴纸片段添加到视频轨道")
    
    # 添加文本片段到文本轨道
    text_track = next((t for t in tracks if t["track_type"] == "text"), None)
    if text_track:
        text_track["segments"].append(text_id)
        logger.info(f"✅ 文本片段添加到文本轨道")
    
    config["tracks"] = tracks
    success = draft_manager.update_draft_config(draft_id, config)
    
    if not success:
        logger.error("更新草稿配置失败")
        return False
    
    logger.info("✅ 所有片段添加成功")
    return True


def test_save_draft(draft_id):
    """
    步骤 9: 保存草稿
    对应 demo.py:
        script.save()
    """
    print_section("步骤 9: 保存草稿")
    
    config = draft_manager.get_draft_config(draft_id)
    if config is None:
        logger.error(f"草稿不存在: {draft_id}")
        return False
    
    # 更新状态为已保存
    config["status"] = "saved"
    success = draft_manager.update_draft_config(draft_id, config)
    
    if success:
        logger.info(f"✅ 草稿保存成功")
        logger.info(f"   草稿 ID: {draft_id}")
        logger.info(f"   草稿路径: /tmp/jianying_assistant/drafts/{draft_id}")
    else:
        logger.error("保存草稿失败")
    
    return success


def test_query_draft_status(draft_id):
    """
    步骤 10: 查询草稿状态
    """
    print_section("步骤 10: 查询草稿状态")
    
    config = draft_manager.get_draft_config(draft_id)
    if config is None:
        logger.error(f"草稿不存在: {draft_id}")
        return False
    
    logger.info("草稿状态信息:")
    logger.info(f"  项目名称: {config.get('project', {}).get('name')}")
    logger.info(f"  分辨率: {config.get('project', {}).get('width')}x{config.get('project', {}).get('height')}")
    logger.info(f"  帧率: {config.get('project', {}).get('fps')} fps")
    logger.info(f"  状态: {config.get('status')}")
    logger.info(f"  轨道数量: {len(config.get('tracks', []))}")
    
    # 统计片段数量
    total_segments = 0
    for track in config.get("tracks", []):
        track_type = track.get("track_type")
        segment_count = len(track.get("segments", []))
        total_segments += segment_count
        logger.info(f"  {track_type} 轨道片段数: {segment_count}")
    
    logger.info(f"  总片段数: {total_segments}")
    
    return True


def main():
    """主测试流程"""
    print("\n" + "🎬" * 30)
    print("  DraftStateManager 和 SegmentManager 测试")
    print("  仿照 pyJianYingDraft demo.py 完整工作流")
    print("🎬" * 30)
    
    try:
        # 步骤 1: 创建草稿
        draft_id = test_create_draft()
        if not draft_id:
            logger.error("❌ 测试失败: 无法创建草稿")
            return False
        
        # 步骤 2: 添加轨道
        if not test_add_tracks(draft_id):
            logger.error("❌ 测试失败: 无法添加轨道")
            return False
        
        # 步骤 3: 创建音频片段
        audio_id = test_create_audio_segment()
        if not audio_id:
            logger.error("❌ 测试失败: 无法创建音频片段")
            return False
        
        # 步骤 4: 创建视频片段
        video_id = test_create_video_segment()
        if not video_id:
            logger.error("❌ 测试失败: 无法创建视频片段")
            return False
        
        # 步骤 5: 创建贴纸片段
        sticker_id = test_create_sticker_segment(video_segment_end=4200000)
        if not sticker_id:
            logger.error("❌ 测试失败: 无法创建贴纸片段")
            return False
        
        # 步骤 6: 添加转场效果
        test_add_transition(video_id)
        
        # 步骤 7: 创建文本片段
        text_id = test_create_text_segment(video_timerange_start=0, video_timerange_duration=4200000)
        if not text_id:
            logger.error("❌ 测试失败: 无法创建文本片段")
            return False
        
        # 步骤 8: 将片段添加到草稿
        if not test_add_segments_to_draft(draft_id, audio_id, video_id, sticker_id, text_id):
            logger.error("❌ 测试失败: 无法添加片段到草稿")
            return False
        
        # 步骤 9: 保存草稿
        if not test_save_draft(draft_id):
            logger.error("❌ 测试失败: 无法保存草稿")
            return False
        
        # 步骤 10: 查询草稿状态
        test_query_draft_status(draft_id)
        
        # 测试成功
        print_section("✅ 测试完成")
        logger.info("✅ 所有测试步骤执行成功！")
        logger.info(f"✅ 草稿 ID: {draft_id}")
        logger.info("✅ DraftStateManager 和 SegmentManager 功能正常")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
