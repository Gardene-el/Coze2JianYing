"""api/segments/filter_routes.py — FilterSegment 端点"""
from fastapi import APIRouter, Depends, status
from app.backend.schemas.basic import CreateFilterSegmentRequest, CreateFilterSegmentResponse, SegmentDetailResponse
from app.backend.store.session_store import SessionStore
from app.backend.dependencies import get_session
from app.backend.services.segments import filter_segment
from app.backend.utils.logger import logger

router = APIRouter(prefix="/api/segment/filter", tags=["FilterSegment"])

@router.post("/create", response_model=CreateFilterSegmentResponse, status_code=status.HTTP_200_OK,
    summary="创建滤镜片段", description="对应 FilterSegment.__init__")
async def create_filter_segment(request: CreateFilterSegmentRequest,
    session: SessionStore = Depends(get_session)) -> CreateFilterSegmentResponse:
    logger.info("创建滤镜片段: type=%s", request.filter_type)
    segment_id = filter_segment.create_filter(session, request.dict())
    return CreateFilterSegmentResponse(segment_id=segment_id)

@router.get("/{segment_id}", response_model=SegmentDetailResponse, status_code=status.HTTP_200_OK,
    summary="查询滤镜片段详情")
async def get_detail(segment_id: str, session: SessionStore = Depends(get_session)) -> SegmentDetailResponse:
    meta = session.get_segment_meta(segment_id)
    return SegmentDetailResponse(
        segment_id=segment_id,
        segment_type=meta.get("type"),
        material_url=None,
        status="created",
        operations=[],
    )

