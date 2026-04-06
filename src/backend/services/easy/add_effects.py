from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from pyJianYingDraft import EffectSegment, Timerange, TrackType
from pyJianYingDraft.metadata import VideoCharacterEffectType, VideoSceneEffectType

from src.backend.exceptions import CustomError, CustomException
from src.backend.utils.cache import require_draft
from src.backend.utils.logger import logger


def add_effects(draft_id: str, effect_infos: str) -> List[str]:
	"""批量添加特效。"""
	logger.info("add_effects started, draft_id: %s", draft_id)

	script = require_draft(draft_id)
	effect_items = parse_effects_data(effect_infos)
	if len(effect_items) == 0:
		raise CustomException(CustomError.INVALID_EFFECT_INFO)

	track_name = f"effect_track_{uuid.uuid4().hex[:12]}"
	script.add_track(track_type=TrackType.effect, track_name=track_name)

	segment_ids: List[str] = []
	for effect in effect_items:
		segment_id, _ = add_effect_to_draft(script, track_name, effect)
		segment_ids.append(segment_id)

	script.save()

	return segment_ids


def add_effect_to_draft(script, track_name: str, effect: Dict[str, Any]) -> Tuple[str, str]:
	"""向草稿添加单个特效。"""
	try:
		effect_type = find_effect_type_by_name(effect["effect_title"])
		if effect_type is None:
			raise CustomException(CustomError.EFFECT_NOT_FOUND)

		effect_duration = effect["end"] - effect["start"]
		timerange = Timerange(start=effect["start"], duration=effect_duration)
		effect_segment = EffectSegment(effect_type=effect_type, target_timerange=timerange)
		script.add_segment(effect_segment, track_name)
		return effect_segment.segment_id, effect_segment.effect_inst.global_id
	except CustomException:
		raise
	except Exception as e:
		logger.error("Add effect failed: %s", e)
		raise CustomException(CustomError.EFFECT_ADD_FAILED, str(e))


def find_effect_type_by_name(effect_title: str) -> Optional[Union[VideoSceneEffectType, VideoCharacterEffectType]]:
	"""根据名称匹配特效类型（大小写不敏感，忽略空格/下划线差异）。"""
	try:
		return VideoSceneEffectType.from_name(effect_title)
	except Exception:
		pass
	try:
		return VideoCharacterEffectType.from_name(effect_title)
	except Exception:
		pass
	return None


def parse_effects_data(json_str: str) -> List[Dict[str, Any]]:
	"""解析并校验特效参数。"""
	try:
		data = json.loads(json_str)
	except json.JSONDecodeError as e:
		raise CustomException(CustomError.INVALID_EFFECT_INFO, f"JSON parse error: {e.msg}")

	if not isinstance(data, list):
		raise CustomException(CustomError.INVALID_EFFECT_INFO, "effect_infos should be a list")

	result = []
	for i, item in enumerate(data):
		if not isinstance(item, dict):
			raise CustomException(CustomError.INVALID_EFFECT_INFO, f"the {i}th item should be a dict")

		required_fields = ["effect_title", "start", "end"]
		missing_fields = [field for field in required_fields if field not in item]
		if missing_fields:
			raise CustomException(CustomError.INVALID_EFFECT_INFO, f"the {i}th item is missing required fields: {', '.join(missing_fields)}")

		processed_item = {
			"effect_title": str(item["effect_title"]),
			"start": int(item["start"]),
			"end": int(item["end"]),
		}

		if processed_item["start"] < 0:
			raise CustomException(CustomError.INVALID_EFFECT_INFO, f"the {i}th item has invalid start time")
		if processed_item["end"] <= processed_item["start"]:
			raise CustomException(CustomError.INVALID_EFFECT_INFO, f"the {i}th item has invalid end time")
		if len(processed_item["effect_title"].strip()) == 0:
			raise CustomException(CustomError.INVALID_EFFECT_INFO, f"the {i}th item has invalid effect_title")

		result.append(processed_item)

	return result
