from __future__ import annotations

from typing import Any

import pyJianYingDraft as draft

from app.backend.core.common_types import TimeRange, parse_common_model, to_draft_timerange
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def _parse_filter_type(filter_type: str) -> draft.FilterType:
	name = str(filter_type or "").strip()
	if not name:
		raise ValueError("filter_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.FilterType.from_name(name)


def create_filter_segment(
	filter_type: str,
	target_timerange: Any,
	intensity: float = 100.0,
) -> str:
	"""创建全局滤镜片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create filter segment: %s", segment_id, filter_type)

	try:
		target_range = parse_common_model(TimeRange, target_timerange)

		segment = draft.FilterSegment(
			meta=_parse_filter_type(filter_type),
			target_timerange=to_draft_timerange(target_range),
			intensity=float(intensity) / 100.0,
		)

	except Exception as e:
		logger.error("create filter segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create filter segment success: %s", segment_id)
	return f"draft://coze2jianying/basic/create_filter_segment?segment_id={segment_id}"

