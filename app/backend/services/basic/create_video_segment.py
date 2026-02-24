from __future__ import annotations

from typing import Any, Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import (
	ClipSettings,
	CropSettings,
	TimeRange,
	parse_common_model,
	to_draft_clip_settings,
	to_draft_crop_settings,
	to_draft_timerange,
)
from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.services.material import MaterialService
from app.backend.utils.cache import update_segment_cache
from app.backend.utils.helper import gen_unique_id
from app.backend.utils.logger import logger


def create_video_segment(
	material_url: str,
	target_timerange: Any,
	source_timerange: Optional[Any] = None,
	speed: float = 1.0,
	volume: float = 1.0,
	change_pitch: bool = False,
	clip_settings: Optional[Any] = None,
	crop_settings: Optional[Any] = None,
) -> str:
	"""创建视频片段并写入缓存。"""
	segment_id = gen_unique_id()
	logger.info("segment_id: %s, create video segment from: %s", segment_id, material_url)

	try:
		target_range = parse_common_model(TimeRange, target_timerange)
		source_range = parse_common_model(TimeRange, source_timerange) if source_timerange is not None else None
		clip_model = parse_common_model(ClipSettings, clip_settings) if clip_settings is not None else None
		crop_model = parse_common_model(CropSettings, crop_settings) if crop_settings is not None else None

		settings = get_settings_manager()
		settings.reload()
		output_dir = settings.get_effective_output_path()

		material_service = MaterialService(output_dir, draft_name=segment_id, project_id=segment_id)

		if crop_model is not None:
			local_path = material_service.download_material(material_url)
			video_material = draft.VideoMaterial(local_path, crop_settings=to_draft_crop_settings(crop_model))
		else:
			video_material = material_service.create_video_material(material_url)

		segment = draft.VideoSegment(
			material=video_material,
			target_timerange=to_draft_timerange(target_range),
			source_timerange=to_draft_timerange(source_range) if source_range is not None else None,
			speed=speed,
			volume=volume,
			change_pitch=change_pitch,
			clip_settings=to_draft_clip_settings(clip_model) if clip_model is not None else None,
		)

	except Exception as e:
		logger.error("create video segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_segment_cache(segment_id, segment)
	logger.info("create video segment success: %s", segment_id)
	return f"draft://coze2jianying/basic/create_video_segment?segment_id={segment_id}"

