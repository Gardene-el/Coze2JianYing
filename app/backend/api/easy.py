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


@router.post(path="/add_audios", response_model=AddAudiosResponse)
def add_audios(request: AddAudiosRequest) -> AddAudiosResponse:
	draft_id, track_id, audio_ids = service.add_audios(
		draft_id=request.draft_id,
		audio_infos=request.audio_infos,
	)
	return AddAudiosResponse(draft_id=draft_id, track_id=track_id, audio_ids=audio_ids)


@router.post(path="/add_captions", response_model=AddCaptionsResponse)
def add_captions(request: AddCaptionsRequest) -> AddCaptionsResponse:
	draft_id, track_id, text_ids, segment_ids, segment_infos = service.add_captions(
		draft_id=request.draft_id,
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
		draft_id=draft_id,
		track_id=track_id,
		text_ids=text_ids,
		segment_ids=segment_ids,
		segment_infos=segment_infos,
	)


@router.post(path="/add_videos", response_model=AddVideosResponse)
def add_videos(request: AddVideosRequest) -> AddVideosResponse:
	draft_id, track_id, video_ids, segment_ids = service.add_videos(
		draft_id=request.draft_id,
		video_infos=request.video_infos,
		alpha=request.alpha,
		scale_x=request.scale_x,
		scale_y=request.scale_y,
		transform_x=request.transform_x,
		transform_y=request.transform_y,
	)
	return AddVideosResponse(draft_id=draft_id, track_id=track_id, video_ids=video_ids, segment_ids=segment_ids)


@router.post(path="/add_images", response_model=AddImagesResponse)
def add_images(request: AddImagesRequest) -> AddImagesResponse:
	draft_id, track_id, image_ids, segment_ids, segment_infos = service.add_images(
		draft_id=request.draft_id,
		image_infos=request.image_infos,
		alpha=request.alpha,
		scale_x=request.scale_x,
		scale_y=request.scale_y,
		transform_x=request.transform_x,
		transform_y=request.transform_y,
	)
	return AddImagesResponse(
		draft_id=draft_id,
		track_id=track_id,
		image_ids=image_ids,
		segment_ids=segment_ids,
		segment_infos=segment_infos,
	)


@router.post(path="/add_effects", response_model=AddEffectsResponse)
def add_effects(request: AddEffectsRequest) -> AddEffectsResponse:
	draft_id, track_id, effect_ids, segment_ids = service.add_effects(
		draft_id=request.draft_id,
		effect_infos=request.effect_infos,
	)
	return AddEffectsResponse(draft_id=draft_id, track_id=track_id, effect_ids=effect_ids, segment_ids=segment_ids)


@router.post(path="/add_masks", response_model=AddMasksResponse)
def add_masks(request: AddMasksRequest) -> AddMasksResponse:
	draft_id, masks_added, affected_segments, mask_ids = service.add_masks(
		draft_id=request.draft_id,
		segment_ids=request.segment_ids,
		name=request.name,
		X=request.X,
		Y=request.Y,
		width=request.width,
		height=request.height,
		feather=request.feather,
		rotation=request.rotation,
		invert=request.invert,
		roundCorner=request.roundCorner,
	)
	return AddMasksResponse(
		draft_id=draft_id,
		masks_added=masks_added,
		affected_segments=affected_segments,
		mask_ids=mask_ids,
	)


@router.post(path="/add_keyframes", response_model=AddKeyframesResponse)
def add_keyframes(request: AddKeyframesRequest) -> AddKeyframesResponse:
	draft_id, keyframes_added, affected_segments = service.add_keyframes(
		draft_id=request.draft_id,
		keyframes=request.keyframes,
	)
	return AddKeyframesResponse(
		draft_id=draft_id,
		keyframes_added=keyframes_added,
		affected_segments=affected_segments,
	)
