"""
Draft API 新路由 - 符合 API_ENDPOINTS_REFERENCE.md 规范
提供草稿级别的操作端点
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.segment_schemas import (
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
from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.segment_manager import get_segment_manager
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/draft", tags=["草稿操作"])
logger = get_logger(__name__)

# 获取全局管理器
draft_manager = get_draft_state_manager()
segment_manager = get_segment_manager()


@router.post(
    "/create",
    response_model=CreateDraftResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建草稿",
    description="创建新的剪映草稿项目并返回 UUID"
)
async def create_draft(request: CreateDraftRequest):
    """
    创建新的剪映草稿
    
    对应 pyJianYingDraft 代码：
    ```python
    script = draft_folder.create_draft("demo", 1920, 1080, allow_replace=True)
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建草稿请求")
    logger.info(f"项目名称: {request.draft_name}")
    logger.info(f"分辨率: {request.width}x{request.height}")
    logger.info(f"帧率: {request.fps}")
    
    try:
        result = draft_manager.create_draft(
            draft_name=request.draft_name,
            width=request.width,
            height=request.height,
            fps=request.fps
        )
        
        if not result["success"]:
            logger.error(f"草稿创建失败: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        logger.info(f"草稿创建成功: {result['draft_id']}")
        logger.info("=" * 60)
        
        return CreateDraftResponse(
            draft_id=result["draft_id"],
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建草稿时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建草稿失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add_track",
    response_model=AddTrackResponse,
    summary="添加轨道",
    description="向草稿添加指定类型的轨道"
)
async def add_track(draft_id: str, request: AddTrackRequest):
    """
    添加轨道
    
    对应 pyJianYingDraft 代码：
    ```python
    script.add_track(draft.TrackType.audio)
    ```
    """
    logger.info("=" * 60)
    logger.info(f"收到添加轨道请求: draft_id={draft_id}")
    logger.info(f"轨道类型: {request.track_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加轨道失败"
            )
        
        logger.info(f"轨道添加成功: index={track_index}, type={request.track_type}")
        logger.info("=" * 60)
        
        return AddTrackResponse(
            success=True,
            track_index=track_index,
            message=f"轨道添加成功，索引: {track_index}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加轨道时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加轨道失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add_segment",
    response_model=AddSegmentToDraftResponse,
    summary="添加片段到草稿",
    description="将已创建的 segment 添加到草稿中"
)
async def add_segment(draft_id: str, request: AddSegmentToDraftRequest):
    """
    添加片段到草稿
    
    对应 pyJianYingDraft 代码：
    ```python
    script.add_segment(audio_segment)
    ```
    """
    logger.info("=" * 60)
    logger.info(f"收到添加片段请求: draft_id={draft_id}")
    logger.info(f"片段 ID: {request.segment_id}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 验证片段是否存在
        segment = segment_manager.get_segment(request.segment_id)
        if not segment:
            logger.error(f"片段不存在: {request.segment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {request.segment_id} 不存在"
            )
        
        segment_type = segment["segment_type"]
        
        # 查找或创建合适的轨道
        tracks = config.get("tracks", [])
        target_track_index = request.track_index
        
        if target_track_index is None:
            # 自动选择合适的轨道
            # 根据片段类型映射到轨道类型
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"轨道索引 {target_track_index} 无效"
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型 {segment_type} 不能添加到 {track['track_type']} 轨道"
            )
        
        # 添加片段到轨道
        track["segments"].append(request.segment_id)
        config["tracks"] = tracks
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("添加片段失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加片段失败"
            )
        
        logger.info(f"片段添加成功: segment_id={request.segment_id}, track={target_track_index}")
        logger.info("=" * 60)
        
        return AddSegmentToDraftResponse(
            success=True,
            message=f"片段已添加到轨道 {target_track_index}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加片段时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加片段失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add_effect",
    response_model=AddGlobalEffectResponse,
    summary="添加全局特效",
    description="向草稿添加全局特效"
)
async def add_global_effect(draft_id: str, request: AddGlobalEffectRequest):
    """
    添加全局特效
    
    对应 pyJianYingDraft 代码：
    ```python
    script.add_effect(VideoSceneEffectType.XXX, timerange, params)
    ```
    """
    logger.info(f"为草稿 {draft_id} 添加全局特效: {request.effect_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加全局特效失败"
            )
        
        logger.info(f"全局特效添加成功: {effect_id}")
        
        return AddGlobalEffectResponse(
            success=True,
            effect_id=effect_id,
            message="全局特效添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加全局特效时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加全局特效失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add_filter",
    response_model=AddGlobalFilterResponse,
    summary="添加全局滤镜",
    description="向草稿添加全局滤镜"
)
async def add_global_filter(draft_id: str, request: AddGlobalFilterRequest):
    """
    添加全局滤镜
    
    对应 pyJianYingDraft 代码：
    ```python
    script.add_filter(FilterType.XXX, timerange, intensity)
    ```
    """
    logger.info(f"为草稿 {draft_id} 添加全局滤镜: {request.filter_type}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加全局滤镜失败"
            )
        
        logger.info(f"全局滤镜添加成功: {filter_id}")
        
        return AddGlobalFilterResponse(
            success=True,
            filter_id=filter_id,
            message="全局滤镜添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加全局滤镜时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加全局滤镜失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/save",
    response_model=SaveDraftResponse,
    summary="保存草稿",
    description="保存并完成草稿编辑，生成剪映草稿文件"
)
async def save_draft(draft_id: str):
    """
    保存草稿
    
    对应 pyJianYingDraft 代码：
    ```python
    script.save()
    ```
    
    注意：实际的草稿保存逻辑需要调用 pyJianYingDraft 库
    目前仅更新状态，实际实现待完成
    """
    logger.info(f"保存草稿: {draft_id}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 更新状态为已保存
        config["status"] = "saved"
        
        # 保存配置
        success = draft_manager.update_draft_config(draft_id, config)
        
        if not success:
            logger.error("保存草稿失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="保存草稿失败"
            )
        
        # TODO: 实际调用 pyJianYingDraft 保存逻辑
        # 这里需要将配置转换为 pyJianYingDraft 的调用序列
        
        # 构造草稿路径（实际路径取决于保存位置）
        draft_path = f"/tmp/jianying_drafts/{draft_id}"
        
        logger.info(f"草稿保存成功: {draft_path}")
        
        return SaveDraftResponse(
            success=True,
            draft_path=draft_path,
            message="草稿保存成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存草稿时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存草稿失败: {str(e)}"
        )


@router.get(
    "/{draft_id}/status",
    response_model=DraftStatusResponse,
    summary="查询草稿状态",
    description="根据草稿ID查询草稿的详细状态和信息"
)
async def get_draft_status(draft_id: str):
    """
    查询草稿状态
    
    返回草稿的轨道、片段和下载状态信息
    """
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
