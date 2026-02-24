from __future__ import annotations

from typing import Any, Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import TimeRange, parse_common_model, to_draft_timerange
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def _parse_effect_type(effect_type: str) -> Any:
	name = str(effect_type or "").strip()
	if not name:
		raise ValueError("effect_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]

	try:
		return draft.VideoSceneEffectType.from_name(name)
	except Exception:
		return draft.VideoCharacterEffectType.from_name(name)


def create_effect_segment(
	effect_type: str,
	target_timerange: Any,
	params: Optional[list[float]] = None,
) -> str:
	"""创建全局特效片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create effect segment: %s", segment_id, effect_type)

	try:
		target_range = parse_common_model(TimeRange, target_timerange)

		segment = draft.EffectSegment(
			effect_type=_parse_effect_type(effect_type),
			target_timerange=to_draft_timerange(target_range),
			params=params,
		)

	except Exception as e:
		logger.error("create effect segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create effect segment success: %s", segment_id)
	return f"draft://coze2jianying/basic/create_effect_segment?segment_id={segment_id}"

