from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import get_segment_cache, update_segment_cache


def _parse_video_animation_type(animation_type: str):
	name = str(animation_type or "").strip()
	if not name:
		raise ValueError("animation_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]

	try:
		return draft.IntroType.from_name(name)
	except Exception:
		try:
			return draft.OutroType.from_name(name)
		except Exception:
			return draft.GroupAnimationType.from_name(name)


def add_video_animation(segment_url: str, animation_type: str, duration: str = "1s") -> str:
	"""为视频片段添加动画。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	raw_segment = get_segment_cache(segment_id)
	if raw_segment is None:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)
	if not isinstance(raw_segment, draft.VideoSegment):
		raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"expect VideoSegment, got {type(raw_segment).__name__}")
	segment = raw_segment

	logger.info("segment_id: %s, add video animation: %s", segment_id, animation_type)

	try:
		animation = _parse_video_animation_type(animation_type)
		segment.add_animation(animation_type=animation, duration=duration)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video animation failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video animation success: %s", segment_id)
	return segment_url

