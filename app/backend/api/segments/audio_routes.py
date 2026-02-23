"""
api/segments/audio_routes.py — AudioSegment 端点
"""
import uuid
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import (
    CreateAudioSegmentRequest, CreateAudioSegmentResponse,
    AddAudioEffectRequest, AddAudioEffectResponse,
    AddAudioFadeRequest, AddAudioFadeResponse,
    AddAudioKeyframeRequest, AddAudioKeyframeResponse,
    SegmentDetailResponse,
)
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session, get_settings
from app.backend.core.settings_manager import SettingsManager
from app.backend.services.segments import audio_segment
from app.backend.utils.logger import logger

router = APIRouter(prefix="/api/segment/audio", tags=["AudioSegment"])


@router.post("/create", response_model=CreateAudioSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建音频片段", description="对应 AudioSegment.__init__")
async def create_audio_segment(
    request: CreateAudioSegmentRequest,
    session: SessionStore = Depends(get_session),
    settings: SettingsManager = Depends(get_settings),
) -> CreateAudioSegmentResponse:
    logger.info("创建音频片段: url=%s", request.material_url)
    assets_dir = settings.get_effective_assets_path()
    segment_id = audio_segment.create_audio(session, assets_dir, request.dict())
    return CreateAudioSegmentResponse(segment_id=segment_id)


@router.post("/{segment_id}/add_fade", response_model=AddAudioFadeResponse, status_code=status.HTTP_200_OK,
    summary="添加淡入淡出", description="对应 AudioSegment.add_fade")
async def add_fade(
    segment_id: str,
    request: AddAudioFadeRequest,
    session: SessionStore = Depends(get_session),
) -> AddAudioFadeResponse:
    logger.info("音频片段 %s 添加淡入淡出", segment_id)
    audio_segment.add_fade(session, segment_id, request.in_duration, request.out_duration)
    return AddAudioFadeResponse()


@router.post("/{segment_id}/add_effect", response_model=AddAudioEffectResponse, status_code=status.HTTP_200_OK,
    summary="添加音频特效", description="对应 AudioSegment.add_effect")
async def add_effect(
    segment_id: str,
    request: AddAudioEffectRequest,
    session: SessionStore = Depends(get_session),
) -> AddAudioEffectResponse:
    logger.info("音频片段 %s 添加特效: %s", segment_id, request.effect_type)
    audio_segment.add_effect(session, segment_id, request.effect_type, request.params)
    effect_id = str(uuid.uuid4())
    return AddAudioEffectResponse(effect_id=effect_id)


@router.post("/{segment_id}/add_keyframe", response_model=AddAudioKeyframeResponse, status_code=status.HTTP_200_OK,
    summary="添加音量关键帧", description="对应 AudioSegment.add_keyframe")
async def add_keyframe(
    segment_id: str,
    request: AddAudioKeyframeRequest,
    session: SessionStore = Depends(get_session),
) -> AddAudioKeyframeResponse:
    logger.info("音频片段 %s 添加关键帧 offset=%d", segment_id, request.time_offset)
    audio_segment.add_keyframe(session, segment_id, request.time_offset, request.volume)
    keyframe_id = str(uuid.uuid4())
    return AddAudioKeyframeResponse(keyframe_id=keyframe_id)


@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询音频片段详情")
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

