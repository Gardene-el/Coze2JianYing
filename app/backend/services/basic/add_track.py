from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE, update_draft_cache
from app.backend.utils.logger import logger


def _parse_track_type(track_type: str) -> draft.TrackType:
	name = str(track_type or "").strip()
	if not name:
		raise ValueError("track_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.TrackType.from_name(name)


def add_track(
	draft_id: str,
	track_type: str,
	track_name: Optional[str] = None,
	*,
	mute: bool = False,
	relative_index: int = 0,
	absolute_index: Optional[int] = None,
) -> None:
	"""向草稿添加轨道。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)
	script = DRAFT_CACHE[draft_id]

	logger.info("draft_id: %s, add track: %s", draft_id, track_type)

	try:
		parsed_track_type = _parse_track_type(track_type)
		script.add_track(
			track_type=parsed_track_type,
			track_name=track_name,
			mute=mute,
			relative_index=relative_index,
			absolute_index=absolute_index,
		)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add track failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_draft_cache(draft_id, script)
	logger.info("add track success: %s", draft_id)

