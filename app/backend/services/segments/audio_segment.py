"""
segments/audio_segment.py — 对应 pyJianYingDraft.AudioSegment 的操作。

每个函数直接操作 SessionStore 中的原生对象，立即执行。
"""
import uuid
from typing import Any, Dict, List, Optional

from app.backend.exceptions import CustomError, CustomException
from app.backend.store.session_store import SessionStore
from app.backend.services.segments._base import download_material
from app.backend.adapters import jianying_adapter as conv
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


def _resolve_audio_effect_type(effect_type: str):
    """将 'AudioSceneEffectType.XXX' 格式字符串解析为对应枚举成员。"""
    from pyJianYingDraft.metadata import AudioSceneEffectType, ToneEffectType, SpeechToSongType

    enum_map = {
        "AudioSceneEffectType": AudioSceneEffectType,
        "ToneEffectType": ToneEffectType,
        "SpeechToSongType": SpeechToSongType,
    }
    if "." in effect_type:
        prefix, name = effect_type.split(".", 1)
        if prefix in enum_map:
            try:
                return enum_map[prefix][name]
            except KeyError:
                valid = [m.name for m in enum_map[prefix]][:50]
                raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"'{name}' 不是 {prefix} 的合法成员，合法值（前50个）: {valid}")
        raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"未知音频特效枚举前缀 '{prefix}'，合法前缀: {list(enum_map.keys())}")
    # 无前缀：遍历所有
    for ec in enum_map.values():
        member = ec.__members__.get(effect_type)
        if member is not None:
            return member
    raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"未知音频特效类型: '{effect_type}'，请使用前缀格式如 'AudioSceneEffectType.人声增强'")


# ---------------------------------------------------------------------------
# 创建：构造 AudioSegment 并存入 Session
# ---------------------------------------------------------------------------

def create_audio(session: SessionStore, assets_dir: str, config: Dict[str, Any]) -> str:
    """
    创建音频片段，返回 segment_id。

    对应 AudioSegment.__init__(material, target_timerange, ...)。
    """
    url = config.get("material_url", "")
    local_path = download_material(url, assets_dir)

    seg = conv.build_audio_segment(config, local_path)
    segment_id = str(uuid.uuid4())
    session.store_segment(segment_id, seg, {"type": "audio", "material_url": url})
    logger.info("音频片段已创建: %s", segment_id)
    return segment_id


# ---------------------------------------------------------------------------
# AudioSegment.add_fade
# ---------------------------------------------------------------------------

def add_fade(
    session: SessionStore,
    segment_id: str,
    in_duration: str,
    out_duration: str,
) -> None:
    """对应 AudioSegment.add_fade(in_duration, out_duration)。"""
    session.get_segment(segment_id).add_fade(in_duration, out_duration)
    logger.info("音频片段 %s 添加淡入淡出 in=%s out=%s", segment_id, in_duration, out_duration)


# ---------------------------------------------------------------------------
# AudioSegment.add_effect
# ---------------------------------------------------------------------------

def add_effect(
    session: SessionStore,
    segment_id: str,
    effect_type: str,
    params: Optional[List[Optional[float]]] = None,
) -> None:
    """对应 AudioSegment.add_effect(effect_type, params)。"""
    effect_enum = _resolve_audio_effect_type(effect_type)
    seg = session.get_segment(segment_id)
    if params is not None:
        seg.add_effect(effect_enum, params)
    else:
        seg.add_effect(effect_enum)
    logger.info("音频片段 %s 添加特效: %s", segment_id, effect_type)


# ---------------------------------------------------------------------------
# AudioSegment.add_keyframe
# ---------------------------------------------------------------------------

def add_keyframe(
    session: SessionStore,
    segment_id: str,
    time_offset: int,
    volume: float,
) -> None:
    """对应 AudioSegment.add_keyframe(time_offset, volume)。"""
    session.get_segment(segment_id).add_keyframe(time_offset, volume)
    logger.info("音频片段 %s 添加关键帧 offset=%d volume=%s", segment_id, time_offset, volume)

