from __future__ import annotations

from typing import List, Optional, Tuple

from pyJianYingDraft import MaskType, ScriptFile
from pyJianYingDraft.segment import VisualSegment
from pyJianYingDraft.video_segment import VideoSegment

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.cache import DRAFT_CACHE
from app.backend.utils.logger import logger


def add_masks(
	draft_id: str,
	segment_ids: List[str],
	name: str = "线性",
	X: int = 0,
	Y: int = 0,
	width: int = 512,
	height: int = 512,
	feather: int = 0,
	rotation: int = 0,
	invert: bool = False,
	roundCorner: int = 0,
) -> Tuple[int, List[str]]:
	"""批量添加遮罩。"""
	if (not draft_id) or (draft_id not in DRAFT_CACHE):
		raise CustomException(CustomError.INVALID_DRAFT_URL)
	if not segment_ids:
		raise CustomException(CustomError.INVALID_MASK_INFO)

	script: ScriptFile = DRAFT_CACHE[draft_id]
	mask_type = find_mask_type_by_name(name)
	if mask_type is None:
		raise CustomException(CustomError.MASK_NOT_FOUND)

	masks_added = 0
	affected_segments: List[str] = []

	for segment_id in segment_ids:
		add_mask_to_segment(
			script=script,
			segment_id=segment_id,
			mask_type=mask_type,
			center_x=X,
			center_y=Y,
			width=width,
			height=height,
			feather=feather,
			rotation=rotation,
			invert=invert,
			round_corner=roundCorner,
		)
		masks_added += 1
		affected_segments.append(segment_id)

	script.save()
	return masks_added, affected_segments


def add_mask_to_segment(
	script: ScriptFile,
	segment_id: str,
	mask_type: MaskType,
	center_x: int = 0,
	center_y: int = 0,
	width: int = 512,
	height: int = 512,
	feather: int = 0,
	rotation: int = 0,
	invert: bool = False,
	round_corner: int = 0,
) -> str:
	"""向指定片段添加遮罩。"""
	try:
		segment = find_segment_by_id(script, segment_id)
		if segment is None:
			raise CustomException(CustomError.SEGMENT_NOT_FOUND)
		if not isinstance(segment, VideoSegment):
			raise CustomException(CustomError.INVALID_SEGMENT_TYPE)

		if segment.mask is not None:
			return segment.mask.global_id

		material_width, material_height = segment.material_size
		size = height / material_height
		rect_width = width / material_width if mask_type == MaskType.矩形 else None

		if mask_type == MaskType.矩形:
			segment.add_mask(
				mask_type=mask_type,
				center_x=float(center_x),
				center_y=float(center_y),
				size=size,
				rotation=float(rotation),
				feather=float(feather),
				invert=invert,
				rect_width=rect_width,
				round_corner=float(round_corner),
			)
		else:
			segment.add_mask(
				mask_type=mask_type,
				center_x=float(center_x),
				center_y=float(center_y),
				size=size,
				rotation=float(rotation),
				feather=float(feather),
				invert=invert,
			)

		mask_id = segment.mask.global_id if segment.mask is not None else ""
		if not mask_id:
			raise CustomException(CustomError.MASK_ADD_FAILED)
		return mask_id
	except CustomException:
		raise
	except Exception as e:
		logger.error("Add mask failed: %s", e)
		raise CustomException(CustomError.MASK_ADD_FAILED, str(e))


def find_segment_by_id(script: ScriptFile, segment_id: str) -> Optional[VisualSegment]:
	"""在草稿所有轨道中查找片段。"""
	for _, track in script.tracks.items():
		for segment in track.segments:
			if segment.segment_id == segment_id:
				return segment
	return None


def find_mask_type_by_name(mask_name: str) -> Optional[MaskType]:
	"""根据遮罩名匹配遮罩类型。"""
	for mask_type in MaskType:
		if mask_type.value.name == mask_name:
			return mask_type
	return None
