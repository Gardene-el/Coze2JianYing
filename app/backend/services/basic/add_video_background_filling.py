from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def add_video_background_filling(
	segment_id: str,
	fill_type: str,
	blur: float = 0.0625,
	color: str = "#00000000",
) -> None:
	"""为视频片段添加背景填充效果。"""
	segment = require_segment(segment_id, draft.VideoSegment)

	logger.info("segment_id: %s, add video background filling: %s", segment_id, fill_type)

	try:
		segment.add_background_filling(fill_type=fill_type, blur=blur, color=color)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video background filling failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video background filling success: %s", segment_id)

