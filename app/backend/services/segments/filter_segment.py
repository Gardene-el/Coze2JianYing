"""
segments/filter_segment.py — 对应 pyJianYingDraft.FilterSegment 的操作。

FilterSegment 是独立的滤镜轨道片段。不需要下载素材。
"""
import uuid
from typing import Any, Dict

from app.backend.store.session_store import SessionStore
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import logger


def create_filter(session: SessionStore, config: Dict[str, Any]) -> str:
    """
    创建滤镜轨道片段，返回 segment_id。

    对应 FilterSegment.__init__(filter_type, target_timerange, intensity)。
    """
    seg = conv.build_filter_segment(config)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "filter", "material_url": None})
    logger.info("滤镜片段已创建: %s (type=%s)", segment_id, config.get("filter_type"))
    return segment_id

