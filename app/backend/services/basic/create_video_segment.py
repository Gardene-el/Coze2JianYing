from __future__ import annotations

import os
from typing import Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import (
	ClipSettings,
	CropSettings,
	TimeRange,
	to_draft_clip_settings,
	to_draft_crop_settings,
	to_draft_timerange,
)
from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.download import download
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def create_video_segment(
	material_url: str,
	target_timerange: TimeRange,
	source_timerange: Optional[TimeRange] = None,
	speed: float = 1.0,
	volume: float = 1.0,
	change_pitch: bool = False,
	clip_settings: Optional[ClipSettings] = None,
	crop_settings: Optional[CropSettings] = None,
) -> str:
	"""创建视频片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create video segment from: %s", segment_id, material_url)

	try:
		settings = get_settings_manager()
		settings.reload()
		output_dir = settings.get_effective_output_path()
		draft_video_dir = create_video_directory(output_dir, segment_id)
		video_path = download_video_file(material_url, draft_video_dir)
		video_material = create_video_material(video_path, crop_settings)

		segment = draft.VideoSegment(
			material=video_material,
			target_timerange=to_draft_timerange(target_timerange),
			source_timerange=to_draft_timerange(source_timerange) if source_timerange is not None else None,
			speed=speed,
			volume=volume,
			change_pitch=change_pitch,
			clip_settings=to_draft_clip_settings(clip_settings) if clip_settings is not None else None,
		)

	except Exception as e:
		logger.error("create video segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create video segment success: %s", segment_id)
	return segment_id


def create_video_directory(output_dir: str, segment_id: str) -> str:
	"""创建视频资源目录。"""
	draft_video_dir = os.path.join(output_dir, "CozeJianYingAssistantAssets", segment_id)
	os.makedirs(name=draft_video_dir, exist_ok=True)
	return draft_video_dir


def download_video_file(material_url: str, draft_video_dir: str) -> str:
	"""下载视频文件并返回本地路径。"""
	video_path = download(url=material_url, save_dir=draft_video_dir)
	logger.info("Downloaded video from %s to %s", material_url, video_path)
	return video_path


def create_video_material(video_path: str, crop_settings: Optional[CropSettings]) -> draft.VideoMaterial:
	"""根据本地路径构建视频素材对象。"""
	if crop_settings is not None:
		return draft.VideoMaterial(video_path, crop_settings=to_draft_crop_settings(crop_settings))
	return draft.VideoMaterial(video_path)

