"""
api/segments/video_routes.py — VideoSegment 端点（含图片片段）
"""
import uuid
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import (
    CreateVideoSegmentRequest, CreateVideoSegmentResponse,
    AddVideoAnimationRequest, AddVideoAnimationResponse,
    AddVideoEffectRequest, AddVideoEffectResponse,
    AddVideoFadeRequest, AddVideoFadeResponse,
    AddVideoFilterRequest, AddVideoFilterResponse,
    AddVideoMaskRequest, AddVideoMaskResponse,
    AddVideoTransitionRequest, AddVideoTransitionResponse,
    AddVideoBackgroundFillingRequest, AddVideoBackgroundFillingResponse,
    AddVideoKeyframeRequest, AddVideoKeyframeResponse,
    SegmentDetailResponse,
)
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session, get_settings
from app.backend.core.settings_manager import SettingsManager
from app.backend.services.segments import video_segment
from app.backend.utils.logger import get_logger

router = APIRouter(prefix="/api/segment/video", tags=["VideoSegment"])
logger = get_logger(__name__)


@router.post("/create", response_model=CreateVideoSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建视频片段", description="对应 VideoSegment.__init__")
async def create_video_segment(
    request: CreateVideoSegmentRequest,
    session: SessionStore = Depends(get_session),
    settings: SettingsManager = Depends(get_settings),
) -> CreateVideoSegmentResponse:
    logger.info("创建视频片段: url=%s", request.material_url)
    assets_dir = settings.get_effective_assets_path()
    segment_id = video_segment.create_video(session, assets_dir, request.dict())
    return CreateVideoSegmentResponse(segment_id=segment_id)


@router.post("/{segment_id}/add_animation", response_model=AddVideoAnimationResponse, status_code=status.HTTP_200_OK,
    summary="添加入场/出场动画", description="对应 VideoSegment.add_animation")
async def add_animation(
    segment_id: str,
    request: AddVideoAnimationRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoAnimationResponse:
    logger.info("视频片段 %s 添加动画: %s", segment_id, request.animation_type)
    video_segment.add_animation(session, segment_id, request.animation_type, request.duration)
    return AddVideoAnimationResponse(animation_id=str(uuid.uuid4()))


@router.post("/{segment_id}/add_effect", response_model=AddVideoEffectResponse, status_code=status.HTTP_200_OK,
    summary="添加视频特效", description="对应 VideoSegment.add_effect")
async def add_effect(
    segment_id: str,
    request: AddVideoEffectRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoEffectResponse:
    logger.info("视频片段 %s 添加特效: %s", segment_id, request.effect_type)
    video_segment.add_effect(session, segment_id, request.effect_type, request.params)
    return AddVideoEffectResponse(effect_id=str(uuid.uuid4()))


@router.post("/{segment_id}/add_fade", response_model=AddVideoFadeResponse, status_code=status.HTTP_200_OK,
    summary="添加淡入淡出", description="对应 VideoSegment.add_fade")
async def add_fade(
    segment_id: str,
    request: AddVideoFadeRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoFadeResponse:
    logger.info("视频片段 %s 添加淡入淡出", segment_id)
    video_segment.add_fade(session, segment_id, request.in_duration, request.out_duration)
    return AddVideoFadeResponse()


@router.post("/{segment_id}/add_filter", response_model=AddVideoFilterResponse, status_code=status.HTTP_200_OK,
    summary="添加滤镜", description="对应 VideoSegment.add_filter")
async def add_filter(
    segment_id: str,
    request: AddVideoFilterRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoFilterResponse:
    logger.info("视频片段 %s 添加滤镜: %s", segment_id, request.filter_type)
    video_segment.add_filter(session, segment_id, request.filter_type, request.intensity)
    return AddVideoFilterResponse(filter_id=str(uuid.uuid4()))


@router.post("/{segment_id}/add_mask", response_model=AddVideoMaskResponse, status_code=status.HTTP_200_OK,
    summary="添加蒙版", description="对应 VideoSegment.add_mask")
async def add_mask(
    segment_id: str,
    request: AddVideoMaskRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoMaskResponse:
    logger.info("视频片段 %s 添加蒙版: %s", segment_id, request.mask_type)
    video_segment.add_mask(
        session, segment_id,
        request.mask_type,
        request.center_x, request.center_y,
        request.size, request.feather,
        request.invert, request.rotation,
        rect_width=request.rect_width,
        round_corner=request.round_corner,
    )
    return AddVideoMaskResponse(mask_id=str(uuid.uuid4()))


@router.post("/{segment_id}/add_transition", response_model=AddVideoTransitionResponse, status_code=status.HTTP_200_OK,
    summary="添加转场", description="对应 VideoSegment.add_transition")
async def add_transition(
    segment_id: str,
    request: AddVideoTransitionRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoTransitionResponse:
    logger.info("视频片段 %s 添加转场: %s", segment_id, request.transition_type)
    video_segment.add_transition(session, segment_id, request.transition_type, request.duration)
    return AddVideoTransitionResponse(transition_id=str(uuid.uuid4()))


@router.post("/{segment_id}/add_background_filling", response_model=AddVideoBackgroundFillingResponse,
    status_code=status.HTTP_200_OK, summary="添加背景填充", description="对应 VideoSegment.add_background_filling")
async def add_background_filling(
    segment_id: str,
    request: AddVideoBackgroundFillingRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoBackgroundFillingResponse:
    logger.info("视频片段 %s 添加背景填充: %s", segment_id, request.fill_type)
    video_segment.add_background_filling(session, segment_id, request.fill_type, request.blur, request.color)
    return AddVideoBackgroundFillingResponse()


@router.post("/{segment_id}/add_keyframe", response_model=AddVideoKeyframeResponse, status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧", description="对应 VideoSegment.add_keyframe")
async def add_keyframe(
    segment_id: str,
    request: AddVideoKeyframeRequest,
    session: SessionStore = Depends(get_session),
) -> AddVideoKeyframeResponse:
    logger.info("视频片段 %s 添加关键帧 prop=%s", segment_id, request.property)
    video_segment.add_keyframe(session, segment_id, request.property, request.time_offset, request.value)
    return AddVideoKeyframeResponse(keyframe_id=str(uuid.uuid4()))


@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询视频片段详情")
async def get_detail(
    segment_id: str,
    session: SessionStore = Depends(get_session),
) -> SegmentDetailResponse:
    meta = session.get_segment_meta(segment_id)
    return SegmentDetailResponse(
        segment_id=segment_id,
        segment_type=meta.get("type"),
        material_url=meta.get("material_url"),
        status="created",
        operations=[],
    )

