from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from src.backend.exceptions import CustomError, CustomException
from src.backend.utils.cache import SEGMENT_CACHE, require_draft, require_segment, update_draft_cache
from src.backend.utils.logger import logger


def add_segment(draft_id: str, segment_id: str, track_name: Optional[str] = None) -> None:
	script = require_draft(draft_id)

	segment = require_segment(
		segment_id,
		(draft.VideoSegment, draft.StickerSegment, draft.AudioSegment, draft.TextSegment),
	)

	logger.info("draft_id: %s, add segment: %s", draft_id, segment_id)

	try:
		script.add_segment(segment, track_name)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_draft_cache(draft_id, script)
	SEGMENT_CACHE.pop(segment_id, None)
	logger.info("add segment success: draft=%s, segment=%s", draft_id, segment_id)

