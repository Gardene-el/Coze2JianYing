from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Tuple

import pyJianYingDraft as draft
from pyJianYingDraft.metadata import GroupAnimationType, IntroType, OutroType, TransitionType

from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.schemas.easy.add_images import SegmentInfo
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.download import download
from app.backend.utils.logger import logger


def add_images(
	draft_id: str,
	image_infos: str,
	alpha: float = 1.0,
	scale_x: float = 1.0,
	scale_y: float = 1.0,
	transform_x: int = 0,
	transform_y: int = 0,
) -> Tuple[str, str, List[str], List[str], List[SegmentInfo]]:
	"""批量添加图片。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)

	settings = get_settings_manager()
	settings.reload()
	draft_dir = os.path.join(settings.get_effective_output_path(), draft_id)
	draft_image_dir = os.path.join(draft_dir, "assets", "images")
	os.makedirs(name=draft_image_dir, exist_ok=True)

	images = parse_image_data(image_infos)
	if len(images) == 0:
		raise CustomException(CustomError.INVALID_IMAGE_INFO)

	script = DRAFT_CACHE[draft_id]
	track_name = f"image_track_{uuid.uuid4().hex[:12]}"
	script.add_track(track_type=draft.TrackType.video, track_name=track_name, relative_index=10)

	segment_ids: List[str] = []
	segment_infos: List[SegmentInfo] = []
	for image in images:
		segment_id, segment_info = add_image_to_draft(
			script,
			track_name,
			draft_image_dir=draft_image_dir,
			image=image,
			alpha=alpha,
			scale_x=scale_x,
			scale_y=scale_y,
			transform_x=transform_x,
			transform_y=transform_y,
		)
		segment_ids.append(segment_id)
		segment_infos.append(segment_info)

	script.save()

	track_id = ""
	for key in script.tracks.keys():
		if script.tracks[key].name == track_name:
			track_id = script.tracks[key].track_id
			break

	image_ids = [video.material_id for video in script.materials.videos if video.material_type == "photo"]
	return draft_id, track_id, image_ids, segment_ids, segment_infos


def add_image_to_draft(
	script,
	track_name: str,
	draft_image_dir: str,
	image: Dict[str, Any],
	alpha: float = 1.0,
	scale_x: float = 1.0,
	scale_y: float = 1.0,
	transform_x: int = 0,
	transform_y: int = 0,
) -> Tuple[str, SegmentInfo]:
	"""向草稿添加单张图片。"""
	try:
		image_path = download(url=image["image_url"], save_dir=draft_image_dir)
		segment_duration = image["end"] - image["start"]

		clip_settings = draft.ClipSettings(
			alpha=alpha,
			scale_x=scale_x,
			scale_y=scale_y,
			transform_x=transform_x / image["width"],
			transform_y=transform_y / image["height"],
		)

		video_segment = draft.VideoSegment(
			material=image_path,
			target_timerange=draft.trange(start=image["start"], duration=segment_duration),
			clip_settings=clip_settings,
		)

		if image.get("in_animation"):
			intro_enum = map_video_animation_name_to_enum(image["in_animation"], "in")
			if intro_enum:
				in_duration = image.get("in_animation_duration")
				video_segment.add_animation(intro_enum, duration=int(in_duration) if in_duration not in (None, "") else None)

		if image.get("out_animation"):
			outro_enum = map_video_animation_name_to_enum(image["out_animation"], "out")
			if outro_enum:
				out_duration = image.get("out_animation_duration")
				video_segment.add_animation(outro_enum, duration=int(out_duration) if out_duration not in (None, "") else None)

		if image.get("loop_animation"):
			group_enum = map_video_animation_name_to_enum(image["loop_animation"], "group")
			if group_enum:
				group_duration = image.get("loop_animation_duration")
				video_segment.add_animation(group_enum, duration=int(group_duration) if group_duration not in (None, "") else None)

		if image.get("transition"):
			transition_enum = None
			for attr_name in dir(TransitionType):
				attr = getattr(TransitionType, attr_name)
				if isinstance(attr, TransitionType) and attr.value.name == image["transition"]:
					transition_enum = attr
					break
			if transition_enum:
				transition_duration = image.get("transition_duration")
				video_segment.add_transition(transition_enum, duration=int(transition_duration) if transition_duration is not None else None)

		script.add_segment(video_segment, track_name)
		segment_info = SegmentInfo(id=video_segment.segment_id, start=image["start"], end=image["end"])
		return video_segment.segment_id, segment_info
	except CustomException:
		raise
	except Exception as e:
		logger.error("Add image failed: %s", e)
		raise CustomException(CustomError.IMAGE_ADD_FAILED, str(e))


def map_video_animation_name_to_enum(animation_name: str, animation_type: str):
	"""将动画名称映射为动画枚举。"""
	in_animation_map = {}
	for attr_name in dir(IntroType):
		attr = getattr(IntroType, attr_name)
		if isinstance(attr, IntroType):
			in_animation_map[attr.value.title] = attr

	out_animation_map = {}
	for attr_name in dir(OutroType):
		attr = getattr(OutroType, attr_name)
		if isinstance(attr, OutroType):
			out_animation_map[attr.value.title] = attr

	group_animation_map = {}
	for attr_name in dir(GroupAnimationType):
		attr = getattr(GroupAnimationType, attr_name)
		if isinstance(attr, GroupAnimationType):
			group_animation_map[attr.value.title] = attr

	if animation_type == "in":
		return in_animation_map.get(animation_name)
	if animation_type == "out":
		return out_animation_map.get(animation_name)
	if animation_type == "group":
		return group_animation_map.get(animation_name)
	return None


def parse_image_data(json_str: str) -> List[Dict[str, Any]]:
	"""解析并校验图片参数。"""
	try:
		data = json.loads(json_str)
	except json.JSONDecodeError as e:
		raise CustomException(CustomError.INVALID_IMAGE_INFO, f"JSON parse error: {e.msg}")

	if not isinstance(data, list):
		raise CustomException(CustomError.INVALID_IMAGE_INFO, "image_infos should be a list")

	result = []
	for i, item in enumerate(data):
		if not isinstance(item, dict):
			raise CustomException(CustomError.INVALID_IMAGE_INFO, f"the {i}th item should be a dict")

		required_fields = ["image_url", "width", "height", "start", "end"]
		missing_fields = [field for field in required_fields if field not in item]
		if missing_fields:
			raise CustomException(CustomError.INVALID_IMAGE_INFO, f"the {i}th item is missing required fields: {', '.join(missing_fields)}")

		processed_item = {
			"image_url": item["image_url"],
			"width": int(item["width"]),
			"height": int(item["height"]),
			"start": int(item["start"]),
			"end": int(item["end"]),
			"in_animation": item.get("in_animation", None),
			"out_animation": item.get("out_animation", None),
			"loop_animation": item.get("loop_animation", None),
			"in_animation_duration": item.get("in_animation_duration", None),
			"out_animation_duration": item.get("out_animation_duration", None),
			"loop_animation_duration": item.get("loop_animation_duration", None),
			"transition": item.get("transition", None),
			"transition_duration": int(item.get("transition_duration", 500000)),
		}

		if processed_item["width"] <= 0 or processed_item["height"] <= 0:
			raise CustomException(CustomError.INVALID_IMAGE_INFO, f"the {i}th item has invalid image dimensions")
		if processed_item["start"] < 0 or processed_item["end"] <= processed_item["start"]:
			raise CustomException(CustomError.INVALID_IMAGE_INFO, f"the {i}th item has invalid time range")
		if processed_item["transition_duration"] < 100000 or processed_item["transition_duration"] > 2500000:
			processed_item["transition_duration"] = 500000

		result.append(processed_item)

	return result
