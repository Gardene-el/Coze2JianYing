from __future__ import annotations

import os
from typing import Optional

import pyJianYingDraft as draft

from src.backend.core.settings_manager import get_settings_manager
from src.backend.exceptions import CustomError, CustomException
from src.backend.utils.cache import update_draft_cache
from src.backend.utils.helper import gen_unique_id
from src.backend.utils.logger import logger


def create_draft(width: int, height: int, fps: int = 30, draft_name: Optional[str] = None) -> str:
	"""
	基于草稿模板能力创建剪映草稿。

	Args:
		width: 草稿宽度
		height: 草稿高度
		fps: 视频帧率，默认30
		draft_name: 草稿名称（即剪映中显示的名称），默认使用生成的唯一 ID

	Returns:
		草稿ID

	Raises:
		CustomException: 草稿创建失败
	"""
	draft_id = gen_unique_id()
	logger.info("draft_id: %s, draft_name: %s, width: %s, height: %s, fps: %s", draft_id, draft_name, width, height, fps)

	try:
		settings = get_settings_manager()
		output_dir = settings.require("draft_folder")

		draft_folder = draft.DraftFolder(output_dir)
		script = draft_folder.create_draft(
			draft_name=draft_name or draft_id,
			width=width,
			height=height,
			fps=fps,
			allow_replace=True,
		)

		main_track_name = "main_track"
		script.add_track(track_type=draft.TrackType.video, track_name=main_track_name, relative_index=0)
		logger.info("Added empty main track: %s", main_track_name)

		script.save()

	except Exception as e:
		logger.error("create draft failed: %s", e)
		raise CustomException(CustomError.DRAFT_CREATE_FAILED, str(e))

	update_draft_cache(draft_id, script)
	logger.info("create draft success: %s", draft_id)
	return draft_id

