from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import require_segment, update_segment_cache


def _parse_keyframe_property(prop: str) -> draft.KeyframeProperty:
	name = str(prop or "").strip()
	if not name:
		raise ValueError("property 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.KeyframeProperty.from_name(name)


def add_sticker_keyframe(segment_url: str, time_offset: int, value: float, property: str) -> str:
	"""为贴纸片段添加关键帧。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	segment = require_segment(segment_id, draft.StickerSegment)

	logger.info("segment_id: %s, add sticker keyframe", segment_id)

	try:
		key_property = _parse_keyframe_property(property)
		segment.add_keyframe(_property=key_property, time_offset=int(time_offset), value=float(value))
	except CustomException:
		raise
	except Exception as e:
		logger.error("add sticker keyframe failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add sticker keyframe success: %s", segment_id)
	return segment_url

