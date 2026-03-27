from __future__ import annotations

import os

from src.backend.core.settings_manager import get_settings_manager
from src.backend.exceptions import CustomError, CustomException
from src.backend.utils.cache import DRAFT_CACHE
from src.backend.utils.logger import logger


def save_draft(draft_id: str) -> str:
	"""
	保存剪映草稿。

	Args:
		draft_id: 草稿ID

	Returns:
		draft_id
	"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		logger.info("invalid draft id: %s", draft_id)
		raise CustomException(CustomError.INVALID_DRAFT_URL)

	script = DRAFT_CACHE[draft_id]
	script.save()

	logger.info("save draft success: %s", os.path.join(get_settings_manager().require("effective_output_path"), draft_id))
	return draft_id

