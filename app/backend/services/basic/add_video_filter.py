from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def _parse_filter_type(filter_type: str) -> draft.FilterType:
	name = str(filter_type or "").strip()
	if not name:
		raise ValueError("filter_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.FilterType.from_name(name)


def add_video_filter(segment_id: str, filter_type: str, intensity: float = 100.0) -> None:
	"""为视频片段添加滤镜。"""
	segment = require_segment(segment_id, draft.VideoSegment)

	logger.info("segment_id: %s, add video filter: %s", segment_id, filter_type)

	try:
		filter_meta = _parse_filter_type(filter_type)
		segment.add_filter(filter_type=filter_meta, intensity=float(intensity))
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video filter failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video filter success: %s", segment_id)

