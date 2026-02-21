"""
Easy API 路由

前缀: /api/easy
对应 capcut-mate 第 3-10 (add_xxs) 路由的简化移植。
主要差异：使用 draft_id (UUID) 替代 draft_url (本地文件路径)。

草稿管理（create_draft / save_draft）请直接调用 /api/draft 端点。
计算类工具（timelines / audio_timelines / *_infos）已迁移为 Coze 插件工具。
"""

from typing import List

from fastapi import APIRouter

from app.backend.schemas.easy_schemas import (
    AddAudiosRequest, AddAudiosResponse,
    AddCaptionsRequest, AddCaptionsResponse,
    AddEffectsRequest, AddEffectsResponse,
    AddImagesRequest, AddImagesResponse,
    AddKeyframesRequest, AddKeyframesResponse,
    AddMasksRequest, AddMasksResponse,
    AddStickerRequest, AddStickerResponse,
    AddVideosRequest, AddVideosResponse,
    SegmentInfo,
)
from app.backend.services import easy_service
from app.backend.utils.logger import get_logger

router = APIRouter(prefix="/api/easy", tags=["Easy API"])
logger = get_logger(__name__)


# ════════════════════════════════════════════════════════════
# add_xxs 系列（草稿操作）
# ════════════════════════════════════════════════════════════

@router.post("/add_videos", response_model=AddVideosResponse, summary="向草稿添加视频")
async def add_videos(req: AddVideosRequest) -> AddVideosResponse:
    """下载视频并添加到草稿时间线。"""
    try:
        track_id, video_ids, segment_ids = easy_service.add_videos(
            draft_id=req.draft_id,
            video_infos_str=req.video_infos,
            alpha=req.alpha,
            scale_x=req.scale_x,
            scale_y=req.scale_y,
            transform_x=req.transform_x,
            transform_y=req.transform_y,
        )
        return AddVideosResponse(
            success=True,
            message="视频添加成功",
            draft_id=req.draft_id,
            track_id=track_id,
            video_ids=video_ids,
            segment_ids=segment_ids,
        )
    except Exception as exc:
        logger.error(f"add_videos 失败: {exc}")
        return AddVideosResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_audios", response_model=AddAudiosResponse, summary="向草稿添加音频")
async def add_audios(req: AddAudiosRequest) -> AddAudiosResponse:
    """下载音频并添加到草稿时间线。"""
    try:
        track_id, audio_ids = easy_service.add_audios(
            draft_id=req.draft_id,
            audio_infos_str=req.audio_infos,
        )
        return AddAudiosResponse(
            success=True,
            message="音频添加成功",
            draft_id=req.draft_id,
            track_id=track_id,
            audio_ids=audio_ids,
        )
    except Exception as exc:
        logger.error(f"add_audios 失败: {exc}")
        return AddAudiosResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_images", response_model=AddImagesResponse, summary="向草稿添加图片")
async def add_images(req: AddImagesRequest) -> AddImagesResponse:
    """下载图片并添加到草稿时间线。"""
    try:
        track_id, image_ids, segment_ids, seg_infos_raw = easy_service.add_images(
            draft_id=req.draft_id,
            image_infos_str=req.image_infos,
            alpha=req.alpha,
            scale_x=req.scale_x,
            scale_y=req.scale_y,
            transform_x=req.transform_x,
            transform_y=req.transform_y,
        )
        segment_infos = [SegmentInfo(**d) for d in seg_infos_raw]
        return AddImagesResponse(
            success=True,
            message="图片添加成功",
            draft_id=req.draft_id,
            track_id=track_id,
            image_ids=image_ids,
            segment_ids=segment_ids,
            segment_infos=segment_infos,
        )
    except Exception as exc:
        logger.error(f"add_images 失败: {exc}")
        return AddImagesResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_sticker", response_model=AddStickerResponse, summary="向草稿添加贴纸")
