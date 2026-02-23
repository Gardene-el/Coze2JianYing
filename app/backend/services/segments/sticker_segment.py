"""
segments/sticker_segment.py — 对应 pyJianYingDraft.StickerSegment 的操作。

StickerSegment 通过 resource_id 引用剪映内置贴纸，无需下载素材。
"""
import uuid
from typing import Any, Dict

from app.backend.store.session_store import SessionStore
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import logger


# ---------------------------------------------------------------------------
# 创建：构造 StickerSegment 并存入 Session
# ---------------------------------------------------------------------------

def create_sticker(session: SessionStore, config: Dict[str, Any]) -> str:
    """
    创建贴纸片段，返回 segment_id。

    对应 StickerSegment.__init__(resource_id, target_timerange, clip_settings)。
    不需要下载素材（通过剪映内置 resource_id 引用）。

    兼容性：当请求体中使用 material_url 字段而非 resource_id 时，自动做映射。
    """
    cfg = dict(config)
    # 兼容 CreateStickerSegmentRequest 中的 material_url 字段
    if "resource_id" not in cfg and "material_url" in cfg:
        cfg["resource_id"] = cfg.pop("material_url")
    seg = conv.build_sticker_segment(cfg)
    segment_id = str(uuid.uuid4())
    resource_id = cfg.get("resource_id", "")
    session.store_segment(segment_id, seg, {"type": "sticker", "material_url": resource_id})
    logger.info("贴纸片段已创建: %s (resource_id=%s)", segment_id, resource_id)
    return segment_id


# ---------------------------------------------------------------------------
# StickerSegment.add_keyframe
# ---------------------------------------------------------------------------

def add_keyframe(
    session: SessionStore,
    segment_id: str,
    property: str,  # noqa: A002
    time_offset: int,
    value: float,
) -> None:
    """对应 StickerSegment.add_keyframe(property, time_offset, value)。"""
    seg = session.get_segment(segment_id)
    conv.apply_operation(seg, "add_keyframe", {
        "property": property,
        "offset": time_offset,
        "value": value,
    })
    logger.info("贴纸片段 %s 添加关键帧 prop=%s offset=%d", segment_id, property, time_offset)

