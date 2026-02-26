from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import ClipSettings, TimeRange, to_draft_clip_settings, to_draft_timerange
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def create_sticker_segment(
	material_url: str,
	target_timerange: TimeRange,
	clip_settings: Optional[ClipSettings] = None,
) -> str:
	"""创建贴纸片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create sticker segment from: %s", segment_id, material_url)

	try:
		segment = draft.StickerSegment(
			resource_id=material_url,
			target_timerange=to_draft_timerange(target_timerange),
			clip_settings=to_draft_clip_settings(clip_settings) if clip_settings is not None else None,
		)

	except Exception as e:
		logger.error("create sticker segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create sticker segment success: %s", segment_id)
	return f"draft://coze2jianying/basic/create_sticker_segment?segment_id={segment_id}"

