from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import (
	ClipSettings,
	TextBackground,
	TextBorder,
	TextShadow,
	TextStyle,
	TimeRange,
	to_draft_clip_settings,
	to_draft_text_background,
	to_draft_text_border,
	to_draft_text_shadow,
	to_draft_text_style,
	to_draft_timerange,
)
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def create_text_segment(
	text_content: str,
	target_timerange: TimeRange,
	font_family: Optional[str] = "文轩体",
	text_style: Optional[TextStyle] = None,
	text_border: Optional[TextBorder] = None,
	text_shadow: Optional[TextShadow] = None,
	text_background: Optional[TextBackground] = None,
	clip_settings: Optional[ClipSettings] = None,
) -> str:
	"""创建文本片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create text segment", segment_id)

	try:
		font = None
		if font_family:
			try:
				font = draft.FontType.from_name(font_family)
			except Exception:
				logger.warning("font not found in FontType: %s, fallback to default", font_family)

		segment = draft.TextSegment(
			text=text_content,
			timerange=to_draft_timerange(target_timerange),
			font=font,
			style=to_draft_text_style(text_style) if text_style is not None else None,
			clip_settings=to_draft_clip_settings(clip_settings) if clip_settings is not None else None,
			border=to_draft_text_border(text_border) if text_border is not None else None,
			background=to_draft_text_background(text_background) if text_background is not None else None,
			shadow=to_draft_text_shadow(text_shadow) if text_shadow is not None else None,
		)

	except Exception as e:
		logger.error("create text segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create text segment success: %s", segment_id)
	return segment_id

