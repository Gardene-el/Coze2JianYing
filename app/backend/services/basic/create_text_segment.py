from __future__ import annotations

from typing import Any, Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import (
	ClipSettings,
	TextBackground,
	TextBorder,
	TextShadow,
	TextStyle,
	TimeRange,
	parse_common_model,
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
	target_timerange: Any,
	font_family: Optional[str] = "文轩体",
	text_style: Optional[Any] = None,
	text_border: Optional[Any] = None,
	text_shadow: Optional[Any] = None,
	text_background: Optional[Any] = None,
	clip_settings: Optional[Any] = None,
) -> str:
	"""创建文本片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create text segment", segment_id)

	try:
		target_range = parse_common_model(TimeRange, target_timerange)
		style_model = parse_common_model(TextStyle, text_style) if text_style is not None else None
		border_model = parse_common_model(TextBorder, text_border) if text_border is not None else None
		shadow_model = parse_common_model(TextShadow, text_shadow) if text_shadow is not None else None
		background_model = parse_common_model(TextBackground, text_background) if text_background is not None else None
		clip_model = parse_common_model(ClipSettings, clip_settings) if clip_settings is not None else None

		font = None
		if font_family:
			try:
				font = draft.FontType.from_name(font_family)
			except Exception:
				logger.warning("font not found in FontType: %s, fallback to default", font_family)

		segment = draft.TextSegment(
			text=text_content,
			timerange=to_draft_timerange(target_range),
			font=font,
			style=to_draft_text_style(style_model) if style_model is not None else None,
			clip_settings=to_draft_clip_settings(clip_model) if clip_model is not None else None,
			border=to_draft_text_border(border_model) if border_model is not None else None,
			background=to_draft_text_background(background_model) if background_model is not None else None,
			shadow=to_draft_text_shadow(shadow_model) if shadow_model is not None else None,
		)

	except Exception as e:
		logger.error("create text segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create text segment success: %s", segment_id)
	return f"draft://coze2jianying/basic/create_text_segment?segment_id={segment_id}"

