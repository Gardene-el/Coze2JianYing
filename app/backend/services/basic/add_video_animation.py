from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


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


def add_video_animation(segment_id: str, animation_type: str, duration: str = "1s") -> None:
	"""为视频片段添加动画。"""
	segment = require_segment(segment_id, draft.VideoSegment)

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

