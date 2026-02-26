from __future__ import annotations

import os

from app.backend.config import get_config
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.logger import logger


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

	config = get_config()
	logger.info("save draft success: %s", os.path.join(config.drafts_dir, draft_id))
	return draft_id

