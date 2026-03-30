from __future__ import annotations

from fastapi import APIRouter, Path

from src.backend.schemas.easy.add_audios import AddAudiosRequest, AddAudiosResponse
from src.backend.schemas.easy.add_captions import AddCaptionsRequest, AddCaptionsResponse
from src.backend.schemas.easy.add_effects import AddEffectsRequest, AddEffectsResponse
from src.backend.schemas.easy.add_images import AddImagesRequest, AddImagesResponse
from src.backend.schemas.easy.add_keyframes import AddKeyframesRequest, AddKeyframesResponse
from src.backend.schemas.easy.add_masks import AddMasksRequest, AddMasksResponse
from src.backend.schemas.easy.add_videos import AddVideosRequest, AddVideosResponse
from src.backend.services import easy as service


router = APIRouter(tags=["easy"])


@router.post(
	path="/drafts/{draft_id}/add_audios",
	response_model=AddAudiosResponse,
	summary="批量添加音频",
	description="解析音频信息 JSON，批量创建音频片段并添加到草稿，返回片段 ID 列表。",
)
def add_audios(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddAudiosRequest = ...,
) -> AddAudiosResponse:
	segment_ids = service.add_audios(
		draft_id=draft_id,
		audio_infos=request.audio_infos,
	)
	return AddAudiosResponse(segment_ids=segment_ids)


@router.post(
	path="/drafts/{draft_id}/add_captions",
	response_model=AddCaptionsResponse,
	summary="批量添加字幕",
	description="解析字幕信息 JSON，批量创建文本片段并添加到草稿，支持字体、颜色、阴影等样式设置。",
)
def add_captions(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddCaptionsRequest = ...,
) -> AddCaptionsResponse:
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


@router.post(
	path="/drafts/{draft_id}/add_videos",
	response_model=AddVideosResponse,
	summary="批量添加视频",
	description="解析视频信息 JSON，批量创建视频片段并添加到草稿，返回片段 ID 列表。",
)
def add_videos(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddVideosRequest = ...,
) -> AddVideosResponse:
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


@router.post(
	path="/drafts/{draft_id}/add_images",
	response_model=AddImagesResponse,
	summary="批量添加图片",
	description="解析图片信息 JSON，批量创建图片片段并添加到草稿，返回片段 ID 列表。",
)
def add_images(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddImagesRequest = ...,
) -> AddImagesResponse:
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


@router.post(
	path="/drafts/{draft_id}/add_effects",
	response_model=AddEffectsResponse,
	summary="批量添加特效",
	description="解析特效信息 JSON，批量创建特效片段并添加到草稿，返回片段 ID 列表。",
)
def add_effects(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddEffectsRequest = ...,
) -> AddEffectsResponse:
	segment_ids = service.add_effects(
		draft_id=draft_id,
		effect_infos=request.effect_infos,
	)
	return AddEffectsResponse(segment_ids=segment_ids)


@router.post(
	path="/drafts/{draft_id}/add_masks",
	response_model=AddMasksResponse,
	summary="批量添加遮罩",
	description="为指定的多个片段批量应用遇罩效果，支持形状、缩放、缩放、旋转和羽化设置。",
)
def add_masks(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddMasksRequest = ...,
) -> AddMasksResponse:
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


@router.post(
	path="/drafts/{draft_id}/add_keyframes",
	response_model=AddKeyframesResponse,
	summary="批量添加关键帧",
	description="解析关键帧信息 JSON，批量为多个片段添加动画关键帧。",
)
def add_keyframes(
	draft_id: str = Path(..., description="草稿的唯一标识 ID"),
	request: AddKeyframesRequest = ...,
) -> AddKeyframesResponse:
	service.add_keyframes(
		draft_id=draft_id,
		keyframes=request.keyframes,
	)
	return AddKeyframesResponse()
