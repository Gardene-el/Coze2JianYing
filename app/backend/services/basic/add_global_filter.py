from __future__ import annotations

import pyJianYingDraft as draft

from app.backend.core.common_types import TimeRange, to_draft_timerange
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE, update_draft_cache
from app.backend.utils.helper import get_url_param
from app.backend.utils.logger import logger


def _parse_filter_type(filter_type: str) -> draft.FilterType:
	name = str(filter_type or "").strip()
	if not name:
		raise ValueError("filter_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]
	return draft.FilterType.from_name(name)


def _first_track_name_by_type(script: draft.ScriptFile, track_type: draft.TrackType) -> str:
	for name, track in script.tracks.items():
		if track.track_type == track_type:
			return name

	new_track_name = track_type.name
	if new_track_name in script.tracks:
		idx = 1
		while f"{new_track_name}_{idx}" in script.tracks:
			idx += 1
		new_track_name = f"{new_track_name}_{idx}"

	script.add_track(track_type=track_type, track_name=new_track_name)
	return new_track_name


def add_global_filter(
	draft_url: str,
	filter_type: str,
	target_timerange: TimeRange,
	intensity: float = 100.0,
) -> str:
	"""向草稿添加全局滤镜片段。"""
	draft_id = get_url_param(draft_url, "draft_id")
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)
	script = DRAFT_CACHE[draft_id]

	logger.info("draft_id: %s, add global filter: %s", draft_id, filter_type)

	try:
		filter_meta = _parse_filter_type(filter_type)
		track_name = _first_track_name_by_type(script, draft.TrackType.filter)
		script.add_filter(
			filter_meta=filter_meta,
			t_range=to_draft_timerange(target_timerange),
			track_name=track_name,
			intensity=float(intensity),
		)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add global filter failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_draft_cache(draft_id, script)
	logger.info("add global filter success: %s", draft_id)
	return draft_url

