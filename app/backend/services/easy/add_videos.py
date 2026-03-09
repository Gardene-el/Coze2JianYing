from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional

import pyJianYingDraft as draft

from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.download import download
from app.backend.utils.logger import logger


def add_videos(
	draft_id: str,
	video_infos: str,
	alpha: float = 1.0,
	scale_x: float = 1.0,
	scale_y: float = 1.0,
	transform_x: int = 0,
	transform_y: int = 0,
) -> List[str]:
	"""批量添加视频。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)

	settings = get_settings_manager()
	settings.reload()
	draft_dir = os.path.join(settings.get_effective_output_path(), draft_id)
	draft_video_dir = os.path.join(draft_dir, "assets", "videos")
	os.makedirs(name=draft_video_dir, exist_ok=True)

	videos = parse_video_data(video_infos)
	if len(videos) == 0:
		raise CustomException(CustomError.INVALID_VIDEO_INFO)

	script = DRAFT_CACHE[draft_id]
	track_name = f"video_track_{uuid.uuid4().hex[:12]}"
	script.add_track(track_type=draft.TrackType.video, track_name=track_name, relative_index=10)

	segment_ids = []
	for video in videos:
		segment_id = add_video_to_draft(
			script,
			track_name,
			draft_video_dir=draft_video_dir,
			video=video,
			alpha=alpha,
			scale_x=scale_x,
			scale_y=scale_y,
			transform_x=transform_x,
			transform_y=transform_y,
		)
		segment_ids.append(segment_id)

	script.save()

	return segment_ids


def add_video_to_draft(
	script,
	track_name: str,
	draft_video_dir: str,
	video: Dict[str, Any],
	alpha: float = 1.0,
	scale_x: float = 1.0,
	scale_y: float = 1.0,
	transform_x: int = 0,
	transform_y: int = 0,
) -> str:
	"""向草稿添加单个视频。"""
	try:
		video_path = download(url=video["video_url"], save_dir=draft_video_dir)
		video_material = draft.VideoMaterial(video_path)

		video_width = video.get("width")
		video_height = video.get("height")
		if video_width is None or video_height is None:
			video_width = video_material.width
			video_height = video_material.height

		display_duration = video["end"] - video["start"]
		clip_settings = draft.ClipSettings(
			alpha=alpha,
			scale_x=scale_x,
			scale_y=scale_y,
			transform_x=transform_x / video_width,
			transform_y=transform_y / video_height,
		)

		video_segment = draft.VideoSegment(
			material=video_material,
			target_timerange=draft.trange(start=video["start"], duration=display_duration),
			source_timerange=draft.trange(start=0, duration=min(video_material.duration, display_duration)),
			speed=1.0,
			volume=video.get("volume", 1.0),
			clip_settings=clip_settings,
		)

		transition_name = video.get("transition")
		if transition_name:
			transition_type = find_transition_type_by_name(transition_name)
			if transition_type:
				transition_duration = video.get("transition_duration", 500000)
				video_segment.add_transition(transition_type, duration=transition_duration)

		script.add_segment(video_segment, track_name)
		return video_segment.segment_id
	except CustomException:
		raise
	except Exception as e:
		logger.error("Add video failed: %s", e)
		raise CustomException(CustomError.VIDEO_ADD_FAILED, str(e))


def find_transition_type_by_name(transition_name: str) -> Optional[draft.TransitionType]:
	"""根据转场名称查找转场类型。"""
	if not transition_name:
		return None
	try:
		return draft.TransitionType.from_name(transition_name)
	except Exception:
		return None


def parse_video_data(json_str: str) -> List[Dict[str, Any]]:
	"""解析并校验视频参数。"""
	try:
		data = json.loads(json_str)
	except json.JSONDecodeError as e:
		raise CustomException(CustomError.INVALID_VIDEO_INFO, f"JSON parse error: {e.msg}")

	if not isinstance(data, list):
		raise CustomException(CustomError.INVALID_VIDEO_INFO, "video_infos should be a list")

	result = []
	for i, item in enumerate(data):
		if not isinstance(item, dict):
			raise CustomException(CustomError.INVALID_VIDEO_INFO, f"the {i}th item should be a dict")

		required_fields = ["video_url", "start", "end"]
		missing_fields = [field for field in required_fields if field not in item]
		if missing_fields:
			raise CustomException(CustomError.INVALID_VIDEO_INFO, f"the {i}th item is missing required fields: {', '.join(missing_fields)}")

		duration = item.get("duration", item["end"] - item["start"])
		processed_item = {
			"video_url": item["video_url"],
			"width": item.get("width"),
			"height": item.get("height"),
			"start": int(item["start"]),
			"end": int(item["end"]),
			"duration": int(duration),
			"mask": item.get("mask", None),
			"transition": item.get("transition", None),
			"transition_duration": int(item.get("transition_duration", 500000)),
			"volume": float(item.get("volume", 1.0)),
		}

		if processed_item["volume"] < 0 or processed_item["volume"] > 1:
			processed_item["volume"] = 1.0
		if processed_item["transition_duration"] < 0:
			processed_item["transition_duration"] = 500000

		result.append(processed_item)

	return result
