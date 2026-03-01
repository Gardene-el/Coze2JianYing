from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from pyJianYingDraft import ScriptFile
from pyJianYingDraft.keyframe import KeyframeProperty
from pyJianYingDraft.segment import VisualSegment

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.logger import logger


def add_keyframes(draft_id: str, keyframes: str) -> Tuple[str, int, List[str]]:
	"""批量添加关键帧。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)

	keyframe_items = parse_keyframes_data(keyframes)
	if len(keyframe_items) == 0:
		raise CustomException(CustomError.INVALID_KEYFRAME_INFO)

	script: ScriptFile = DRAFT_CACHE[draft_id]
	keyframes_added = 0
	affected_segments: List[str] = []

	for keyframe_item in keyframe_items:
		segment = find_segment_by_id(script, keyframe_item["segment_id"])
		if segment is None:
			continue
		if not isinstance(segment, VisualSegment):
			continue

		try:
			property_enum = KeyframeProperty(keyframe_item["property"])
		except ValueError:
			continue

		segment_duration = segment.duration
		offset_value = keyframe_item["offset"]
		relative_offset = max(0.0, min(1.0, offset_value / segment_duration))
		time_offset = int(relative_offset * segment_duration)
		segment.add_keyframe(property_enum, time_offset, keyframe_item["value"])

		keyframes_added += 1
		if keyframe_item["segment_id"] not in affected_segments:
			affected_segments.append(keyframe_item["segment_id"])

	try:
		script.save()
	except Exception as e:
		raise CustomException(CustomError.KEYFRAME_ADD_FAILED, str(e))

	return draft_id, keyframes_added, affected_segments


def find_segment_by_id(script: ScriptFile, segment_id: str) -> Optional[VisualSegment]:
	"""通过segment_id在草稿中查找片段。"""
	for _, track in script.tracks.items():
		for segment in track.segments:
			if segment.segment_id == segment_id:
				return segment
	return None


def parse_keyframes_data(json_str: str) -> List[Dict[str, Any]]:
	"""解析关键帧JSON并做基础校验。"""
	try:
		data = json.loads(json_str)
	except json.JSONDecodeError as e:
		raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"JSON parse error: {e.msg}")

	if not isinstance(data, list):
		raise CustomException(CustomError.INVALID_KEYFRAME_INFO, "keyframes should be a list")

	result = []
	supported_properties = {
		"KFTypePositionX",
		"KFTypePositionY",
		"KFTypeScaleX",
		"KFTypeScaleY",
		"KFTypeRotation",
		"KFTypeAlpha",
		"UNIFORM_SCALE",
		"KFTypeSaturation",
		"KFTypeContrast",
		"KFTypeBrightness",
		"KFTypeVolume",
	}

	for i, item in enumerate(data):
		if not isinstance(item, dict):
			raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"the {i}th item should be a dict")

		required_fields = ["segment_id", "property", "offset", "value"]
		missing_fields = [field for field in required_fields if field not in item]
		if missing_fields:
			raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"the {i}th item is missing required fields: {', '.join(missing_fields)}")

		if item["property"] not in supported_properties:
			raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"the {i}th item has unsupported property type: {item['property']}")
		if not isinstance(item["offset"], (int, float)) or item["offset"] < 0:
			raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"the {i}th item has invalid offset type or value: {item['offset']}")
		if not isinstance(item["value"], (int, float)):
			raise CustomException(CustomError.INVALID_KEYFRAME_INFO, f"the {i}th item has invalid value type: {type(item['value'])}")

		result.append(
			{
				"segment_id": str(item["segment_id"]),
				"property": item["property"],
				"offset": float(item["offset"]),
				"value": float(item["value"]),
			}
		)

	return result
