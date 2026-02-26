from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def add_audio_keyframe(segment_url: str, time_offset: int, volume: float) -> str:
	"""为音频片段添加音量关键帧。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	segment = require_segment(segment_id, draft.AudioSegment)

	logger.info("segment_id: %s, add audio keyframe", segment_id)

	try:
		segment.add_keyframe(time_offset=int(time_offset), volume=float(volume))
	except CustomException:
		raise
	except Exception as e:
		logger.error("add audio keyframe failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add audio keyframe success: %s", segment_id)
	return segment_url

