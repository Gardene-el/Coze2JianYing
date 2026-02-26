from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def add_video_fade(segment_id: str, in_duration: str, out_duration: str) -> None:
	"""为视频片段添加音频淡入淡出效果。"""
	segment = require_segment(segment_id, draft.VideoSegment)

	logger.info("segment_id: %s, add video fade", segment_id)

	try:
		segment.add_fade(in_duration=in_duration, out_duration=out_duration)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video fade failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video fade success: %s", segment_id)

