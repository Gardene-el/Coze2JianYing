from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft
from pyJianYingDraft.metadata import SpeechToSongType, ToneEffectType

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def _parse_audio_effect_type(effect_type: str):
	name = str(effect_type or "").strip()
	if not name:
		raise ValueError("effect_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]

	try:
		return draft.AudioSceneEffectType.from_name(name)
	except Exception:
		try:
			return ToneEffectType.from_name(name)
		except Exception:
			return SpeechToSongType.from_name(name)


def add_audio_effect(segment_url: str, effect_type: str, params: Optional[list[float | None]] = None) -> str:
	"""为音频片段添加音效。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	segment = require_segment(segment_id, draft.AudioSegment)

	logger.info("segment_id: %s, add audio effect: %s", segment_id, effect_type)

	try:
		effect = _parse_audio_effect_type(effect_type)
		segment.add_effect(effect_type=effect, params=params)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add audio effect failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add audio effect success: %s", segment_id)
	return segment_url

