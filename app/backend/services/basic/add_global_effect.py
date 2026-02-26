from __future__ import annotations

from typing import Optional

import pyJianYingDraft as draft

from app.backend.core.common_types import TimeRange, to_draft_timerange
from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE, update_draft_cache
from app.backend.utils.logger import logger


def _parse_effect_type(effect_type: str):
	name = str(effect_type or "").strip()
	if not name:
		raise ValueError("effect_type 不能为空")
	if "." in name:
		name = name.split(".")[-1]

	try:
		return draft.VideoSceneEffectType.from_name(name)
	except Exception:
		return draft.VideoCharacterEffectType.from_name(name)


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


def add_global_effect(
	draft_id: str,
	effect_type: str,
	target_timerange: TimeRange,
	params: Optional[list[float | None]] = None,
) -> None:
	"""向草稿添加全局特效片段。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)
	script = DRAFT_CACHE[draft_id]

	logger.info("draft_id: %s, add global effect: %s", draft_id, effect_type)

	try:
		effect = _parse_effect_type(effect_type)
		track_name = _first_track_name_by_type(script, draft.TrackType.effect)
		script.add_effect(
			effect=effect,
			t_range=to_draft_timerange(target_timerange),
			track_name=track_name,
			params=params,
		)
	except CustomException:
		raise
	except Exception as e:
		logger.error("add global effect failed: %s", e)
		raise CustomException(CustomError.PARAM_VALIDATION_FAILED, str(e))

	update_draft_cache(draft_id, script)
	logger.info("add global effect success: %s", draft_id)

