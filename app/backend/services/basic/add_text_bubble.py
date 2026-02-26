from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def add_text_bubble(segment_id: str, effect_id: str, resource_id: str) -> None:
	"""为文本片段添加气泡效果。"""
	segment = require_segment(segment_id, draft.TextSegment)

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

