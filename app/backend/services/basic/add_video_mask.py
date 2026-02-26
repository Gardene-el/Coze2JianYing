from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import get_segment_cache, update_segment_cache


def _parse_mask_type(mask_type: str) -> draft.MaskType:
	name = str(mask_type or "").strip()
	if not name:
		raise ValueError("mask_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.MaskType.from_name(name)


def add_video_mask(
	segment_url: str,
	mask_type: str,
	center_x: float = 0.0,
	center_y: float = 0.0,
	size: float = 0.5,
	feather: float = 0.0,
	invert: bool = False,
	rotation: float = 0.0,
	rect_width: Optional[float] = None,
	round_corner: Optional[float] = None,
) -> str:
	"""为视频片段添加蒙版。"""
	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	raw_segment = get_segment_cache(segment_id)
	if raw_segment is None:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)
	if not isinstance(raw_segment, draft.VideoSegment):
		raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"expect VideoSegment, got {type(raw_segment).__name__}")
	segment = raw_segment

	logger.info("segment_id: %s, add video mask: %s", segment_id, mask_type)

	try:
		mask = _parse_mask_type(mask_type)
		segment.add_mask(
			mask_type=mask,
			center_x=float(center_x),
			center_y=float(center_y),
			size=float(size),
			rotation=float(rotation),
			feather=float(feather),
			invert=bool(invert),
			rect_width=rect_width,
			round_corner=round_corner,
		)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add video mask failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("add video mask success: %s", segment_id)
	return segment_url

