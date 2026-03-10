from __future__ import annotations

from fastapi import APIRouter

from app.backend.schemas.easy.add_audios import AddAudiosRequest, AddAudiosResponse
from app.backend.schemas.easy.add_captions import AddCaptionsRequest, AddCaptionsResponse
from app.backend.schemas.easy.add_effects import AddEffectsRequest, AddEffectsResponse
from app.backend.schemas.easy.add_images import AddImagesRequest, AddImagesResponse
from app.backend.schemas.easy.add_keyframes import AddKeyframesRequest, AddKeyframesResponse
from app.backend.schemas.easy.add_masks import AddMasksRequest, AddMasksResponse
from app.backend.schemas.easy.add_videos import AddVideosRequest, AddVideosResponse
from app.backend.services import easy as service


router = APIRouter(tags=["easy"])


@router.post(path="/drafts/{draft_id}/add_audios", response_model=AddAudiosResponse)
def add_audios(draft_id: str, request: AddAudiosRequest) -> AddAudiosResponse:
	segment_ids = service.add_audios(
		draft_id=draft_id,
		audio_infos=request.audio_infos,
	)
	return AddAudiosResponse(segment_ids=segment_ids)


@router.post(path="/drafts/{draft_id}/add_captions", response_model=AddCaptionsResponse)
def add_captions(draft_id: str, request: AddCaptionsRequest) -> AddCaptionsResponse:
	segment_ids = service.add_captions(
		draft_id=draft_id,
		captions=request.captions,
		text_color=request.text_color,
		border_color=request.border_color,
		alignment=request.alignment,
		alpha=request.alpha,
		font=request.font,
		font_size=request.font_size,
		letter_spacing=request.letter_spacing,
		line_spacing=request.line_spacing,
		scale_x=request.scale_x,
		scale_y=request.scale_y,
		transform_x=request.transform_x,
		transform_y=request.transform_y,
		style_text=request.style_text,
		underline=request.underline,
		italic=request.italic,
		bold=request.bold,
		has_shadow=request.has_shadow,
		shadow_info=request.shadow_info,
	)
	return AddCaptionsResponse(
		segment_ids=segment_ids,
	)


@router.post(path="/drafts/{draft_id}/add_videos", response_model=AddVideosResponse)
def add_videos(draft_id: str, request: AddVideosRequest) -> AddVideosResponse:
	segment_ids = service.add_videos(
		draft_id=draft_id,
		video_infos=request.video_infos,
		alpha=request.alpha,
		scale_x=request.scale_x,
		scale_y=request.scale_y,
		transform_x=request.transform_x,
		transform_y=request.transform_y,
	)
	return AddVideosResponse(segment_ids=segment_ids)


@router.post(path="/drafts/{draft_id}/add_images", response_model=AddImagesResponse)
def add_images(draft_id: str, request: AddImagesRequest) -> AddImagesResponse:
	segment_ids = service.add_images(
		draft_id=draft_id,
		image_infos=request.image_infos,
		alpha=request.alpha,
		scale_x=request.scale_x,
		scale_y=request.scale_y,
		transform_x=request.transform_x,
		transform_y=request.transform_y,
	)
	return AddImagesResponse(
		segment_ids=segment_ids,
	)


@router.post(path="/drafts/{draft_id}/add_effects", response_model=AddEffectsResponse)
def add_effects(draft_id: str, request: AddEffectsRequest) -> AddEffectsResponse:
	segment_ids = service.add_effects(
		draft_id=draft_id,
		effect_infos=request.effect_infos,
	)
	return AddEffectsResponse(segment_ids=segment_ids)


@router.post(path="/drafts/{draft_id}/add_masks", response_model=AddMasksResponse)
def add_masks(draft_id: str, request: AddMasksRequest) -> AddMasksResponse:
	service.add_masks(
		draft_id=draft_id,
		segment_ids=request.segment_ids,
		name=request.name,
		X=request.X,
		Y=request.Y,
		width=request.width,
		height=request.height,
		feather=request.feather,
		rotation=request.rotation,
		invert=request.invert,
		round_corner=request.round_corner,
	)
	return AddMasksResponse()


@router.post(path="/drafts/{draft_id}/add_keyframes", response_model=AddKeyframesResponse)
def add_keyframes(draft_id: str, request: AddKeyframesRequest) -> AddKeyframesResponse:
	service.add_keyframes(
		draft_id=draft_id,
		keyframes=request.keyframes,
	)
	return AddKeyframesResponse()
