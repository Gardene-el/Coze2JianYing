"""
segments/effect_segment.py — 对应 pyJianYingDraft.EffectSegment 的操作。

EffectSegment 是独立的特效轨道片段（VideoSceneEffectType / VideoCharacterEffectType）。
不需要下载素材。
"""
import uuid
from typing import Any, Dict

from app.backend.store.session_store import SessionStore
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


def create_effect(session: SessionStore, config: Dict[str, Any]) -> str:
    """
    创建特效轨道片段，返回 segment_id。

    对应 EffectSegment.__init__(effect_type, target_timerange, params)。
    """
    seg = conv.build_effect_segment(config)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "effect", "material_url": None})
    logger.info("特效片段已创建: %s (type=%s)", segment_id, config.get("effect_type"))
    return segment_id