async def add_sticker(req: AddStickerRequest) -> AddStickerResponse:
    """将贴纸素材添加到草稿时间线。"""
    try:
        sticker_id_ret, track_id, segment_id, duration = easy_service.add_sticker(
            draft_id=req.draft_id,
            sticker_id=req.sticker_id,
            start=req.start,
            end=req.end,
            scale=req.scale,
            transform_x=req.transform_x,
            transform_y=req.transform_y,
        )
        return AddStickerResponse(
            success=True,
            message="贴纸添加成功",
            draft_id=req.draft_id,
            sticker_id=sticker_id_ret,
            track_id=track_id,
            segment_id=segment_id,
            duration=duration,
        )
    except Exception as exc:
        logger.error(f"add_sticker 失败: {exc}")
        return AddStickerResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_keyframes", response_model=AddKeyframesResponse, summary="向草稿片段添加关键帧")
async def add_keyframes(req: AddKeyframesRequest) -> AddKeyframesResponse:
    """为指定片段添加关键帧动画。"""
    try:
        keyframes_added, affected_segments = easy_service.add_keyframes(
            draft_id=req.draft_id,
            keyframes_str=req.keyframes,
        )
        return AddKeyframesResponse(
            success=True,
            message=f"关键帧添加成功: {keyframes_added} 个",
            draft_id=req.draft_id,
            keyframes_added=keyframes_added,
            affected_segments=affected_segments,
        )
    except Exception as exc:
        logger.error(f"add_keyframes 失败: {exc}")
        return AddKeyframesResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_captions", response_model=AddCaptionsResponse, summary="向草稿添加字幕")
async def add_captions(req: AddCaptionsRequest) -> AddCaptionsResponse:
    """将字幕文本添加到草稿文字轨道。"""
    try:
        track_id, text_ids, segment_ids, seg_infos_raw = easy_service.add_captions(
            draft_id=req.draft_id,
            captions_str=req.captions,
            text_color=req.text_color,
            border_color=req.border_color,
            alignment=req.alignment,
            alpha=req.alpha,
            font=req.font,
            font_size=req.font_size,
            letter_spacing=req.letter_spacing,
            line_spacing=req.line_spacing,
            scale_x=req.scale_x,
            scale_y=req.scale_y,
            transform_x=req.transform_x,
            transform_y=req.transform_y,
            style_text=req.style_text,
            underline=req.underline,
            italic=req.italic,
            bold=req.bold,
            has_shadow=req.has_shadow,
            shadow_info=req.shadow_info,
        )
        segment_infos = [SegmentInfo(**d) for d in seg_infos_raw]
        return AddCaptionsResponse(
            success=True,
            message="字幕添加成功",
            draft_id=req.draft_id,
            track_id=track_id,
            text_ids=text_ids,
            segment_ids=segment_ids,
            segment_infos=segment_infos,
        )
    except Exception as exc:
        logger.error(f"add_captions 失败: {exc}")
        return AddCaptionsResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_effects", response_model=AddEffectsResponse, summary="向草稿添加特效")
async def add_effects(req: AddEffectsRequest) -> AddEffectsResponse:
    """将视频特效添加到草稿时间线。"""
    try:
        track_id, effect_ids, segment_ids = easy_service.add_effects(
            draft_id=req.draft_id,
            effect_infos_str=req.effect_infos,
        )
        return AddEffectsResponse(
            success=True,
            message="特效添加成功",
            draft_id=req.draft_id,
            track_id=track_id,
            effect_ids=effect_ids,
            segment_ids=segment_ids,
        )
    except Exception as exc:
        logger.error(f"add_effects 失败: {exc}")
        return AddEffectsResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )


@router.post("/add_masks", response_model=AddMasksResponse, summary="向片段添加遮罩")
async def add_masks(req: AddMasksRequest) -> AddMasksResponse:
    """为指定片段添加遮罩效果。"""
    try:
        masks_added, affected_segments, mask_ids = easy_service.add_masks(
            draft_id=req.draft_id,
            segment_ids_list=req.segment_ids,
            name=req.name,
            X=req.X,
            Y=req.Y,
            width=req.width,
            height=req.height,
            feather=req.feather,
            rotation=req.rotation,
            invert=req.invert,
            roundCorner=req.roundCorner,
        )
        return AddMasksResponse(
            success=True,
            message=f"遮罩添加成功: {masks_added} 个",
            draft_id=req.draft_id,
            masks_added=masks_added,
            affected_segments=affected_segments,
            mask_ids=mask_ids,
        )
    except Exception as exc:
        logger.error(f"add_masks 失败: {exc}")
        return AddMasksResponse(
            success=False,
            message=str(exc),
            draft_id=req.draft_id,
        )
