from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def _parse_video_effect_type(effect_type: str):
	name = str(effect_type or "").strip()
	if not name:
		raise ValueError("effect_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]

	try:
		return draft.VideoSceneEffectType.from_name(name)
	except Exception:
		return draft.VideoCharacterEffectType.from_name(name)


def add_video_effect(segment_id: str, effect_type: str, params: Optional[list[float]] = None) -> None:
	"""为视频片段添加特效。"""
	segment = require_segment(segment_id, draft.VideoSegment)

	logger.info("segment_id: %s, add video effect: %s", segment_id, effect_type)

	try:
		effect = _parse_video_effect_type(effect_type)
		segment.add_effect(effect_type=effect, params=params)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video effect failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video effect success: %s", segment_id)

