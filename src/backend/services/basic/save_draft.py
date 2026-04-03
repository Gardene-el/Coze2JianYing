from __future__ import annotations

import os

from src.backend.core.draft_store import require_draft_folder
from src.backend.utils.cache import require_draft
from src.backend.utils.logger import logger


def save_draft(draft_id: str) -> str:
	"""
	保存剪映草稿。

	Args:
		draft_id: 草稿ID

	Returns:
		draft_id
	"""
	script = require_draft(draft_id)
	script.save()

	logger.info("save draft success: %s", os.path.join(require_draft_folder(), draft_id))
	return draft_id

