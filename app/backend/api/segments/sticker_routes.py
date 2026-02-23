"""api/segments/sticker_routes.py — StickerSegment 端点"""
import uuid
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import (
    CreateStickerSegmentRequest, CreateStickerSegmentResponse,
    AddStickerKeyframeRequest, AddStickerKeyframeResponse,
    SegmentDetailResponse,
)
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session
from app.backend.services.segments import sticker_segment
from app.backend.utils.logger import logger

router = APIRouter(prefix="/api/segment/sticker", tags=["StickerSegment"])

@router.post("/create", response_model=CreateStickerSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建贴纸片段", description="对应 StickerSegment.__init__")
async def create_sticker_segment(request: CreateStickerSegmentRequest,
    session: SessionStore = Depends(get_session)) -> CreateStickerSegmentResponse:
    logger.info("创建贴纸片段: url=%s", request.material_url)
    segment_id = sticker_segment.create_sticker(session, request.dict())
    return CreateStickerSegmentResponse(segment_id=segment_id)

@router.post("/{segment_id}/add_keyframe", response_model=AddStickerKeyframeResponse, status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧", description="对应 StickerSegment.add_keyframe")
async def add_keyframe(segment_id: str, request: AddStickerKeyframeRequest,
    session: SessionStore = Depends(get_session)) -> AddStickerKeyframeResponse:
    sticker_segment.add_keyframe(session, segment_id, request.property, request.time_offset, request.value)
    return AddStickerKeyframeResponse(keyframe_id=str(uuid.uuid4()))

@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询贴纸片段详情")
async def get_detail(segment_id: str, session: SessionStore = Depends(get_session)) -> SegmentDetailResponse:
    meta = session.get_segment_meta(segment_id)
    return SegmentDetailResponse(
        segment_id=segment_id,
        segment_type=meta.get("type"),
        material_url=meta.get("material_url"),
        status="created",
        operations=[],
    )

