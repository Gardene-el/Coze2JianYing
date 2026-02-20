"""
Draft API 新路由 - 符合 API_ENDPOINTS_REFERENCE.md 规范
提供草稿级别的操作端点

更新说明：
- 所有响应使用 APIResponseManager 统一管理
- 始终返回 success=True（便于 Coze 插件测试）
- 错误详情通过 error_code 和 message 字段传递
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from app.backend.schemas.segment_schemas import (
    # Draft 操作
    CreateDraftRequest, CreateDraftResponse,
    AddTrackRequest, AddTrackResponse,
    AddSegmentToDraftRequest, AddSegmentToDraftResponse,
    AddGlobalEffectRequest, AddGlobalEffectResponse,
    AddGlobalFilterRequest, AddGlobalFilterResponse,
    SaveDraftResponse,
    # 查询
    DraftStatusResponse, TrackInfo, SegmentInfo, DownloadStatusInfo,
)
from app.backend.utils.draft_state_manager import get_draft_state_manager
from app.backend.utils.segment_manager import get_segment_manager
from app.backend.utils.draft_saver import get_draft_saver
from app.backend.utils.settings_manager import get_settings_manager
from app.backend.utils.logger import get_logger
from app.backend.utils.api_response_manager import get_response_manager, ErrorCode

router = APIRouter(prefix="/api/draft", tags=["草稿操作"])
logger = get_logger(__name__)
response_manager = get_response_manager()

# 获取全局管理器
draft_manager = get_draft_state_manager()
segment_manager = get_segment_manager()


@router.post(
    "/create",
    response_model=CreateDraftResponse,
    status_code=status.HTTP_200_OK,  # 改为 200，因为始终返回 success=True
    summary="创建草稿",
    description="创建新的剪映草稿项目并返回 UUID（总是返回 success=True，错误信息在 message 中）"
)
async def create_draft(request: CreateDraftRequest) -> CreateDraftResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    script = draft_folder.create_draft("demo", 1920, 1080, allow_replace=True)
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建剪映草稿, 并指定其基本参数如分辨率、帧率等
        草稿创建完成后, 可通过添加轨道和片段来构建完整的视频项目
        
        Args:
            draft_name (`str`): 草稿名称, 即相应文件夹名称
            width (`int`): 视频宽度, 单位为像素
            height (`int`): 视频高度, 单位为像素
            fps (`int`, optional): 视频帧率. 默认为30.
            allow_replace (`bool`, optional): 是否允许覆盖与`draft_name`重名的草稿. 默认为否.

        Raises:
            `FileExistsError`: 已存在与`draft_name`重名的草稿, 但不允许覆盖.
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建草稿请求")
    logger.info(f"项目名称: {request.draft_name}")
    logger.info(f"分辨率: {request.width}x{request.height}")
    logger.info(f"帧率: {request.fps}")
    
    try:
        # 调用草稿管理器创建草稿
        result = draft_manager.create_draft(
            draft_name=request.draft_name,
            width=request.width,
            height=request.height,
            fps=request.fps
        )
        
        if not result["success"]:
            # 创建失败，但依然返回 success=True
            logger.error(f"草稿创建失败: {result['message']}")
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateDraftResponse,
                error_code=ErrorCode.DRAFT_CREATE_FAILED,
                details={"reason": result["message"]},
                draft_id=""
            )
        
        # 创建成功
        logger.info(f"草稿创建成功: {result['draft_id']}")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            CreateDraftResponse,
            message=result["message"],
            draft_id=result["draft_id"]
        )
        
    except Exception as e:
        # 捕获所有异常，返回内部错误（依然 success=True）
        logger.error(f"创建草稿时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateDraftResponse,
            error=e,
            draft_id=""
        )


@router.post(
    "/{draft_id}/add_track",
    response_model=AddTrackResponse,
    status_code=status.HTTP_200_OK,
    summary="添加轨道",
    description="向草稿添加指定类型的轨道（总是返回 success=True）"
)
async def add_track(draft_id: str, request: AddTrackRequest) -> AddTrackResponse:
    """添加轨道（Coze 友好版本）"""
    logger.info("=" * 60)
    logger.info(f"收到添加轨道请求: draft_id={draft_id}")
    logger.info(f"轨道类型: {request.track_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            return response_manager.not_found_response(
                AddTrackResponse,
                resource_type="draft",
                resource_id=draft_id,
                track_index=-1
            )
        
        # 添加轨道
        tracks = config.get("tracks", [])
        track_index = len(tracks)
        
        track_info = {
            "track_type": request.track_type,
            "track_index": track_index,
            "track_name": request.track_name or f"{request.track_type}_{track_index}",
            "segments": []
        }
        
        tracks.append(track_info)
        config["tracks"] = tracks
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("添加轨道失败")
            return response_manager.error_response(
                AddTrackResponse,
                error_code=ErrorCode.TRACK_OPERATION_FAILED,
                details={"reason": "更新配置失败"},
                track_index=-1
            )
        
        logger.info(f"轨道添加成功: index={track_index}, type={request.track_type}")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddTrackResponse,
            message=f"轨道添加成功，索引: {track_index}",
            track_index=track_index
        )
        
    except Exception as e:
        logger.error(f"添加轨道时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddTrackResponse,
            error=e,
            track_index=-1
        )


@router.post(
    "/{draft_id}/add_segment",
    response_model=AddSegmentToDraftResponse,
    status_code=status.HTTP_200_OK,
    summary="添加片段到草稿",
    description="将已创建的 segment 添加到草稿中（总是返回 success=True）"
)
async def add_segment(draft_id: str, request: AddSegmentToDraftRequest) -> AddSegmentToDraftResponse:
    """添加片段到草稿（Coze 友好版本）"""
    logger.info("=" * 60)
    logger.info(f"收到添加片段请求: draft_id={draft_id}")
    logger.info(f"片段 ID: {request.segment_id}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            return response_manager.not_found_response(

                AddSegmentToDraftResponse,

                resource_type="draft",

                resource_id=draft_id

            )
        
        # 验证片段是否存在
        segment = segment_manager.get_segment(request.segment_id)
        if not segment:
            logger.error(f"片段不存在: {request.segment_id}")
            return response_manager.not_found_response(

                AddSegmentToDraftResponse,

                resource_type="segment",

                resource_id=request.segment_id

            )
        
        segment_type = segment["segment_type"]
        
        # 查找或创建合适的轨道
        tracks = config.get("tracks", [])
        target_track_index = request.track_index
        
        if target_track_index is None:
            # 自动选择合适的轨道
            track_type_map = {
                "audio": "audio",
                "video": "video",
                "text": "text",
                "sticker": "sticker"
            }
            required_track_type = track_type_map.get(segment_type)
            
            # 查找现有的合适轨道
            target_track_index = None
            for i, track in enumerate(tracks):
                if track["track_type"] == required_track_type:
                    target_track_index = i
                    break
            
            # 如果没有合适的轨道，创建一个新轨道
            if target_track_index is None:
                target_track_index = len(tracks)
                track_info = {
                    "track_type": required_track_type,
                    "track_index": target_track_index,
                    "track_name": f"{required_track_type}_{target_track_index}",
                    "segments": []
                }
                tracks.append(track_info)
                logger.info(f"自动创建轨道: index={target_track_index}, type={required_track_type}")
        
        # 验证轨道索引有效性
        if target_track_index >= len(tracks):
            return response_manager.error_response(
                AddSegmentToDraftResponse,
                error_code=ErrorCode.TRACK_INDEX_INVALID,
                details={"track_index": target_track_index}
            )
        
        # 验证轨道类型匹配
        track = tracks[target_track_index]
        track_type_map = {
            "audio": "audio",
            "video": "video",
            "text": "text",
            "sticker": "sticker"
        }
        expected_track_type = track_type_map.get(segment_type)
        
        if track["track_type"] != expected_track_type:
            return response_manager.error_response(
                AddSegmentToDraftResponse,
                error_code=ErrorCode.TRACK_TYPE_MISMATCH,
                details={
                    "segment_type": segment_type,
                    "track_type": track["track_type"]
                }
            )
        
        # 添加片段到轨道
        track["segments"].append(request.segment_id)
        config["tracks"] = tracks
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("添加片段失败")
            return response_manager.error_response(
                AddSegmentToDraftResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "更新配置失败"}
            )
        
        logger.info(f"片段添加成功: segment_id={request.segment_id}, track={target_track_index}")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddSegmentToDraftResponse,
            message=f"片段已添加到轨道 {target_track_index}"
        )
        
    except Exception as e:
        logger.error(f"添加片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddSegmentToDraftResponse,
            error=e
        )


@router.post(
    "/{draft_id}/add_effect",
    response_model=AddGlobalEffectResponse,
    status_code=status.HTTP_200_OK,
    summary="添加全局特效",
    description="向草稿添加全局特效（总是返回 success=True）"
)
async def add_global_effect(draft_id: str, request: AddGlobalEffectRequest) -> AddGlobalEffectResponse:
    """添加全局特效（Coze 友好版本）"""
    logger.info(f"为草稿 {draft_id} 添加全局特效: {request.effect_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            return response_manager.not_found_response(
                AddGlobalEffectResponse,
                resource_type="draft",
                resource_id=draft_id,
                effect_id=""
            )
        
        # 添加全局特效记录
        import uuid
        effect_id = str(uuid.uuid4())
        
        if "global_effects" not in config:
            config["global_effects"] = []
        
        effect_data = {
            "effect_id": effect_id,
            "effect_type": request.effect_type,
            "target_timerange": request.target_timerange.dict(),
            "params": request.params
        }
        
        config["global_effects"].append(effect_data)
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("添加全局特效失败")
            return response_manager.error_response(
                AddGlobalEffectResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "更新配置失败"},
                effect_id=""
            )
        
        logger.info(f"全局特效添加成功: {effect_id}")
        
        return response_manager.success_response(
            AddGlobalEffectResponse,
            message="全局特效添加成功",
            effect_id=effect_id
        )
        
    except Exception as e:
        logger.error(f"添加全局特效时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddGlobalEffectResponse,
            error=e,
            effect_id=""
        )


@router.post(
    "/{draft_id}/add_filter",
    response_model=AddGlobalFilterResponse,
    status_code=status.HTTP_200_OK,
    summary="添加全局滤镜",
    description="向草稿添加全局滤镜（总是返回 success=True）"
)
async def add_global_filter(draft_id: str, request: AddGlobalFilterRequest) -> AddGlobalFilterResponse:
    """添加全局滤镜（Coze 友好版本）"""
    logger.info(f"为草稿 {draft_id} 添加全局滤镜: {request.filter_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            return response_manager.not_found_response(
                AddGlobalFilterResponse,
                resource_type="draft",
                resource_id=draft_id,
                filter_id=""
            )
        
        # 添加全局滤镜记录
        import uuid
        filter_id = str(uuid.uuid4())
        
        if "global_filters" not in config:
            config["global_filters"] = []
        
        filter_data = {
            "filter_id": filter_id,
            "filter_type": request.filter_type,
            "target_timerange": request.target_timerange.dict(),
            "intensity": request.intensity
        }
        
        config["global_filters"].append(filter_data)
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("添加全局滤镜失败")
            return response_manager.error_response(
                AddGlobalFilterResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "更新配置失败"},
                filter_id=""
            )
        
        logger.info(f"全局滤镜添加成功: {filter_id}")
        
        return response_manager.success_response(
            AddGlobalFilterResponse,
            message="全局滤镜添加成功",
            filter_id=filter_id
        )
        
    except Exception as e:
        logger.error(f"添加全局滤镜时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddGlobalFilterResponse,
            error=e,
            filter_id=""
        )


@router.post(
    "/{draft_id}/save",
    response_model=SaveDraftResponse,
    status_code=status.HTTP_200_OK,
    summary="保存草稿",
    description="保存并完成草稿编辑，生成剪映草稿文件（总是返回 success=True）"
)
async def save_draft(draft_id: str) -> SaveDraftResponse:
    """保存草稿（Coze 友好版本）"""
    logger.info(f"保存草稿: {draft_id}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            return response_manager.not_found_response(
                SaveDraftResponse,
                resource_type="draft",
                resource_id=draft_id,
                draft_path=""
            )
        
        # 重新加载设置，确保使用最新的路径配置
        get_settings_manager().reload()
        
        # 使用 DraftSaver 保存草稿
        draft_saver = get_draft_saver()
        draft_path = draft_saver.save_draft(draft_id)
        
        # 更新状态为已保存
        config["status"] = "saved"
        draft_manager.update_draft_config(draft_id, config)
        
        logger.info(f"草稿保存成功: {draft_path}")
        
        return response_manager.success_response(
            SaveDraftResponse,
            message="草稿保存成功",
            draft_path=draft_path
        )
        
    except Exception as e:
        logger.error(f"保存草稿时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            SaveDraftResponse,
            error=e,
            draft_path=""
        )


@router.get(
    "/{draft_id}/status",
    response_model=DraftStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="查询草稿状态",
    description="根据草稿ID查询草稿的详细状态和信息（总是返回 success=True）"
)
async def get_draft_status(draft_id: str) -> DraftStatusResponse:
    """查询草稿状态（Coze 友好版本）"""
    logger.info(f"查询草稿状态: {draft_id}")
    
    try:
        config = draft_manager.get_draft_config(draft_id)
        
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 构建轨道信息
        tracks_info = []
        for track in config.get("tracks", []):
            tracks_info.append(TrackInfo(
                track_type=track["track_type"],
                track_index=track["track_index"],
                segment_count=len(track["segments"])
            ))
        
        # 构建片段信息
        segments_info = []
        all_segments = set()
        for track in config.get("tracks", []):
            for segment_id in track["segments"]:
                if segment_id not in all_segments:
                    all_segments.add(segment_id)
                    segment = segment_manager.get_segment(segment_id)
                    if segment:
                        material_url = segment.get("config", {}).get("material_url")
                        segments_info.append(SegmentInfo(
                            segment_id=segment_id,
                            segment_type=segment["segment_type"],
                            material_url=material_url,
                            download_status=segment.get("download_status", "none")
                        ))
        
        # 构建下载状态
        total = len([s for s in segments_info if s.material_url])
        completed = len([s for s in segments_info if s.download_status == "completed"])
        failed = len([s for s in segments_info if s.download_status == "failed"])
        pending = len([s for s in segments_info if s.download_status == "pending"])
        
        download_status = DownloadStatusInfo(
            total=total,
            completed=completed,
            pending=pending,
            failed=failed
        )
        
        return DraftStatusResponse(
            draft_id=draft_id,
            draft_name=config.get("project", {}).get("name", "未命名"),
            tracks=tracks_info,
            segments=segments_info,
            download_status=download_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询草稿状态时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询草稿状态失败: {str(e)}"
        )
