"""
segments/text_segment.py — 对应 pyJianYingDraft.TextSegment 的操作。

每个函数直接操作 SessionStore 中的原生对象，立即执行。
"""
import uuid
from typing import Any, Dict, Optional

from app.backend.store.session_store import SessionStore
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import logger


# ---------------------------------------------------------------------------
# 创建：构造 TextSegment 并存入 Session
# ---------------------------------------------------------------------------

def create_text(session: SessionStore, config: Dict[str, Any]) -> str:
    """
    创建文本片段，返回 segment_id。

    对应 TextSegment.__init__(text_content, target_timerange, ...)。
    不需要下载素材。
    """
    seg = conv.build_text_segment(config)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "text", "material_url": None})
    logger.info("文本片段已创建: %s", segment_id)
    return segment_id


# ---------------------------------------------------------------------------
# TextSegment.add_animation
# ---------------------------------------------------------------------------

def add_animation(
    session: SessionStore,
    segment_id: str,
    animation_type: str,
    duration: Optional[str] = "1s",
) -> None:
    """对应 TextSegment.add_animation(animation_type, duration)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_animation", {
        "animation_type": animation_type,
        "duration": duration,
    })
    logger.info("文本片段 %s 添加动画: %s", segment_id, animation_type)


# ---------------------------------------------------------------------------
# TextSegment.add_bubble
# ---------------------------------------------------------------------------

def add_bubble(
    session: SessionStore,
    segment_id: str,
    effect_id: str,
    resource_id: str,
) -> None:
    """对应 TextSegment.add_bubble(effect_id, resource_id)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_bubble", {
        "effect_id": effect_id,
        "resource_id": resource_id,
    })
    logger.info("文本片段 %s 添加气泡: effect_id=%s", segment_id, effect_id)


# ---------------------------------------------------------------------------
# TextSegment.add_effect（花字）
# ---------------------------------------------------------------------------

def add_effect(
    session: SessionStore,
    segment_id: str,
    effect_id: str,
) -> None:
    """对应 TextSegment.add_effect(effect_id)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_effect", {
        "effect_id": effect_id,
    })
    logger.info("文本片段 %s 添加花字特效: %s", segment_id, effect_id)


# ---------------------------------------------------------------------------
# TextSegment.add_keyframe
# ---------------------------------------------------------------------------

def add_keyframe(
    session: SessionStore,
    segment_id: str,
    property: str,  # noqa: A002
    time_offset: int,
    value: float,
) -> None:
    """对应 TextSegment.add_keyframe(property, time_offset, value)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_keyframe", {
        "property": property,
        "offset": time_offset,
        "value": value,
    })
    logger.info("文本片段 %s 添加关键帧 prop=%s offset=%d", segment_id, property, time_offset)

