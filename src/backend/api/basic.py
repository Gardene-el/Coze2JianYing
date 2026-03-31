from __future__ import annotations

from typing import Optional, cast

from fastapi import APIRouter, Path

from src.backend.schemas.basic.add_audio_effect import AddAudioEffectRequest, AddAudioEffectResponse
from src.backend.schemas.basic.add_audio_fade import AddAudioFadeRequest, AddAudioFadeResponse
from src.backend.schemas.basic.add_audio_keyframe import AddAudioKeyframeRequest, AddAudioKeyframeResponse
from src.backend.schemas.basic.add_effect import AddEffectRequest, AddEffectResponse
from src.backend.schemas.basic.add_filter import AddFilterRequest, AddFilterResponse
from src.backend.schemas.basic.add_segment import AddSegmentRequest, AddSegmentResponse
from src.backend.schemas.basic.add_sticker_keyframe import AddStickerKeyframeRequest, AddStickerKeyframeResponse
from src.backend.schemas.basic.add_text_animation import AddTextAnimationRequest, AddTextAnimationResponse
from src.backend.schemas.basic.add_text_bubble import AddTextBubbleRequest, AddTextBubbleResponse
from src.backend.schemas.basic.add_text_effect import AddTextEffectRequest, AddTextEffectResponse
from src.backend.schemas.basic.add_text_keyframe import AddTextKeyframeRequest, AddTextKeyframeResponse
from src.backend.schemas.basic.add_track import AddTrackRequest, AddTrackResponse
from src.backend.schemas.basic.add_video_animation import AddVideoAnimationRequest, AddVideoAnimationResponse
from src.backend.schemas.basic.add_video_background_filling import (
	AddVideoBackgroundFillingRequest,
	AddVideoBackgroundFillingResponse,
)
from src.backend.schemas.basic.add_video_effect import AddVideoEffectRequest, AddVideoEffectResponse
from src.backend.schemas.basic.add_video_fade import AddVideoFadeRequest, AddVideoFadeResponse
from src.backend.schemas.basic.add_video_filter import AddVideoFilterRequest, AddVideoFilterResponse
from src.backend.schemas.basic.add_video_keyframe import AddVideoKeyframeRequest, AddVideoKeyframeResponse
from src.backend.schemas.basic.add_video_mask import AddVideoMaskRequest, AddVideoMaskResponse
from src.backend.schemas.basic.add_video_transition import AddVideoTransitionRequest, AddVideoTransitionResponse
from src.backend.schemas.basic.create_audio_segment import CreateAudioSegmentRequest, CreateAudioSegmentResponse
from src.backend.schemas.basic.create_draft import CreateDraftRequest, CreateDraftResponse
from src.backend.schemas.basic.create_sticker_segment import (
	CreateStickerSegmentRequest,
	CreateStickerSegmentResponse,
)
from src.backend.schemas.basic.create_text_segment import CreateTextSegmentRequest, CreateTextSegmentResponse
from src.backend.schemas.basic.create_video_segment import CreateVideoSegmentRequest, CreateVideoSegmentResponse
from src.backend.schemas.basic.save_draft import SaveDraftResponse
from src.backend.services import basic as service


router = APIRouter(tags=["basic"])


@router.post(
	path="/drafts/create_draft",
	response_model=CreateDraftResponse,
	summary="创建草稿",
	description="创建一个新的剪映草稿，返回草稿 ID，后续所有操作均通过此 ID 引用该草稿。",
)
def create_draft(request: CreateDraftRequest) -> CreateDraftResponse:
	draft_id = service.create_draft(width=request.width, height=request.height)
	return CreateDraftResponse(draft_id=draft_id)


@router.post(
	path="/drafts/{draft_id}/save_draft",
	response_model=SaveDraftResponse,
	summary="保存草稿",
	description="将当前草稿内容持久化写入磁盘，使剪映可以读取到最新编辑结果。",
)
def save_draft(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
) -> SaveDraftResponse:
	service.save_draft(draft_id=draft_id)
	return SaveDraftResponse()



@router.post(
	path="/drafts/{draft_id}/add_segment",
	response_model=AddSegmentResponse,
	summary="添加片段到草稿",
	description="将已创建的片段（音频/视频/文本/贴纸）添加到指定草稿的对应轨道中。",
)
def add_segment(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddSegmentRequest = ...,
) -> AddSegmentResponse:
	service.add_segment(draft_id=draft_id, segment_id=request.segment_id, track_name=request.track_name)
	return AddSegmentResponse()


@router.post(
	path="/drafts/{draft_id}/add_track",
	response_model=AddTrackResponse,
	summary="添加轨道",
	description="在草稿中新建一条指定类型的轨道（audio/video/text/sticker/effect/filter）。",
)
def add_track(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddTrackRequest = ...,
) -> AddTrackResponse:
	service.add_track(draft_id=draft_id, track_type=request.track_type, track_name=request.track_name)
	return AddTrackResponse()


