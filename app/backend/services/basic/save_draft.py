from __future__ import annotations

import os

from app.backend.config import get_config
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger


def save_draft(draft_url: str) -> str:
	"""
	保存剪映草稿。

	Args:
		draft_url: 草稿URL（需包含 draft_id 查询参数）

	Returns:
		draft_url
	"""
	draft_id = get_url_param(draft_url, "draft_id")
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		logger.info("invalid draft url: %s", draft_url)
		raise CustomException(CustomError.INVALID_DRAFT_URL)

	script = DRAFT_CACHE[draft_id]
	script.save()

	config = get_config()
	logger.info("save draft success: %s", os.path.join(config.drafts_dir, draft_id))
	return draft_url

