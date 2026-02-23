"""
segments/video_segment.py — 对应 pyJianYingDraft.VideoSegment / StickerSegment 的操作。

图片片段（image）使用 video 类型，因此 create_image 也在此模块中。
每个函数直接操作 SessionStore 中的原生对象，立即执行。
"""
import uuid
from typing import Any, Dict, List, Optional

from app.backend.exceptions import CustomError, CustomException
from app.backend.store.session_store import SessionStore
from app.backend.services.segments._base import download_material
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import logger


# ---------------------------------------------------------------------------
# 创建
# ---------------------------------------------------------------------------

def create_video(session: SessionStore, assets_dir: str, config: Dict[str, Any]) -> str:
    """创建视频片段，返回 segment_id。"""
    url = config.get("material_url", "")
    local_path = download_material(url, assets_dir)
    seg = conv.build_video_segment(config, local_path)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "video", "material_url": url})
    logger.info("视频片段已创建: %s", segment_id)
    return segment_id


def create_image(session: SessionStore, assets_dir: str, config: Dict[str, Any]) -> str:
    """创建图片片段（使用 video 类型轨道），返回 segment_id。"""
    url = config.get("material_url", "")
    local_path = download_material(url, assets_dir)
    seg = conv.build_video_segment(config, local_path)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "image", "material_url": url})
    logger.info("图片片段已创建: %s", segment_id)
    return segment_id


# ---------------------------------------------------------------------------
# VideoSegment.add_animation
# ---------------------------------------------------------------------------

def add_animation(
    session: SessionStore,
    segment_id: str,
    animation_type: str,
    duration: Optional[str] = "1s",
) -> None:
    """对应 VideoSegment.add_animation(animation_type, duration)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_animation", {
        "animation_type": animation_type,
        "duration": duration,
    })
    logger.info("视频片段 %s 添加动画: %s", segment_id, animation_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_effect
# ---------------------------------------------------------------------------

def add_effect(
    session: SessionStore,
    segment_id: str,
    effect_type: str,
    params: Optional[List[Optional[float]]] = None,
) -> None:
    """对应 VideoSegment.add_effect(effect_type, params)。"""
    effect_enum = conv.resolve_video_effect_enum(effect_type)

    seg = session.get_segment(segment_id)
    if params is not None:
        seg.add_effect(effect_enum, params)
    else:
        seg.add_effect(effect_enum)
    logger.info("视频片段 %s 添加特效: %s", segment_id, effect_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_fade
# ---------------------------------------------------------------------------

def add_fade(
    session: SessionStore,
    segment_id: str,
    in_duration: str,
    out_duration: str,
) -> None:
    """对应 VideoSegment.add_fade(in_duration, out_duration)。"""
    session.get_segment(segment_id).add_fade(in_duration, out_duration)
    logger.info("视频片段 %s 添加淡入淡出", segment_id)


# ---------------------------------------------------------------------------
# VideoSegment.add_filter
# ---------------------------------------------------------------------------

def add_filter(
    session: SessionStore,
    segment_id: str,
    filter_type: str,
    intensity: float = 100.0,
) -> None:
    """对应 VideoSegment.add_filter(filter_type, intensity)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_filter", {
        "filter_type": filter_type,
        "intensity": intensity,
    })
    logger.info("视频片段 %s 添加滤镜: %s", segment_id, filter_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_mask
# ---------------------------------------------------------------------------

def add_mask(
    session: SessionStore,
    segment_id: str,
    mask_type: str,
    center_x: float = 0.0,
    center_y: float = 0.0,
    size: float = 0.5,
    feather: float = 0.0,
    invert: bool = False,
    rotation: float = 0.0,
    rect_width: Optional[float] = None,
    round_corner: Optional[float] = None,
) -> None:
    """对应 VideoSegment.add_mask(mask_type, ...).

    Args:
        center_x/center_y: 以素材像素为单位（pyJianYingDraft 内部会除以 material_size/2 归一化）
        feather: 羽化程度 0-100
        rect_width: 矩形蒙版宽度（占素材宽度比例），仅 mask_type=矩形 时生效
        round_corner: 矩形蒙版圆角 0-100，仅 mask_type=矩形 时生效
    """
    seg = session.get_segment(segment_id)
    op_data: dict = {
        "mask_type_name": mask_type.split(".")[-1] if "." in mask_type else mask_type,
        "center_x": center_x,
        "center_y": center_y,
        "size": size,
        "feather": feather,
        "invert": invert,
        "rotation": rotation,
    }
    if rect_width is not None:
        op_data["rect_width"] = rect_width
    if round_corner is not None:
        op_data["round_corner"] = round_corner
    conv.apply_operation(seg, "add_mask", op_data)
    logger.info("视频片段 %s 添加蒙版: %s", segment_id, mask_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_transition
# ---------------------------------------------------------------------------

def add_transition(
    session: SessionStore,
    segment_id: str,
    transition_type: str,
    duration: Optional[str] = "1s",
) -> None:
    """对应 VideoSegment.add_transition(transition_type, duration)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_transition", {
        "transition_type": transition_type,
        "duration": duration,
    })
    logger.info("视频片段 %s 添加转场: %s", segment_id, transition_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_background_filling
# ---------------------------------------------------------------------------

def add_background_filling(
    session: SessionStore,
    segment_id: str,
    fill_type: str,
    blur: float = 0.0625,
    color: str = "#00000000",
) -> None:
    """对应 VideoSegment.add_background_filling(fill_type, blur, color)。"""
    if fill_type not in ("blur", "color"):
        raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"fill_type 必须为 'blur' 或 'color'，当前值: '{fill_type}'")
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_background_filling", {
        "fill_type": fill_type,
        "blur": blur,
        "color": color,
    })
    logger.info("视频片段 %s 添加背景填充: %s", segment_id, fill_type)


# ---------------------------------------------------------------------------
# VideoSegment.add_keyframe
# ---------------------------------------------------------------------------

def add_keyframe(
    session: SessionStore,
    segment_id: str,
    property: str,  # noqa: A002
    time_offset: int,
    value: float,
) -> None:
    """对应 VideoSegment.add_keyframe(property, time_offset, value)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_keyframe", {
        "property": property,
        "offset": time_offset,
        "value": value,
    })
    logger.info("视频片段 %s 添加关键帧 prop=%s offset=%d", segment_id, property, time_offset)