@router.post(
	path="/drafts/{draft_id}/add_effect",
	response_model=AddEffectResponse,
	summary="添加全局特效",
	description="在草稿上添加一个覆盖指定时间范围的全局特效。",
)
def add_effect(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddEffectRequest = ...,
) -> AddEffectResponse:
	service.add_effect(
		draft_id=draft_id,
		effect_type=request.effect_type,
		target_timerange=request.target_timerange,
		params=request.params,
	)
	return AddEffectResponse()


@router.post(
	path="/drafts/{draft_id}/add_filter",
	response_model=AddFilterResponse,
	summary="添加全局滤镜",
	description="在草稿上添加一个覆盖指定时间范围的全局色彩滤镜。",
)
def add_filter(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddFilterRequest = ...,
) -> AddFilterResponse:
	service.add_filter(
		draft_id=draft_id,
		filter_type=request.filter_type,
		target_timerange=request.target_timerange,
		intensity=request.intensity,
	)
	return AddFilterResponse()


@router.post(
	path="/segments/create_audio_segment",
	response_model=CreateAudioSegmentResponse,
	summary="创建音频片段",
	description="根据素材 URL 和时间范围创建音频片段，返回片段 ID，后续可将其添加到草稿轨道。",
)
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


@router.post(
	path="/segments/create_video_segment",
	response_model=CreateVideoSegmentResponse,
	summary="创建视频片段",
	description="根据素材 URL 和时间范围创建视频片段，返回片段 ID，后续可将其添加到草稿轨道。",
)
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


@router.post(
	path="/segments/create_text_segment",
	response_model=CreateTextSegmentResponse,
	summary="创建文本片段",
	description="根据文本内容和时间范围创建文本片段，支持字体、样式、描边、阴影等设置，返回片段 ID。",
)
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


@router.post(
	path="/segments/create_sticker_segment",
	response_model=CreateStickerSegmentResponse,
	summary="创建贴纸片段",
	description="根据素材 URL 和时间范围创建贴纸片段，返回片段 ID，后续可将其添加到草稿轨道。",
)
def create_sticker_segment(request: CreateStickerSegmentRequest) -> CreateStickerSegmentResponse:
	segment_id = service.create_sticker_segment(
		material_url=request.material_url,
		target_timerange=request.target_timerange,
		clip_settings=request.clip_settings,
	)
	return CreateStickerSegmentResponse(segment_id=segment_id)


@router.post(
	path="/segments/{segment_id}/add_audio_effect",
	response_model=AddAudioEffectResponse,
	summary="为音频片段添加音效",
	description="为指定音频片段添加音场、变调或语音转歌曲等音效。",
)
def add_audio_effect(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddAudioEffectRequest = ...,
) -> AddAudioEffectResponse:
	params = cast(Optional[list[float | None]], request.params)
	service.add_audio_effect(segment_id=segment_id, effect_type=request.effect_type, params=params)
	return AddAudioEffectResponse()


@router.post(
	path="/segments/{segment_id}/add_audio_fade",
	response_model=AddAudioFadeResponse,
	summary="为音频片段添加淡入淡出",
	description="为指定音频片段设置淡入和淡出的时长。",
)
def add_audio_fade(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddAudioFadeRequest = ...,
) -> AddAudioFadeResponse:
	service.add_audio_fade(segment_id=segment_id, in_duration=request.in_duration, out_duration=request.out_duration)
	return AddAudioFadeResponse()


@router.post(
	path="/segments/{segment_id}/add_audio_keyframe",
	response_model=AddAudioKeyframeResponse,
	summary="为音频片段添加音量关键帧",
	description="在指定时间点为音频片段添加音量关键帧，实现音量随时间的动态变化。",
)
def add_audio_keyframe(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddAudioKeyframeRequest = ...,
) -> AddAudioKeyframeResponse:
	service.add_audio_keyframe(segment_id=segment_id, time_offset=request.time_offset, volume=request.volume)
	return AddAudioKeyframeResponse()


@router.post(
	path="/segments/{segment_id}/add_sticker_keyframe",
	response_model=AddStickerKeyframeResponse,
	summary="为贴纸片段添加关键帧",
	description="在指定时间点为贴纸片段添加位置、缩放、旋转或透明度等属性的动画关键帧。",
)
def add_sticker_keyframe(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddStickerKeyframeRequest = ...,
) -> AddStickerKeyframeResponse:
	service.add_sticker_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddStickerKeyframeResponse()


@router.post(
	path="/segments/{segment_id}/add_text_animation",
	response_model=AddTextAnimationResponse,
	summary="为文本片段添加动画",
	description="为指定文本片段添加入场、出场或循环动画。",
)
def add_text_animation(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddTextAnimationRequest = ...,
) -> AddTextAnimationResponse:
	service.add_text_animation(
		segment_id=segment_id,
		animation_type=request.animation_type,
		duration=request.duration or "1s",
	)
	return AddTextAnimationResponse()


@router.post(
	path="/segments/{segment_id}/add_text_bubble",
	response_model=AddTextBubbleResponse,
	summary="为文本片段添加气泡",
	description="为指定文本片段添加气泡背景装饰特效。",
)
def add_text_bubble(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddTextBubbleRequest = ...,
) -> AddTextBubbleResponse:
	service.add_text_bubble(segment_id=segment_id, effect_id=request.effect_id, resource_id=request.resource_id)
	return AddTextBubbleResponse()


