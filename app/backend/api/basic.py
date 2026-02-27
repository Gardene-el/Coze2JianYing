from __future__ import annotations

import os
from typing import Optional, cast

from fastapi import APIRouter, Body

from app.backend.config import get_config
from app.backend.schemas.basic.add_audio_effect import AddAudioEffectRequest, AddAudioEffectResponse
from app.backend.schemas.basic.add_audio_fade import AddAudioFadeRequest, AddAudioFadeResponse
from app.backend.schemas.basic.add_audio_keyframe import AddAudioKeyframeRequest, AddAudioKeyframeResponse
from app.backend.schemas.basic.add_effect import AddEffectRequest, AddEffectResponse
from app.backend.schemas.basic.add_filter import AddFilterRequest, AddFilterResponse
from app.backend.schemas.basic.add_segment import AddSegmentRequest, AddSegmentResponse
from app.backend.schemas.basic.add_sticker_keyframe import AddStickerKeyframeRequest, AddStickerKeyframeResponse
from app.backend.schemas.basic.add_text_animation import AddTextAnimationRequest, AddTextAnimationResponse
from app.backend.schemas.basic.add_text_bubble import AddTextBubbleRequest, AddTextBubbleResponse
from app.backend.schemas.basic.add_text_effect import AddTextEffectRequest, AddTextEffectResponse
from app.backend.schemas.basic.add_text_keyframe import AddTextKeyframeRequest, AddTextKeyframeResponse
from app.backend.schemas.basic.add_track import AddTrackRequest, AddTrackResponse
from app.backend.schemas.basic.add_video_animation import AddVideoAnimationRequest, AddVideoAnimationResponse
from app.backend.schemas.basic.add_video_background_filling import (
	AddVideoBackgroundFillingRequest,
	AddVideoBackgroundFillingResponse,
)
from app.backend.schemas.basic.add_video_effect import AddVideoEffectRequest, AddVideoEffectResponse
from app.backend.schemas.basic.add_video_fade import AddVideoFadeRequest, AddVideoFadeResponse
from app.backend.schemas.basic.add_video_filter import AddVideoFilterRequest, AddVideoFilterResponse
from app.backend.schemas.basic.add_video_keyframe import AddVideoKeyframeRequest, AddVideoKeyframeResponse
from app.backend.schemas.basic.add_video_mask import AddVideoMaskRequest, AddVideoMaskResponse
from app.backend.schemas.basic.add_video_transition import AddVideoTransitionRequest, AddVideoTransitionResponse
from app.backend.schemas.basic.create_audio_segment import CreateAudioSegmentRequest, CreateAudioSegmentResponse
from app.backend.schemas.basic.create_draft import CreateDraftRequest, CreateDraftResponse
from app.backend.schemas.basic.create_sticker_segment import (
	CreateStickerSegmentRequest,
	CreateStickerSegmentResponse,
)
from app.backend.schemas.basic.create_text_segment import CreateTextSegmentRequest, CreateTextSegmentResponse
from app.backend.schemas.basic.create_video_segment import CreateVideoSegmentRequest, CreateVideoSegmentResponse
from app.backend.schemas.basic.save_draft import SaveDraftRequest, SaveDraftResponse
from app.backend.services import basic as service
from app.backend.utils.helper import gen_unique_id


router = APIRouter(prefix="/basic", tags=["basic"])


@router.post(path="/create_draft", response_model=CreateDraftResponse)
def create_draft(request: CreateDraftRequest) -> CreateDraftResponse:
	draft_id = service.create_draft(width=request.width, height=request.height)
	return CreateDraftResponse(draft_id=draft_id)


@router.post(path="/save_draft", response_model=SaveDraftResponse)
def save_draft(request: SaveDraftRequest) -> SaveDraftResponse:
	saved_draft_id = service.save_draft(draft_id=request.draft_id)
	draft_path = os.path.join(get_config().drafts_dir, saved_draft_id)
	return SaveDraftResponse(draft_path=draft_path)


@router.post(path="/create_audio_segment", response_model=CreateAudioSegmentResponse)
def create_audio_segment(request: CreateAudioSegmentRequest) -> CreateAudioSegmentResponse:
	segment_id = service.create_audio_segment(
		material_url=request.material_url,
		target_timerange=request.target_timerange,
		source_timerange=request.source_timerange,
		speed=request.speed,
		volume=request.volume,
		change_pitch=request.change_pitch,
	)
	return CreateAudioSegmentResponse(segment_id=segment_id)


