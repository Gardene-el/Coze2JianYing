"""
数据结构转换器
将 Draft Generator Interface 的数据结构转换为 pyJianYingDraft 的数据结构
"""
import pyJianYingDraft as draft
from pyJianYingDraft import (
    Timerange, ClipSettings, CropSettings, TextStyle,
    VideoSegment, AudioSegment, TextSegment, IntroType, TransitionType, trange, tim
)

from typing import Dict, Any, Optional
from src.backend.utils.logger import logger


# ========== 基础转换函数 ==========

def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为RGB元组，取值范围 [0, 1]"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    rgb_tuple = (r / 255.0, g / 255.0, b / 255.0)
    logger.debug(f"颜色转换: {hex_color} -> {rgb_tuple}")
    return rgb_tuple


def convert_timerange(time_range_dict: Dict[str, int]) -> Timerange:
    """
    转换时间范围格式
    Draft Generator Interface: {"start": ms, "end": ms}
    pyJianYingDraft: Timerange(start, duration)
    """
    start = time_range_dict["start"]
    end = time_range_dict["end"]
    duration = end - start
    logger.info(f"转换时间范围: start={start}ms, end={end}ms -> duration={duration}ms")
    return Timerange(start=start, duration=duration)


def convert_crop_settings(crop_dict: Dict[str, Any]) -> Optional[CropSettings]:
    """
    转换裁剪设置
    Draft Generator Interface: {left, top, right, bottom}
    pyJianYingDraft: CropSettings(四角点坐标)
    """
    if not crop_dict.get("enabled", False):
        return None

    left = crop_dict.get("left", 0.0)
    top = crop_dict.get("top", 0.0)
    right = crop_dict.get("right", 1.0)
    bottom = crop_dict.get("bottom", 1.0)

    logger.debug(f"转换裁剪设置: L={left}, T={top}, R={right}, B={bottom}")
    return CropSettings(
        upper_left_x=left,
        upper_left_y=top,
        upper_right_x=right,
        upper_right_y=top,
        lower_left_x=left,
        lower_left_y=bottom,
        lower_right_x=right,
        lower_right_y=bottom
    )


def convert_clip_settings(transform_dict: Dict[str, Any]) -> ClipSettings:
    """
    转换变换设置
    Draft Generator Interface: {position_x, position_y, scale_x, scale_y, rotation, opacity}
    pyJianYingDraft: ClipSettings(alpha, rotation, scale_x, scale_y, transform_x, transform_y)
    """
    def get(key: str, default: float) -> float:
        value = transform_dict.get(key)
        return default if value is None else value

    settings = ClipSettings(
        alpha=get("opacity", 1.0),
        rotation=get("rotation", 0.0),
        scale_x=get("scale_x", 1.0),
        scale_y=get("scale_y", 1.0),
        transform_x=get("position_x", 0.0),
        transform_y=get("position_y", 0.0)
    )
    logger.debug(f"转换变换设置: alpha={settings.alpha}, rotation={settings.rotation}")
    return settings


def convert_filter_intensity(intensity_0_1: float) -> float:
    """转换滤镜强度：0.0-1.0 → 0-100"""
    result = intensity_0_1 * 100.0
    logger.debug(f"转换滤镜强度: {intensity_0_1} -> {result}")
    return result


# ========== Segment转换函数 ==========

