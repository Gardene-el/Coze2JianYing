from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import get_segment_cache, update_segment_cache


def add_text_bubble(segment_url: str, effect_id: str, resource_id: str) -> str:
	"""为文本片段添加气泡效果。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	raw_segment = get_segment_cache(segment_id)
	if raw_segment is None:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)
	if not isinstance(raw_segment, draft.TextSegment):
		raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"expect TextSegment, got {type(raw_segment).__name__}")
	segment = raw_segment

	logger.info("segment_id: %s, add text bubble", segment_id)

	try:
		segment.add_bubble(effect_id=effect_id, resource_id=resource_id)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add text bubble failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add text bubble success: %s", segment_id)
	return segment_url

