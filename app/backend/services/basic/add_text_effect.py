from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def add_text_effect(segment_url: str, effect_id: str) -> str:
	"""为文本片段添加花字效果。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	segment = require_segment(segment_id, draft.TextSegment)

	logger.info("segment_id: %s, add text effect", segment_id)

	try:
		segment.add_effect(effect_id=effect_id)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add text effect failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add text effect success: %s", segment_id)
	return segment_url

