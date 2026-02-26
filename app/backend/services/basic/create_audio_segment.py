from __future__ import annotations

import os
from typing import Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import TimeRange, to_draft_timerange
from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.download import download
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def create_audio_segment(
	material_url: str,
	target_timerange: TimeRange,
	source_timerange: Optional[TimeRange] = None,
	speed: float = 1.0,
	volume: float = 1.0,
	change_pitch: bool = False,
) -> str:
	"""创建音频片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create audio segment from: %s", segment_id, material_url)

	try:
		settings = get_settings_manager()
		settings.reload()
		output_dir = settings.get_effective_output_path()
		draft_audio_dir = create_audio_directory(output_dir, segment_id)
		audio_path = download_audio_file(material_url, draft_audio_dir)

		segment = draft.AudioSegment(
			material=audio_path,
			target_timerange=to_draft_timerange(target_timerange),
			source_timerange=to_draft_timerange(source_timerange) if source_timerange is not None else None,
			speed=speed,
			volume=volume,
			change_pitch=change_pitch,
		)

	except Exception as e:
		logger.error("create audio segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create audio segment success: %s", segment_id)
	return segment_id


def create_audio_directory(output_dir: str, segment_id: str) -> str:
	"""创建音频资源目录。"""
	draft_audio_dir = os.path.join(output_dir, "CozeJianYingAssistantAssets", segment_id)
	os.makedirs(name=draft_audio_dir, exist_ok=True)
	return draft_audio_dir


def download_audio_file(material_url: str, draft_audio_dir: str) -> str:
	"""下载音频文件并返回本地路径。"""
	audio_path = download(url=material_url, save_dir=draft_audio_dir)
	logger.info("Downloaded audio from %s to %s", material_url, audio_path)
	return audio_path

