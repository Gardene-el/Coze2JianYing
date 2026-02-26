from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE, update_draft_cache
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger
from app.backend.utils.cache import get_segment_cache, update_segment_cache


def _infer_track_type(segment) -> draft.TrackType:
	if isinstance(segment, draft.AudioSegment):
		return draft.TrackType.audio
	if isinstance(segment, draft.VideoSegment):
		return draft.TrackType.video
	if isinstance(segment, draft.StickerSegment):
		return draft.TrackType.sticker
	if isinstance(segment, draft.TextSegment):
		return draft.TrackType.text
	if isinstance(segment, draft.EffectSegment):
		return draft.TrackType.effect
	if isinstance(segment, draft.FilterSegment):
		return draft.TrackType.filter
	raise CustomException(CustomError.INVALID_SEGMENT_TYPE, type(segment).__name__)


def _make_unique_track_name(script: draft.ScriptFile, base: str) -> str:
	if base not in script.tracks:
		return base
	idx = 1
	while f"{base}_{idx}" in script.tracks:
		idx += 1
	return f"{base}_{idx}"


def _choose_track_name_for_segment(script: draft.ScriptFile, segment, track_index: Optional[int] = None) -> str:
	track_items = list(script.tracks.items())

	if track_index is not None:
		if track_index < 0 or track_index >= len(track_items):
			raise CustomException(CustomError.TRACK_NOT_FOUND, str(track_index))
		track_name, track = track_items[track_index]
		accept_type = track.accept_segment_type
		if accept_type is None or not isinstance(segment, accept_type):
			raise CustomException(CustomError.TRACK_TYPE_MISMATCH)
		return track_name

	for track_name, track in track_items:
		accept_type = track.accept_segment_type
		if accept_type is not None and isinstance(segment, accept_type):
			return track_name

	track_type = _infer_track_type(segment)
	new_track_name = _make_unique_track_name(script, track_type.name)
	script.add_track(track_type=track_type, track_name=new_track_name)
	return new_track_name


def add_segment(draft_url: str, segment_url: str, track_index: Optional[int] = None) -> str:
	"""将片段添加到草稿的目标轨道。"""
	draft_id = get_url_param(draft_url, "draft_id")
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)
	script = DRAFT_CACHE[draft_id]

	segment_id = get_url_param(segment_url, "segment_id")
	if not segment_id:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)
	segment = get_segment_cache(segment_id)
	if segment is None:
		raise CustomException(CustomError.SEGMENT_NOT_FOUND)

	logger.info("draft_id: %s, add segment: %s", draft_id, segment_id)

	try:
		track_name = _choose_track_name_for_segment(script, segment, track_index=track_index)
		script.add_segment(segment, track_name=track_name)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add segment failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_draft_cache(draft_id, script)
	update_segment_cache(segment_id, segment)
	logger.info("add segment success: draft=%s, segment=%s", draft_id, segment_id)
	return draft_url

