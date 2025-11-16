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
from app.utils.draft_saver import get_draft_saver
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
    对应 pyJianYingDraft 代码：
    ```python
    script.add_track(draft.TrackType.audio)
    ```
    对应 pyJianYingDraft 注释：
    ```
        向草稿添加指定类型的轨道, 并可配置轨道名称、静音状态及图层位置
        轨道创建完成后, 可通过添加片段来填充轨道内容
        
        Args:
            track_type (`TrackType`): 轨道类型
            track_name (`str`, optional): 轨道名称. 仅在创建第一个同类型轨道时允许不指定.
            mute (`bool`, optional): 轨道是否静音. 默认不静音.
            relative_index (`int`, optional): 相对(同类型轨道的)图层位置, 越高越接近前景. 默认为0.
            absolute_index (`int`, optional): 绝对图层位置, 越高越接近前景. 此参数将直接覆盖相应片段的`render_index`属性, 供有经验的用户使用.
                此参数不能与`relative_index`同时使用.

        Raises:
            `NameError`: 已存在同类型轨道且未指定名称, 或已存在同名轨道
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
    对应 pyJianYingDraft 代码：
    ```python
    script.add_segment(audio_segment)
    ```
    对应 pyJianYingDraft 注释：
    ```
        将已创建的片段添加到草稿的指定轨道中, 可自动或手动指定轨道名称
        片段添加后将按时间轴排列, 不允许与已有片段重叠
        
        Args:
            segment (`VideoSegment`, `StickerSegment`, `AudioSegment`, or `TextSegment`): 要添加的片段
            track_name (`str`, optional): 添加到的轨道名称. 当此类型的轨道仅有一条时可省略.

        Raises:
            `NameError`: 未找到指定名称的轨道, 或必须提供`track_name`参数时未提供
            `TypeError`: 片段类型不匹配轨道类型
            `SegmentOverlap`: 新片段与已有片段重叠
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
    对应 pyJianYingDraft 代码：
    ```python
    script.add_effect(VideoSceneEffectType.XXX, timerange, params)
    ```
    对应 pyJianYingDraft 注释：
    ```
        向草稿添加全局特效, 可配置特效类型、时间范围及参数
        特效将应用于指定时间段的所有视频内容
        
        Args:
            effect (`VideoSceneEffectType` or `VideoCharacterEffectType`): 特效类型
            t_range (`Timerange`): 特效片段的时间范围
            track_name (`str`, optional): 添加到的轨道名称. 当特效轨道仅有一条时可省略.
            params (`List[Optional[float]]`, optional): 特效参数列表, 参数列表中未提供或为None的项使用默认值.
                参数取值范围(0~100)与剪映中一致. 某个特效类型有何参数以及具体参数顺序以枚举类成员的annotation为准.

        Raises:
            `NameError`: 未找到指定名称的轨道, 或必须提供`track_name`参数时未提供
            `TypeError`: 指定的轨道不是特效轨道
            `ValueError`: 新片段与已有片段重叠、提供的参数数量超过了该特效类型的参数数量, 或参数值超出范围.
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
    对应 pyJianYingDraft 代码：
    ```python
    script.add_filter(FilterType.XXX, timerange, intensity)
    ```
    对应 pyJianYingDraft 注释：
    ```
        向草稿添加全局滤镜, 可配置滤镜类型、时间范围及强度
        滤镜将应用于指定时间段的所有视频内容
        
        Args:
            filter_meta (`FilterType`): 滤镜类型
            t_range (`Timerange`): 滤镜片段的时间范围
            track_name (`str`, optional): 添加到的轨道名称. 当滤镜轨道仅有一条时可省略.
            intensity (`float`, optional): 滤镜强度(0-100). 仅当所选滤镜能够调节强度时有效. 默认为100.

        Raises:
            `NameError`: 未找到指定名称的轨道, 或必须提供`track_name`参数时未提供
            `TypeError`: 指定的轨道不是滤镜轨道
            `ValueError`: 新片段与已有片段重叠
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
    对应 pyJianYingDraft 代码：
    ```python
    script.save()
    ```
    对应 pyJianYingDraft 注释：
    ```
        保存草稿到磁盘, 生成剪映可识别的草稿文件
        保存完成后即可在剪映中打开和编辑该草稿
        
        Raises:
            `ValueError`: 没有设置保存路径
    ```
    
    实际实现: 将 DraftStateManager 和 SegmentManager 的数据转换为 pyJianYingDraft 调用并保存
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
        
        # 使用 DraftSaver 保存草稿
        draft_saver = get_draft_saver()
        draft_path = draft_saver.save_draft(draft_id)
        
        # 更新状态为已保存
        config["status"] = "saved"
        draft_manager.update_draft_config(draft_id, config)
        
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