@router.post(path="/create_video_segment", response_model=CreateVideoSegmentResponse)
def create_video_segment(request: CreateVideoSegmentRequest) -> CreateVideoSegmentResponse:
	segment_id = service.create_video_segment(
		material_url=request.material_url,
		target_timerange=request.target_timerange,
		source_timerange=request.source_timerange,
		speed=request.speed,
		volume=request.volume,
		change_pitch=request.change_pitch,
		clip_settings=request.clip_settings,
		crop_settings=request.crop_settings,
	)
	return CreateVideoSegmentResponse(segment_id=segment_id)


@router.post(path="/create_text_segment", response_model=CreateTextSegmentResponse)
def create_text_segment(request: CreateTextSegmentRequest) -> CreateTextSegmentResponse:
	segment_id = service.create_text_segment(
		text_content=request.text_content,
		target_timerange=request.target_timerange,
		font_family=request.font_family,
		text_style=request.text_style,
		text_border=request.text_border,
		text_shadow=request.text_shadow,
		text_background=request.text_background,
		clip_settings=request.clip_settings,
	)
	return CreateTextSegmentResponse(segment_id=segment_id)


@router.post(path="/create_sticker_segment", response_model=CreateStickerSegmentResponse)
def create_sticker_segment(request: CreateStickerSegmentRequest) -> CreateStickerSegmentResponse:
	segment_id = service.create_sticker_segment(
		material_url=request.material_url,
		target_timerange=request.target_timerange,
		clip_settings=request.clip_settings,
	)
	return CreateStickerSegmentResponse(segment_id=segment_id)



@router.post(path="/add_segment", response_model=AddSegmentResponse)
def add_segment(draft_id: str = Body(..., embed=True, description="草稿ID"), request: AddSegmentRequest = Body(...)) -> AddSegmentResponse:
	service.add_segment(draft_id=draft_id, segment_id=request.segment_id)
	return AddSegmentResponse()


@router.post(path="/add_track", response_model=AddTrackResponse)
def add_track(draft_id: str = Body(..., embed=True, description="草稿ID"), request: AddTrackRequest = Body(...)) -> AddTrackResponse:
	service.add_track(draft_id=draft_id, track_type=request.track_type, track_name=request.track_name)
	return AddTrackResponse()


@router.post(path="/add_audio_effect", response_model=AddAudioEffectResponse)
def add_audio_effect(segment_id: str = Body(..., embed=True, description="片段ID"), request: AddAudioEffectRequest = Body(...)) -> AddAudioEffectResponse:
	params = cast(Optional[list[float | None]], request.params)
	service.add_audio_effect(segment_id=segment_id, effect_type=request.effect_type, params=params)
	return AddAudioEffectResponse(effect_id=gen_unique_id())


@router.post(path="/add_audio_fade", response_model=AddAudioFadeResponse)
def add_audio_fade(segment_id: str = Body(..., embed=True, description="片段ID"), request: AddAudioFadeRequest = Body(...)) -> AddAudioFadeResponse:
	service.add_audio_fade(segment_id=segment_id, in_duration=request.in_duration, out_duration=request.out_duration)
	return AddAudioFadeResponse()


@router.post(path="/add_audio_keyframe", response_model=AddAudioKeyframeResponse)
def add_audio_keyframe(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddAudioKeyframeRequest = Body(...),
) -> AddAudioKeyframeResponse:
	service.add_audio_keyframe(segment_id=segment_id, time_offset=request.time_offset, volume=request.volume)
	return AddAudioKeyframeResponse(keyframe_id=gen_unique_id())


@router.post(path="/add_global_effect", response_model=AddEffectResponse)
def add_global_effect(
	draft_id: str = Body(..., embed=True, description="草稿ID"),
	request: AddEffectRequest = Body(...),
) -> AddEffectResponse:
	service.add_global_effect(
		draft_id=draft_id,
		effect_type=request.effect_type,
		target_timerange=request.target_timerange,
		params=request.params,
	)
	return AddEffectResponse(effect_id=gen_unique_id())


@router.post(path="/add_global_filter", response_model=AddFilterResponse)
def add_global_filter(
	draft_id: str = Body(..., embed=True, description="草稿ID"),
	request: AddFilterRequest = Body(...),
) -> AddFilterResponse:
	service.add_global_filter(
		draft_id=draft_id,
		filter_type=request.filter_type,
		target_timerange=request.target_timerange,
		intensity=request.intensity,
	)
	return AddFilterResponse(filter_id=gen_unique_id())


@router.post(path="/add_sticker_keyframe", response_model=AddStickerKeyframeResponse)
def add_sticker_keyframe(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddStickerKeyframeRequest = Body(...),
) -> AddStickerKeyframeResponse:
	service.add_sticker_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddStickerKeyframeResponse(keyframe_id=gen_unique_id())


