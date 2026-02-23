from __future__ import annotations

import datetime
import os
import uuid

import pyJianYingDraft as draft

from app.backend.core.settings_manager import get_settings_manager
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import update_draft_cache
from app.backend.utils.logger import logger


def create_draft(width: int, height: int) -> str:
	"""
	基于草稿模板能力创建剪映草稿。

	Args:
		width: 草稿宽度
		height: 草稿高度

	Returns:
		草稿URL（包含 draft_id 查询参数）

	Raises:
		CustomException: 草稿创建失败
	"""
	timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
	unique_id = uuid.uuid4().hex[:8]
	draft_id = f"{timestamp}{unique_id}"
	logger.info("draft_id: %s, width: %s, height: %s", draft_id, width, height)

	try:
		settings = get_settings_manager()
		settings.reload()
		output_dir = settings.get_effective_output_path()

		draft_folder = draft.DraftFolder(output_dir)
		script = draft_folder.create_draft(
			draft_name=draft_id,
			width=width,
			height=height,
			fps=30,
			allow_replace=True,
		)

		script.content["canvas_config"]["width"] = width
		script.content["canvas_config"]["height"] = height

		main_track_name = "main_track"
		script.add_track(track_type=draft.TrackType.video, track_name=main_track_name, relative_index=0)
		logger.info("Added empty main track: %s", main_track_name)

		script.save()

		draft_dir = os.path.join(output_dir, draft_id)
		draft_info_path = os.path.join(draft_dir, "draft_info.json")
		script.dump(draft_info_path)

	except Exception as e:
		logger.error("create draft failed: %s", e)
		raise CustomException(CustomError.DRAFT_CREATE_FAILED, str(e))

	update_draft_cache(draft_id, script)
	logger.info("create draft success: %s", draft_id)
	return f"draft://coze2jianying/basic/create_draft?draft_id={draft_id}"

