from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def _parse_transition_type(transition_type: str) -> draft.TransitionType:
	name = str(transition_type or "").strip()
	if not name:
		raise ValueError("transition_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.TransitionType.from_name(name)


def add_video_transition(segment_url: str, transition_type: str, duration: Optional[str] = "1s") -> str:
	"""为视频片段添加转场。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	segment = require_segment(segment_id, draft.VideoSegment)

	logger.info("segment_id: %s, add video transition: %s", segment_id, transition_type)

	try:
		transition = _parse_transition_type(transition_type)
		segment.add_transition(transition_type=transition, duration=duration)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video transition failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video transition success: %s", segment_id)
	return segment_url