def convert_image_segment_config(
    segment_config: Dict[str, Any],
    image_file_path: str
) -> VideoSegment:
    """转换图片段配置到 VideoSegment"""
    logger.info("转换图片段配置")

    # 1. 时间范围（必须）
    target_timerange = convert_timerange(segment_config["time_range"])

    # 2. 变换设置（可选）
    clip_settings = None
    transform_config = segment_config.get("transform")
    if transform_config and any(v is not None for v in transform_config.values()):
        clip_settings = convert_clip_settings(transform_config)

    # 3. 创建 VideoSegment
    kwargs: Dict[str, Any] = {
        "material": image_file_path,
        "target_timerange": target_timerange,
    }
    if clip_settings is not None:
        kwargs["clip_settings"] = clip_settings

    image_segment = VideoSegment(**kwargs)
    logger.info(f"图片段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
    return image_segment


def convert_video_segment_config(
    segment_config: Dict[str, Any],
    video_material: draft.VideoMaterial
) -> VideoSegment:
    """转换视频段配置到 VideoSegment"""
    logger.info("转换视频段配置")

    # 1. 时间范围（必须）
    target_timerange = convert_timerange(segment_config["time_range"])

    # 2. 素材裁剪范围（可选）
    source_timerange = None
    if segment_config.get("material_range"):
        source_timerange = convert_timerange(segment_config["material_range"])

    # 3. 变换设置（可选）
    clip_settings = None
    transform_config = segment_config.get("transform")
    if transform_config and any(v is not None for v in transform_config.values()):
        clip_settings = convert_clip_settings(transform_config)

    # 4. 速度控制（可选）
    speed = None
    speed_config = segment_config.get("speed")
    if speed_config and speed_config.get("speed") is not None:
        speed = speed_config["speed"]

    # 5. 创建 VideoSegment，只传入非空参数
    kwargs: Dict[str, Any] = {
        "material": video_material,
        "target_timerange": target_timerange,
    }
    if source_timerange is not None:
        kwargs["source_timerange"] = source_timerange
    if speed is not None:
        kwargs["speed"] = speed
    if clip_settings is not None:
        kwargs["clip_settings"] = clip_settings

    video_segment = VideoSegment(**kwargs)
    logger.info(f"视频段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
    return video_segment


def convert_audio_segment_config(
    segment_config: Dict[str, Any],
    audio_material: draft.AudioMaterial
) -> AudioSegment:
    """转换音频段配置到 AudioSegment"""
    logger.info("转换音频段配置")

    # 1. 时间范围
    target_timerange = convert_timerange(segment_config["time_range"])

    # 2. 素材裁剪范围（可选）
    source_timerange = None
    if segment_config.get("material_range"):
        source_timerange = convert_timerange(segment_config["material_range"])

    # 3. 音频属性（可选）
    volume = None
    speed = None
    audio_config = segment_config.get("audio")
    if audio_config:
        if audio_config.get("volume") is not None:
            volume = audio_config["volume"]
        if audio_config.get("speed") is not None:
            speed = audio_config["speed"]

    # 4. 创建 AudioSegment，只传入非空参数
    kwargs: Dict[str, Any] = {
        "material": audio_material,
        "target_timerange": target_timerange,
    }
    if source_timerange is not None:
        kwargs["source_timerange"] = source_timerange
    if volume is not None:
        kwargs["volume"] = volume
    if speed is not None:
        kwargs["speed"] = speed

    audio_segment = AudioSegment(**kwargs)
    logger.info(f"音频段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
    return audio_segment


def convert_text_segment_config(segment_config: Dict[str, Any]) -> TextSegment:
    """转换文本段配置到 TextSegment"""
    logger.info("转换文本段配置")

    # 1. 基本信息
    text_content = segment_config["content"]
    timerange = convert_timerange(segment_config["time_range"])

    # 2. 变换设置（可选）
    clip_settings = None
    transform_config = segment_config.get("transform")
    if transform_config and any(v is not None for v in transform_config.values()):
        def get(key: str, default: float) -> float:
            value = transform_config.get(key)
            return default if value is None else value

        scale = get("scale", 1.0)
        clip_settings = ClipSettings(
            alpha=get("opacity", 1.0),
            rotation=get("rotation", 0.0),
            scale_x=scale,
            scale_y=scale,
            transform_x=get("position_x", 0.5),
            transform_y=get("position_y", 0.0)
        )

    # 3. 文本样式（可选）
    text_style = None
    style_config = segment_config.get("style")
    if style_config and any(v is not None for v in style_config.values()):
        def get_style(key: str, default: Any) -> Any:
            value = style_config.get(key)
            return default if value is None else value

        color_hex = get_style("color", "#FFFFFF")
        color_rgb = hex_to_rgb(color_hex)

        # 获取字体大小，注意pyJianYingDraft的默认值是8.0
        # 如果输入是像素值（如48），需要转换到合理范围
        font_size_input = get_style("font_size", None)
        if font_size_input is None:
            font_size = 8.0
        elif font_size_input > 20:
            font_size = font_size_input / 6.0  # 48px -> 8.0
            logger.warning(f"字体大小从像素值{font_size_input}转换为{font_size}")
        else:
            font_size = font_size_input

        text_style = TextStyle(size=font_size, color=color_rgb)

    # 4. 创建 TextSegment，只传入非空参数
    kwargs: Dict[str, Any] = {"text": text_content, "timerange": timerange}
    if text_style is not None:
        kwargs["style"] = text_style
    if clip_settings is not None:
        kwargs["clip_settings"] = clip_settings

    text_segment = TextSegment(**kwargs)
    text_preview = text_content[:20] if len(text_content) > 20 else text_content
    logger.info(f"文本段创建完成: '{text_preview}...' at {timerange.start}ms")
    return text_segment