@router.post(
	path="/segments/{segment_id}/add_text_effect",
	response_model=AddTextEffectResponse,
	summary="为文本片段添加花字特效",
	description="为指定文本片段添加花字（文字样式特效）。",
)
def add_text_effect(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddTextEffectRequest = ...,
) -> AddTextEffectResponse:
	service.add_text_effect(segment_id=segment_id, effect_id=request.effect_id)
	return AddTextEffectResponse()


@router.post(
	path="/segments/{segment_id}/add_text_keyframe",
	response_model=AddTextKeyframeResponse,
	summary="为文本片段添加关键帧",
	description="在指定时间点为文本片段添加位置、缩放、旋转或透明度等属性的动画关键帧。",
)
def add_text_keyframe(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddTextKeyframeRequest = ...,
) -> AddTextKeyframeResponse:
	service.add_text_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddTextKeyframeResponse()


@router.post(
	path="/segments/{segment_id}/add_video_animation",
	response_model=AddVideoAnimationResponse,
	summary="为视频片段添加动画",
	description="为指定视频片段添加入场、出场或组合动画。",
)
def add_video_animation(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoAnimationRequest = ...,
) -> AddVideoAnimationResponse:
	service.add_video_animation(
		segment_id=segment_id,
		animation_type=request.animation_type,
		duration=request.duration or "1s",
	)
	return AddVideoAnimationResponse()


@router.post(
	path="/segments/{segment_id}/add_video_background_filling",
	response_model=AddVideoBackgroundFillingResponse,
	summary="为视频片段添加背景填充",
	description="为指定视频片段设置模糊或纯色背景填充，用于填补画面空白区域。",
)
def add_video_background_filling(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoBackgroundFillingRequest = ...,
) -> AddVideoBackgroundFillingResponse:
	service.add_video_background_filling(
		segment_id=segment_id,
		fill_type=request.fill_type,
		blur=request.blur if request.blur is not None else 0.0625,
		color=request.color if request.color is not None else "#00000000",
	)
	return AddVideoBackgroundFillingResponse()


@router.post(
	path="/segments/{segment_id}/add_video_effect",
	response_model=AddVideoEffectResponse,
	summary="为视频片段添加特效",
	description="为指定视频片段添加场景特效或人物特效。",
)
def add_video_effect(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoEffectRequest = ...,
) -> AddVideoEffectResponse:
	service.add_video_effect(segment_id=segment_id, effect_type=request.effect_type, params=request.params)
	return AddVideoEffectResponse()


@router.post(
	path="/segments/{segment_id}/add_video_fade",
	response_model=AddVideoFadeResponse,
	summary="为视频片段添加淡入淡出",
	description="为指定视频片段设置画面淡入和淡出的时长。",
)
def add_video_fade(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoFadeRequest = ...,
) -> AddVideoFadeResponse:
	service.add_video_fade(segment_id=segment_id, in_duration=request.in_duration, out_duration=request.out_duration)
	return AddVideoFadeResponse()


@router.post(
	path="/segments/{segment_id}/add_video_filter",
	response_model=AddVideoFilterResponse,
	summary="为视频片段添加滤镜",
	description="为指定视频片段添加色彩滤镜效果。",
)
def add_video_filter(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoFilterRequest = ...,
) -> AddVideoFilterResponse:
	service.add_video_filter(segment_id=segment_id, filter_type=request.filter_type, intensity=request.intensity)
	return AddVideoFilterResponse()


@router.post(
	path="/segments/{segment_id}/add_video_keyframe",
	response_model=AddVideoKeyframeResponse,
	summary="为视频片段添加关键帧",
	description="在指定时间点为视频片段添加位置、缩放、旋转或透明度等属性的动画关键帧。",
)
def add_video_keyframe(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoKeyframeRequest = ...,
) -> AddVideoKeyframeResponse:
	service.add_video_keyframe(
		segment_id=segment_id,
		time_offset=request.time_offset,
		value=request.value,
		property=request.property,
	)
	return AddVideoKeyframeResponse()


@router.post(
	path="/segments/{segment_id}/add_video_mask",
	response_model=AddVideoMaskResponse,
	summary="为视频片段添加蒙版",
	description="为指定视频片段添加形状蒙版（如圆形、矩形、线性等），支持羽化、旋转和反转。",
)
def add_video_mask(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoMaskRequest = ...,
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
	return AddVideoMaskResponse()


@router.post(
	path="/segments/{segment_id}/add_video_transition",
	response_model=AddVideoTransitionResponse,
	summary="为视频片段添加转场",
	description="为指定视频片段设置转场动画效果及时长。",
)
def add_video_transition(
	segment_id: str = Path(..., description="片段的唯一标识 ID"),
	request: AddVideoTransitionRequest = ...,
) -> AddVideoTransitionResponse:
	service.add_video_transition(segment_id=segment_id, transition_type=request.transition_type, duration=request.duration)
	return AddVideoTransitionResponse()
