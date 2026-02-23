"""
Draft API 路由

薄适配器层：仅负责 HTTP 协议处理（解析请求体、调用服务、构建响应）。
DraftService 直接调用 pyJianYingDraft，SessionStore 持有内存中的 ScriptFile 对象。
"""
import uuid
from fastapi import APIRouter, Depends, status

from app.backend.schemas.basic import (
    CreateDraftRequest, CreateDraftResponse,
    AddTrackRequest, AddTrackResponse,
    AddSegmentRequest, AddSegmentResponse,
    AddGlobalEffectRequest, AddGlobalEffectResponse,
    AddGlobalFilterRequest, AddGlobalFilterResponse,
    SaveDraftResponse,
    DraftStatusResponse,
)
from app.backend.dependencies import get_draft_service, get_settings, get_session
from app.backend.store.session_store import SessionStore
from app.backend.services.draft import DraftService
from app.backend.core.settings_manager import SettingsManager
from app.backend.utils.logger import logger

router = APIRouter(prefix="/api/draft", tags=["草稿操作"])


@router.post(
    "/create",
    response_model=CreateDraftResponse,
    status_code=status.HTTP_200_OK,
    summary="创建草稿",
    description="创建新的剪映草稿项目并返回 UUID"
)
async def create_draft(
    request: CreateDraftRequest,
    service: DraftService = Depends(get_draft_service),
) -> CreateDraftResponse:
    logger.info("创建草稿: %s %dx%d@%dfps", request.draft_name, request.width, request.height, request.fps)
    draft_id = service.create_draft(request.draft_name, request.width, request.height, request.fps)
    return CreateDraftResponse(draft_id=draft_id)


@router.post(
    "/{draft_id}/add_track",
    response_model=AddTrackResponse,
    status_code=status.HTTP_200_OK,
    summary="添加轨道",
    description="向草稿添加指定类型的轨道"
)
async def add_track(
    draft_id: str,
    request: AddTrackRequest,
    service: DraftService = Depends(get_draft_service),
) -> AddTrackResponse:
    logger.info("添加轨道: draft=%s type=%s", draft_id, request.track_type)
    track_index = service.add_track(draft_id, request.track_type, request.track_name)
    return AddTrackResponse(track_index=track_index)


@router.post(
    "/{draft_id}/add_segment",
    response_model=AddSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="添加片段到草稿",
    description="将已创建的 segment 关联到草稿轨道"
)
async def add_segment(
    draft_id: str,
    request: AddSegmentRequest,
    service: DraftService = Depends(get_draft_service),
) -> AddSegmentResponse:
    logger.info("添加片段: draft=%s segment=%s track_index=%s", draft_id, request.segment_id, request.track_index)
    service.add_segment(draft_id, request.segment_id, track_index=request.track_index)
    return AddSegmentResponse()


@router.post(
    "/{draft_id}/add_effect",
    response_model=AddGlobalEffectResponse,
    status_code=status.HTTP_200_OK,
    summary="添加全局特效",
    description="向草稿添加全局特效"
)
async def add_global_effect(
    draft_id: str,
    request: AddGlobalEffectRequest,
    service: DraftService = Depends(get_draft_service),
) -> AddGlobalEffectResponse:
    logger.info("添加全局特效: draft=%s type=%s", draft_id, request.effect_type)
    service.add_global_effect(
        draft_id, request.effect_type,
        request.target_timerange.dict(),
        request.params,
    )
    effect_id = str(uuid.uuid4())
    return AddGlobalEffectResponse(effect_id=effect_id)


@router.post(
    "/{draft_id}/add_filter",
    response_model=AddGlobalFilterResponse,
    status_code=status.HTTP_200_OK,
    summary="添加全局滤镜",
    description="向草稿添加全局滤镜"
)
async def add_global_filter(
    draft_id: str,
    request: AddGlobalFilterRequest,
    service: DraftService = Depends(get_draft_service),
) -> AddGlobalFilterResponse:
    logger.info("添加全局滤镜: draft=%s type=%s", draft_id, request.filter_type)
    service.add_global_filter(
        draft_id, request.filter_type,
        request.target_timerange.dict(),
        request.intensity,
    )
    filter_id = str(uuid.uuid4())
    return AddGlobalFilterResponse(filter_id=filter_id)


@router.post(
    "/{draft_id}/save",
    response_model=SaveDraftResponse,
    status_code=status.HTTP_200_OK,
    summary="保存草稿",
    description="将草稿数据写出为剪映草稿文件"
)
async def save_draft(
    draft_id: str,
    service: DraftService = Depends(get_draft_service),
) -> SaveDraftResponse:
    logger.info("保存草稿: %s", draft_id)
    draft_path = service.save(draft_id)
    return SaveDraftResponse(draft_path=draft_path)


@router.get(
    "/{draft_id}/status",
    response_model=DraftStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="查询草稿状态",
    description="查询草稿的元数据和状态信息"
)
async def get_draft_status(
    draft_id: str,
    session: SessionStore = Depends(get_session),
) -> DraftStatusResponse:
    logger.info("查询草稿状态: %s", draft_id)
    from app.backend.schemas.basic import TrackInfo, SegmentInfo, DownloadStatusInfo
    meta = session.get_draft_meta(draft_id)

    tracks_info = []
    for t in meta.get("tracks", []):
        tracks_info.append(TrackInfo(
            track_type=t["track_type"],
            track_index=meta["tracks"].index(t),
            segment_count=0,  # 在 SessionStore 中片段直接绑定到 ScriptFile
        ))

    return DraftStatusResponse(
        draft_id=draft_id,
        draft_name=meta.get("name", "未命名"),
        tracks=tracks_info,
        segments=[],
        download_status=DownloadStatusInfo(total=0, completed=0, pending=0, failed=0),
    )

