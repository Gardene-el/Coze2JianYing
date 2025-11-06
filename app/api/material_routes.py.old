"""
素材管理 API 路由
提供添加视频、音频、图片、字幕等素材的 API 端点
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List
from datetime import datetime

from app.schemas.material_schemas import (
    AddVideosRequest,
    AddAudiosRequest,
    AddImagesRequest,
    AddCaptionsRequest,
    AddMaterialResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    DraftDetailResponse,
    DownloadStatus,
)
from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/draft", tags=["素材管理"])
logger = get_logger(__name__)

# 获取全局草稿状态管理器
draft_manager = get_draft_state_manager()


@router.post(
    "/create",
    response_model=CreateDraftResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新草稿",
    description="创建具有基本项目设置的新草稿并返回 UUID"
)
async def create_draft(request: CreateDraftRequest):
    """
    创建新的剪映草稿
    
    - **draft_name**: 项目名称
    - **width**: 视频宽度（像素）
    - **height**: 视频高度（像素）
    - **fps**: 帧率
    
    返回草稿 UUID 供后续操作使用
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
    "/{draft_id}/add-videos",
    response_model=AddMaterialResponse,
    summary="添加视频片段",
    description="向指定草稿添加视频轨道和视频片段"
)
async def add_videos(draft_id: str, request: AddVideosRequest):
    """
    添加视频片段到草稿
    
    - **draft_id**: 草稿 UUID
    - **videos**: 视频片段配置列表
    
    后端会自动下载素材文件到 Assets 文件夹
    """
    logger.info("=" * 60)
    logger.info(f"收到添加视频请求: draft_id={draft_id}")
    logger.info(f"视频片段数量: {len(request.videos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 转换请求为段配置
        segments = []
        for video in request.videos:
            segment = {
                "material_url": video.material_url,
                "time_range": {
                    "start": video.time_range.start,
                    "end": video.time_range.end
                },
                "position_x": video.position_x,
                "position_y": video.position_y,
                "scale_x": video.scale_x,
                "scale_y": video.scale_y,
                "rotation": video.rotation,
                "opacity": video.opacity,
                "speed": video.speed,
                "volume": video.volume
            }
            
            if video.material_range:
                segment["material_range"] = {
                    "start": video.material_range.start,
                    "end": video.material_range.end
                }
            
            segments.append(segment)
        
        # 添加视频轨道
        success = draft_manager.add_track(draft_id, "video", segments)
        
        if not success:
            logger.error("添加视频轨道失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加视频轨道失败"
            )
        
        # 获取下载状态
        download_status = draft_manager.get_download_status(draft_id)
        
        logger.info(f"成功添加 {len(segments)} 个视频片段")
        logger.info("=" * 60)
        
        return AddMaterialResponse(
            success=True,
            message=f"成功添加 {len(segments)} 个视频片段",
            segments_added=len(segments),
            download_status=DownloadStatus(**download_status)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加视频时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加视频失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add-audios",
    response_model=AddMaterialResponse,
    summary="添加音频片段",
    description="向指定草稿添加音频轨道和音频片段"
)
async def add_audios(draft_id: str, request: AddAudiosRequest):
    """
    添加音频片段到草稿
    
    - **draft_id**: 草稿 UUID
    - **audios**: 音频片段配置列表
    
    支持背景音乐、旁白、音效等各类音频
    """
    logger.info("=" * 60)
    logger.info(f"收到添加音频请求: draft_id={draft_id}")
    logger.info(f"音频片段数量: {len(request.audios)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 转换请求为段配置
        segments = []
        for audio in request.audios:
            segment = {
                "material_url": audio.material_url,
                "time_range": {
                    "start": audio.time_range.start,
                    "end": audio.time_range.end
                },
                "volume": audio.volume,
                "fade_in": audio.fade_in,
                "fade_out": audio.fade_out,
                "speed": audio.speed
            }
            
            if audio.material_range:
                segment["material_range"] = {
                    "start": audio.material_range.start,
                    "end": audio.material_range.end
                }
            
            segments.append(segment)
        
        # 添加音频轨道
        success = draft_manager.add_track(draft_id, "audio", segments)
        
        if not success:
            logger.error("添加音频轨道失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加音频轨道失败"
            )
        
        # 获取下载状态
        download_status = draft_manager.get_download_status(draft_id)
        
        logger.info(f"成功添加 {len(segments)} 个音频片段")
        logger.info("=" * 60)
        
        return AddMaterialResponse(
            success=True,
            message=f"成功添加 {len(segments)} 个音频片段",
            segments_added=len(segments),
            download_status=DownloadStatus(**download_status)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加音频时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加音频失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add-images",
    response_model=AddMaterialResponse,
    summary="添加图片片段",
    description="向指定草稿添加图片轨道和图片片段（作为静态视频）"
)
async def add_images(draft_id: str, request: AddImagesRequest):
    """
    添加图片片段到草稿
    
    - **draft_id**: 草稿 UUID
    - **images**: 图片片段配置列表
    
    图片在剪映中作为静态视频处理
    """
    logger.info("=" * 60)
    logger.info(f"收到添加图片请求: draft_id={draft_id}")
    logger.info(f"图片片段数量: {len(request.images)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 转换请求为段配置
        segments = []
        for image in request.images:
            segment = {
                "material_url": image.material_url,
                "time_range": {
                    "start": image.time_range.start,
                    "end": image.time_range.end
                },
                "position_x": image.position_x,
                "position_y": image.position_y,
                "scale_x": image.scale_x,
                "scale_y": image.scale_y,
                "rotation": image.rotation,
                "opacity": image.opacity,
                "fit_mode": image.fit_mode,
                "background_color": image.background_color
            }
            
            segments.append(segment)
        
        # 添加图片轨道（注意：使用 "video" 类型，因为图片作为静态视频处理）
        success = draft_manager.add_track(draft_id, "video", segments)
        
        if not success:
            logger.error("添加图片轨道失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加图片轨道失败"
            )
        
        # 获取下载状态
        download_status = draft_manager.get_download_status(draft_id)
        
        logger.info(f"成功添加 {len(segments)} 个图片片段")
        logger.info("=" * 60)
        
        return AddMaterialResponse(
            success=True,
            message=f"成功添加 {len(segments)} 个图片片段",
            segments_added=len(segments),
            download_status=DownloadStatus(**download_status)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加图片时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加图片失败: {str(e)}"
        )


@router.post(
    "/{draft_id}/add-captions",
    response_model=AddMaterialResponse,
    summary="添加字幕片段",
    description="向指定草稿添加字幕轨道和字幕片段"
)
async def add_captions(draft_id: str, request: AddCaptionsRequest):
    """
    添加字幕片段到草稿
    
    - **draft_id**: 草稿 UUID
    - **captions**: 字幕片段配置列表
    
    支持完整的文字样式配置
    """
    logger.info("=" * 60)
    logger.info(f"收到添加字幕请求: draft_id={draft_id}")
    logger.info(f"字幕片段数量: {len(request.captions)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(draft_id)
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 转换请求为段配置
        segments = []
        for caption in request.captions:
            segment = {
                "text": caption.text,
                "time_range": {
                    "start": caption.time_range.start,
                    "end": caption.time_range.end
                },
                "font_family": caption.font_family,
                "font_size": caption.font_size,
                "color": caption.color,
                "position_x": caption.position_x,
                "position_y": caption.position_y,
                "bold": caption.bold,
                "italic": caption.italic,
                "underline": caption.underline
            }
            
            segments.append(segment)
        
        # 添加字幕轨道
        success = draft_manager.add_track(draft_id, "text", segments)
        
        if not success:
            logger.error("添加字幕轨道失败")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加字幕轨道失败"
            )
        
        # 字幕不需要下载素材
        download_status = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "pending": 0
        }
        
        logger.info(f"成功添加 {len(segments)} 个字幕片段")
        logger.info("=" * 60)
        
        return AddMaterialResponse(
            success=True,
            message=f"成功添加 {len(segments)} 个字幕片段",
            segments_added=len(segments),
            download_status=DownloadStatus(**download_status)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加字幕时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加字幕失败: {str(e)}"
        )


@router.get(
    "/{draft_id}/detail",
    response_model=DraftDetailResponse,
    summary="获取草稿详情",
    description="查询草稿的详细信息和状态"
)
async def get_draft_detail(draft_id: str):
    """
    获取草稿详细信息
    
    - **draft_id**: 草稿 UUID
    
    返回草稿的完整配置和统计信息
    """
    logger.info(f"查询草稿详情: {draft_id}")
    
    try:
        config = draft_manager.get_draft_config(draft_id)
        
        if config is None:
            logger.error(f"草稿不存在: {draft_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"草稿 {draft_id} 不存在"
            )
        
        # 获取下载状态
        download_status = draft_manager.get_download_status(draft_id)
        
        # 构建响应
        project = config.get("project", {})
        
        return DraftDetailResponse(
            draft_id=draft_id,
            project_name=project.get("name", "未命名"),
            status=config.get("status", "unknown"),
            width=project.get("width", 1920),
            height=project.get("height", 1080),
            fps=project.get("fps", 30),
            tracks_count=len(config.get("tracks", [])),
            materials_count=len(config.get("media_resources", [])),
            download_status=DownloadStatus(**download_status),
            created_at=datetime.fromtimestamp(config.get("created_timestamp", 0)),
            last_modified=datetime.fromtimestamp(config.get("last_modified", 0))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询草稿详情时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询草稿详情失败: {str(e)}"
        )
