from __future__ import annotations

import pyJianYingDraft as draft

from src.backend.exceptions import CustomError, CustomException
from src.backend.utils.logger import logger
from src.backend.utils.cache import require_segment, update_segment_cache


def _parse_keyframe_property(prop: str) -> draft.KeyframeProperty:
	name = str(prop or "").strip()
	if not name:
		raise ValueError("property 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	try:
		return draft.KeyframeProperty[name]
	except KeyError:
		valid = [m.name for m in draft.KeyframeProperty]
		raise ValueError(f"无效的关键帧属性 '{name}'，有效值：{valid}")


def add_sticker_keyframe(segment_id: str, time_offset: int, value: float, property: str) -> None:
	"""为贴纸片段添加关键帧。"""
	segment = require_segment(segment_id, draft.StickerSegment)

	logger.info("segment_id: %s, add sticker keyframe", segment_id)

	try:
		key_property = _parse_keyframe_property(property)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add sticker keyframe failed: %s", e)
		raise CustomException(CustomError.INVALID_KEYFRAME_INFO, str(e))

	try:
		segment.add_keyframe(_property=key_property, time_offset=int(time_offset), value=float(value))
	except CustomException:
		raise
	except Exception as e:
		logger.error("add sticker keyframe failed: %s", e)
		raise CustomException(CustomError.KEYFRAME_ADD_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add sticker keyframe success: %s", segment_id)

