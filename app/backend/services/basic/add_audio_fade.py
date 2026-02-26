from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import get_segment_cache, update_segment_cache


def add_audio_fade(segment_url: str, in_duration: str, out_duration: str) -> str:
	"""为音频片段添加淡入淡出效果。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	raw_segment = get_segment_cache(segment_id)
	if raw_segment is None:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)
	if not isinstance(raw_segment, draft.AudioSegment):
		raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"expect AudioSegment, got {type(raw_segment).__name__}")
	segment = raw_segment

	logger.info("segment_id: %s, add audio fade", segment_id)

	try:
		segment.add_fade(in_duration=in_duration, out_duration=out_duration)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add audio fade failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add audio fade success: %s", segment_id)
	return segment_url

