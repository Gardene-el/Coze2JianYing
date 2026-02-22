"""api/segments/effect_routes.py — EffectSegment 端点"""
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import CreateEffectSegmentRequest, CreateEffectSegmentResponse, SegmentDetailResponse
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session
from app.backend.services.segments import effect_segment
from app.backend.utils.logger import get_logger

router = APIRouter(prefix="/api/segment/effect", tags=["EffectSegment"])
logger = get_logger(__name__)

@router.post("/create", response_model=CreateEffectSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建特效片段", description="对应 EffectSegment.__init__")
async def create_effect_segment(request: CreateEffectSegmentRequest,
    session: SessionStore = Depends(get_session)) -> CreateEffectSegmentResponse:
    logger.info("创建特效片段: type=%s", request.effect_type)
    segment_id = effect_segment.create_effect(session, request.dict())
    return CreateEffectSegmentResponse(segment_id=segment_id)

@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询特效片段详情")
async def get_detail(segment_id: str, session: SessionStore = Depends(get_session)) -> SegmentDetailResponse:
    meta = session.get_segment_meta(segment_id)
    return SegmentDetailResponse(
        segment_id=segment_id,
        segment_type=meta.get("type"),
        material_url=None,
        status="created",
        operations=[],
    )