@router.post(path="/add_text_animation", response_model=AddTextAnimationResponse)
def add_text_animation(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddTextAnimationRequest = Body(...),
) -> AddTextAnimationResponse:
	service.add_text_animation(
		segment_id=segment_id,
		animation_type=request.animation_type,
		duration=request.duration or "1s",
	)
	return AddTextAnimationResponse(animation_id=gen_unique_id())


@router.post(path="/add_text_bubble", response_model=AddTextBubbleResponse)
def add_text_bubble(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddTextBubbleRequest = Body(...),
) -> AddTextBubbleResponse:
	service.add_text_bubble(segment_id=segment_id, effect_id=request.effect_id, resource_id=request.resource_id)
	return AddTextBubbleResponse(bubble_id=gen_unique_id())


@router.post(path="/add_text_effect", response_model=AddTextEffectResponse)
def add_text_effect(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddTextEffectRequest = Body(...),
) -> AddTextEffectResponse:
	service.add_text_effect(segment_id=segment_id, effect_id=request.effect_id)
	return AddTextEffectResponse(effect_id=gen_unique_id())


@router.post(path="/add_text_keyframe", response_model=AddTextKeyframeResponse)
def add_text_keyframe(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddTextKeyframeRequest = Body(...),
) -> AddTextKeyframeResponse:
	service.add_text_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddTextKeyframeResponse(keyframe_id=gen_unique_id())


@router.post(path="/add_video_animation", response_model=AddVideoAnimationResponse)
def add_video_animation(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoAnimationRequest = Body(...),
) -> AddVideoAnimationResponse:
	service.add_video_animation(
		segment_id=segment_id,
		animation_type=request.animation_type,
		duration=request.duration or "1s",
	)
	return AddVideoAnimationResponse(animation_id=gen_unique_id())


@router.post(path="/add_video_background_filling", response_model=AddVideoBackgroundFillingResponse)
def add_video_background_filling(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoBackgroundFillingRequest = Body(...),
) -> AddVideoBackgroundFillingResponse:
	service.add_video_background_filling(
		segment_id=segment_id,
		fill_type=request.fill_type,
		blur=request.blur if request.blur is not None else 0.0625,
		color=request.color if request.color is not None else "#00000000",
	)
	return AddVideoBackgroundFillingResponse()


@router.post(path="/add_video_effect", response_model=AddVideoEffectResponse)
def add_video_effect(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoEffectRequest = Body(...),
) -> AddVideoEffectResponse:
	service.add_video_effect(segment_id=segment_id, effect_type=request.effect_type, params=request.params)
	return AddVideoEffectResponse(effect_id=gen_unique_id())


@router.post(path="/add_video_fade", response_model=AddVideoFadeResponse)
def add_video_fade(segment_id: str = Body(..., embed=True, description="片段ID"), request: AddVideoFadeRequest = Body(...)) -> AddVideoFadeResponse:
	service.add_video_fade(segment_id=segment_id, in_duration=request.in_duration, out_duration=request.out_duration)
	return AddVideoFadeResponse()


@router.post(path="/add_video_filter", response_model=AddVideoFilterResponse)
def add_video_filter(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoFilterRequest = Body(...),
) -> AddVideoFilterResponse:
	service.add_video_filter(segment_id=segment_id, filter_type=request.filter_type, intensity=request.intensity)
	return AddVideoFilterResponse(filter_id=gen_unique_id())


@router.post(path="/add_video_keyframe", response_model=AddVideoKeyframeResponse)
def add_video_keyframe(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoKeyframeRequest = Body(...),
) -> AddVideoKeyframeResponse:
	service.add_video_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddVideoKeyframeResponse(keyframe_id=gen_unique_id())


@router.post(path="/add_video_mask", response_model=AddVideoMaskResponse)
def add_video_mask(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoMaskRequest = Body(...),
) -> AddVideoMaskResponse:
	service.add_video_mask(
		segment_id=segment_id,
		mask_type=request.mask_type,
		center_x=request.center_x if request.center_x is not None else 0.0,
		center_y=request.center_y if request.center_y is not None else 0.0,
		size=request.size if request.size is not None else 0.5,
		feather=request.feather if request.feather is not None else 0.0,
		invert=request.invert if request.invert is not None else False,
		rotation=request.rotation if request.rotation is not None else 0.0,
		rect_width=request.rect_width,
		round_corner=request.round_corner,
	)
	return AddVideoMaskResponse(mask_id=gen_unique_id())


@router.post(path="/add_video_transition", response_model=AddVideoTransitionResponse)
def add_video_transition(
	segment_id: str = Body(..., embed=True, description="片段ID"),
	request: AddVideoTransitionRequest = Body(...),
) -> AddVideoTransitionResponse:
	service.add_video_transition(segment_id=segment_id, transition_type=request.transition_type, duration=request.duration)
	return AddVideoTransitionResponse(transition_id=gen_unique_id())
