"""api/segments/text_routes.py — TextSegment 端点"""
import uuid
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import (
    CreateTextSegmentRequest, CreateTextSegmentResponse,
    AddTextAnimationRequest, AddTextAnimationResponse,
    AddTextBubbleRequest, AddTextBubbleResponse,
    AddTextEffectRequest, AddTextEffectResponse,
    AddTextKeyframeRequest, AddTextKeyframeResponse,
    SegmentDetailResponse,
)
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session
from app.backend.services.segments import text_segment
from app.backend.utils.logger import logger

router = APIRouter(prefix="/api/segment/text", tags=["TextSegment"])

@router.post("/create", response_model=CreateTextSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建文本片段", description="对应 TextSegment.__init__")
async def create_text_segment(request: CreateTextSegmentRequest,
    session: SessionStore = Depends(get_session)) -> CreateTextSegmentResponse:
    logger.info("创建文本片段: %r", request.text_content)
    segment_id = text_segment.create_text(session, request.dict())
    return CreateTextSegmentResponse(segment_id=segment_id)

@router.post("/{segment_id}/add_animation", response_model=AddTextAnimationResponse, status_code=status.HTTP_200_OK,
    summary="添加文本动画", description="对应 TextSegment.add_animation")
async def add_animation(segment_id: str, request: AddTextAnimationRequest,
    session: SessionStore = Depends(get_session)) -> AddTextAnimationResponse:
    text_segment.add_animation(session, segment_id, request.animation_type, request.duration)
    return AddTextAnimationResponse(animation_id=str(uuid.uuid4()))

@router.post("/{segment_id}/add_bubble", response_model=AddTextBubbleResponse, status_code=status.HTTP_200_OK,
    summary="添加气泡", description="对应 TextSegment.add_bubble")
async def add_bubble(segment_id: str, request: AddTextBubbleRequest,
    session: SessionStore = Depends(get_session)) -> AddTextBubbleResponse:
    text_segment.add_bubble(session, segment_id, request.effect_id, request.resource_id)
    return AddTextBubbleResponse(bubble_id=str(uuid.uuid4()))

@router.post("/{segment_id}/add_effect", response_model=AddTextEffectResponse, status_code=status.HTTP_200_OK,
    summary="添加花字特效", description="对应 TextSegment.add_effect")
async def add_effect(segment_id: str, request: AddTextEffectRequest,
    session: SessionStore = Depends(get_session)) -> AddTextEffectResponse:
    text_segment.add_effect(session, segment_id, request.effect_id)
    return AddTextEffectResponse(effect_id=str(uuid.uuid4()))

@router.post("/{segment_id}/add_keyframe", response_model=AddTextKeyframeResponse, status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧", description="对应 TextSegment.add_keyframe")
async def add_keyframe(segment_id: str, request: AddTextKeyframeRequest,
    session: SessionStore = Depends(get_session)) -> AddTextKeyframeResponse:
    text_segment.add_keyframe(session, segment_id, request.property, request.time_offset, request.value)
    return AddTextKeyframeResponse(keyframe_id=str(uuid.uuid4()))

@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询文本片段详情")
async def get_detail(segment_id: str, session: SessionStore = Depends(get_session)) -> SegmentDetailResponse:
    meta = session.get_segment_meta(segment_id)
    return SegmentDetailResponse(
        segment_id=segment_id,
        segment_type=meta.get("type"),
        material_url=None,
        status="created",
        operations=[],
    )

