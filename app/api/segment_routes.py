"""
Segment API 路由
提供符合 API_ENDPOINTS_REFERENCE.md 规范的 Segment 创建和操作 API 端点
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.schemas.segment_schemas import (
    # Segment 创建
    CreateAudioSegmentRequest, CreateVideoSegmentRequest,
    CreateTextSegmentRequest, CreateStickerSegmentRequest,
    CreateSegmentResponse,
    # Segment 操作
    AddEffectRequest, AddEffectResponse,
    AddFadeRequest, AddFadeResponse,
    AddKeyframeRequest, AddKeyframeResponse,
    AddAnimationRequest, AddAnimationResponse,
    AddFilterRequest, AddFilterResponse,
    AddMaskRequest, AddMaskResponse,
    AddTransitionRequest, AddTransitionResponse,
    AddBackgroundFillingRequest, AddBackgroundFillingResponse,
    AddBubbleRequest, AddBubbleResponse,
    AddTextEffectRequest, AddTextEffectResponse,
    # 查询
    SegmentDetailResponse,
)
from app.utils.segment_manager import get_segment_manager
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/segment", tags=["片段管理"])
logger = get_logger(__name__)

# 获取全局片段管理器
segment_manager = get_segment_manager()


# ==================== Segment 创建端点 ====================

@router.post(
    "/audio/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建音频片段",
    description="创建音频片段并返回 UUID"
)
async def create_audio_segment(request: CreateAudioSegmentRequest):
    """
    创建音频片段
    
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment = draft.AudioSegment(
        "audio.mp3",
        trange("0s", "5s"),
        volume=0.6
    )
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建音频片段请求")
    logger.info(f"素材 URL: {request.material_url}")
    
    try:
        # 准备配置
        config = request.dict()
        
        # 创建片段
        result = segment_manager.create_segment("audio", config)
        
        if not result["success"]:
            logger.error(f"音频片段创建失败: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        logger.info(f"音频片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)
        
        return CreateSegmentResponse(
            segment_id=result["segment_id"],
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建音频片段时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建音频片段失败: {str(e)}"
        )


@router.post(
    "/video/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建视频片段",
    description="创建视频片段并返回 UUID"
)
async def create_video_segment(request: CreateVideoSegmentRequest):
    """
    创建视频片段
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment = draft.VideoSegment(
        VideoMaterial("video.mp4"),
        trange("0s", "5s")
    )
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建视频片段请求")
    logger.info(f"素材 URL: {request.material_url}")
    
    try:
        # 准备配置
        config = request.dict()
        
        # 创建片段
        result = segment_manager.create_segment("video", config)
        
        if not result["success"]:
            logger.error(f"视频片段创建失败: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        logger.info(f"视频片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)
        
        return CreateSegmentResponse(
            segment_id=result["segment_id"],
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建视频片段时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建视频片段失败: {str(e)}"
        )


@router.post(
    "/text/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建文本片段",
    description="创建文本片段并返回 UUID"
)
async def create_text_segment(request: CreateTextSegmentRequest):
    """
    创建文本片段
    
    对应 pyJianYingDraft 代码：
    ```python
    text_segment = draft.TextSegment(
        "Hello World",
        trange("0s", "3s")
    )
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建文本片段请求")
    logger.info(f"文本内容: {request.text_content}")
    
    try:
        # 准备配置
        config = request.dict()
        
        # 创建片段
        result = segment_manager.create_segment("text", config)
        
        if not result["success"]:
            logger.error(f"文本片段创建失败: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        logger.info(f"文本片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)
        
        return CreateSegmentResponse(
            segment_id=result["segment_id"],
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建文本片段时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文本片段失败: {str(e)}"
        )


@router.post(
    "/sticker/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建贴纸片段",
    description="创建贴纸片段并返回 UUID"
)
async def create_sticker_segment(request: CreateStickerSegmentRequest):
    """
    创建贴纸片段
    
    对应 pyJianYingDraft 代码：
    ```python
    sticker_segment = draft.StickerSegment(
        material,
        trange("0s", "3s")
    )
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建贴纸片段请求")
    logger.info(f"素材 URL: {request.material_url}")
    
    try:
        # 准备配置
        config = request.dict()
        
        # 创建片段
        result = segment_manager.create_segment("sticker", config)
        
        if not result["success"]:
            logger.error(f"贴纸片段创建失败: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        logger.info(f"贴纸片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)
        
        return CreateSegmentResponse(
            segment_id=result["segment_id"],
            success=True,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建贴纸片段时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建贴纸片段失败: {str(e)}"
        )


# ==================== AudioSegment 操作端点 ====================

@router.post(
    "/audio/{segment_id}/add_effect",
    response_model=AddEffectResponse,
    summary="添加音频特效",
    description="向音频片段添加特效"
)
async def add_audio_effect(segment_id: str, request: AddEffectRequest):
    """
    添加音频特效
    
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_effect(AudioSceneEffectType.XXX, params)
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加特效: {request.effect_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "audio":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 audio，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_effect", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加特效失败"
            )
        
        # 生成特效 ID
        import uuid
        effect_id = str(uuid.uuid4())
        
        logger.info(f"音频特效添加成功: {effect_id}")
        
        return AddEffectResponse(
            success=True,
            effect_id=effect_id,
            message="音频特效添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加音频特效时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加音频特效失败: {str(e)}"
        )


@router.post(
    "/audio/{segment_id}/add_fade",
    response_model=AddFadeResponse,
    summary="添加淡入淡出",
    description="向音频片段添加淡入淡出"
)
async def add_audio_fade(segment_id: str, request: AddFadeRequest):
    """
    添加淡入淡出
    
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_fade("1s", "0s")
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加淡入淡出")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "audio":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 audio，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_fade", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加淡入淡出失败"
            )
        
        logger.info("淡入淡出添加成功")
        
        return AddFadeResponse(
            success=True,
            message="淡入淡出添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加淡入淡出时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加淡入淡出失败: {str(e)}"
        )


@router.post(
    "/audio/{segment_id}/add_keyframe",
    response_model=AddKeyframeResponse,
    summary="添加音量关键帧",
    description="向音频片段添加音量关键帧"
)
async def add_audio_keyframe(segment_id: str, request: AddKeyframeRequest):
    """
    添加音量关键帧
    
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_keyframe("2s", 0.8)
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加关键帧")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "audio":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 audio，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_keyframe", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加关键帧失败"
            )
        
        # 生成关键帧 ID
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        logger.info(f"关键帧添加成功: {keyframe_id}")
        
        return AddKeyframeResponse(
            success=True,
            keyframe_id=keyframe_id,
            message="关键帧添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加关键帧时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加关键帧失败: {str(e)}"
        )


# ==================== VideoSegment 操作端点 ====================

@router.post(
    "/video/{segment_id}/add_animation",
    response_model=AddAnimationResponse,
    summary="添加动画",
    description="向视频片段添加动画"
)
async def add_video_animation(segment_id: str, request: AddAnimationRequest):
    """
    添加动画
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_animation(IntroType.XXX, duration="1s")
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加动画: {request.animation_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_animation", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加动画失败"
            )
        
        # 生成动画 ID
        import uuid
        animation_id = str(uuid.uuid4())
        
        logger.info(f"动画添加成功: {animation_id}")
        
        return AddAnimationResponse(
            success=True,
            animation_id=animation_id,
            message="动画添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加动画时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加动画失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_effect",
    response_model=AddEffectResponse,
    summary="添加视频特效",
    description="向视频片段添加特效"
)
async def add_video_effect(segment_id: str, request: AddEffectRequest):
    """
    添加视频特效
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_effect(VideoSceneEffectType.XXX, params)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加特效: {request.effect_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_effect", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加特效失败"
            )
        
        # 生成特效 ID
        import uuid
        effect_id = str(uuid.uuid4())
        
        logger.info(f"视频特效添加成功: {effect_id}")
        
        return AddEffectResponse(
            success=True,
            effect_id=effect_id,
            message="视频特效添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加视频特效时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加视频特效失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_fade",
    response_model=AddFadeResponse,
    summary="添加淡入淡出",
    description="向视频片段添加淡入淡出"
)
async def add_video_fade(segment_id: str, request: AddFadeRequest):
    """
    添加淡入淡出
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_fade("1s", "0s")
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加淡入淡出")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_fade", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加淡入淡出失败"
            )
        
        logger.info("淡入淡出添加成功")
        
        return AddFadeResponse(
            success=True,
            message="淡入淡出添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加淡入淡出时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加淡入淡出失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_filter",
    response_model=AddFilterResponse,
    summary="添加滤镜",
    description="向视频片段添加滤镜"
)
async def add_video_filter(segment_id: str, request: AddFilterRequest):
    """
    添加滤镜
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_filter(FilterType.XXX, intensity=100.0)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加滤镜: {request.filter_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_filter", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加滤镜失败"
            )
        
        # 生成滤镜 ID
        import uuid
        filter_id = str(uuid.uuid4())
        
        logger.info(f"滤镜添加成功: {filter_id}")
        
        return AddFilterResponse(
            success=True,
            filter_id=filter_id,
            message="滤镜添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加滤镜时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加滤镜失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_mask",
    response_model=AddMaskResponse,
    summary="添加蒙版",
    description="向视频片段添加蒙版"
)
async def add_video_mask(segment_id: str, request: AddMaskRequest):
    """
    添加蒙版
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_mask(MaskType.XXX, center_x=0.0, center_y=0.0, size=0.5)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加蒙版: {request.mask_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_mask", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加蒙版失败"
            )
        
        # 生成蒙版 ID
        import uuid
        mask_id = str(uuid.uuid4())
        
        logger.info(f"蒙版添加成功: {mask_id}")
        
        return AddMaskResponse(
            success=True,
            mask_id=mask_id,
            message="蒙版添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加蒙版时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加蒙版失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_transition",
    response_model=AddTransitionResponse,
    summary="添加转场",
    description="向视频片段添加转场"
)
async def add_video_transition(segment_id: str, request: AddTransitionRequest):
    """
    添加转场
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_transition(TransitionType.XXX, duration="1s")
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加转场: {request.transition_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_transition", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加转场失败"
            )
        
        # 生成转场 ID
        import uuid
        transition_id = str(uuid.uuid4())
        
        logger.info(f"转场添加成功: {transition_id}")
        
        return AddTransitionResponse(
            success=True,
            transition_id=transition_id,
            message="转场添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加转场时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加转场失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_background_filling",
    response_model=AddBackgroundFillingResponse,
    summary="添加背景填充",
    description="向视频片段添加背景填充"
)
async def add_video_background_filling(segment_id: str, request: AddBackgroundFillingRequest):
    """
    添加背景填充
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_background_filling("blur", blur=0.0625)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加背景填充: {request.fill_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_background_filling", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加背景填充失败"
            )
        
        logger.info("背景填充添加成功")
        
        return AddBackgroundFillingResponse(
            success=True,
            message="背景填充添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加背景填充时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加背景填充失败: {str(e)}"
        )


@router.post(
    "/video/{segment_id}/add_keyframe",
    response_model=AddKeyframeResponse,
    summary="添加视觉属性关键帧",
    description="向视频片段添加视觉属性关键帧"
)
async def add_video_keyframe(segment_id: str, request: AddKeyframeRequest):
    """
    添加视觉属性关键帧
    
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加关键帧")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 video，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_keyframe", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加关键帧失败"
            )
        
        # 生成关键帧 ID
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        logger.info(f"关键帧添加成功: {keyframe_id}")
        
        return AddKeyframeResponse(
            success=True,
            keyframe_id=keyframe_id,
            message="关键帧添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加关键帧时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加关键帧失败: {str(e)}"
        )


# ==================== StickerSegment 操作端点 ====================

@router.post(
    "/sticker/{segment_id}/add_keyframe",
    response_model=AddKeyframeResponse,
    summary="添加视觉属性关键帧",
    description="向贴纸片段添加视觉属性关键帧"
)
async def add_sticker_keyframe(segment_id: str, request: AddKeyframeRequest):
    """
    添加视觉属性关键帧
    
    对应 pyJianYingDraft 代码：
    ```python
    sticker_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为贴纸片段 {segment_id} 添加关键帧")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "sticker":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 sticker，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_keyframe", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加关键帧失败"
            )
        
        # 生成关键帧 ID
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        logger.info(f"关键帧添加成功: {keyframe_id}")
        
        return AddKeyframeResponse(
            success=True,
            keyframe_id=keyframe_id,
            message="关键帧添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加关键帧时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加关键帧失败: {str(e)}"
        )


# ==================== TextSegment 操作端点 ====================

@router.post(
    "/text/{segment_id}/add_animation",
    response_model=AddAnimationResponse,
    summary="添加文字动画",
    description="向文本片段添加文字动画"
)
async def add_text_animation(segment_id: str, request: AddAnimationRequest):
    """
    添加文字动画
    
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_animation(TextIntro.XXX, duration="1s")
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加动画: {request.animation_type}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "text":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 text，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_animation", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加动画失败"
            )
        
        # 生成动画 ID
        import uuid
        animation_id = str(uuid.uuid4())
        
        logger.info(f"文字动画添加成功: {animation_id}")
        
        return AddAnimationResponse(
            success=True,
            animation_id=animation_id,
            message="文字动画添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加文字动画时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加文字动画失败: {str(e)}"
        )


@router.post(
    "/text/{segment_id}/add_bubble",
    response_model=AddBubbleResponse,
    summary="添加气泡",
    description="向文本片段添加气泡"
)
async def add_text_bubble(segment_id: str, request: AddBubbleRequest):
    """
    添加气泡
    
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_bubble(effect_id, resource_id)
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加气泡")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "text":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 text，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_bubble", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加气泡失败"
            )
        
        # 生成气泡 ID
        import uuid
        bubble_id = str(uuid.uuid4())
        
        logger.info(f"气泡添加成功: {bubble_id}")
        
        return AddBubbleResponse(
            success=True,
            bubble_id=bubble_id,
            message="气泡添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加气泡时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加气泡失败: {str(e)}"
        )


@router.post(
    "/text/{segment_id}/add_effect",
    response_model=AddTextEffectResponse,
    summary="添加花字特效",
    description="向文本片段添加花字特效"
)
async def add_text_effect(segment_id: str, request: AddTextEffectRequest):
    """
    添加花字特效
    
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_effect("7296357486490144036")
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加花字特效")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "text":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 text，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_effect", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加花字特效失败"
            )
        
        # 生成特效 ID
        import uuid
        effect_id = str(uuid.uuid4())
        
        logger.info(f"花字特效添加成功: {effect_id}")
        
        return AddTextEffectResponse(
            success=True,
            effect_id=effect_id,
            message="花字特效添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加花字特效时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加花字特效失败: {str(e)}"
        )


@router.post(
    "/text/{segment_id}/add_keyframe",
    response_model=AddKeyframeResponse,
    summary="添加视觉属性关键帧",
    description="向文本片段添加视觉属性关键帧"
)
async def add_text_keyframe(segment_id: str, request: AddKeyframeRequest):
    """
    添加视觉属性关键帧
    
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加关键帧")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        if segment["segment_type"] != "text":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型错误，期望 text，实际 {segment['segment_type']}"
            )
        
        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_keyframe", operation_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加关键帧失败"
            )
        
        # 生成关键帧 ID
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        logger.info(f"关键帧添加成功: {keyframe_id}")
        
        return AddKeyframeResponse(
            success=True,
            keyframe_id=keyframe_id,
            message="关键帧添加成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加关键帧时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加关键帧失败: {str(e)}"
        )


# ==================== 查询端点 ====================

@router.get(
    "/{segment_type}/{segment_id}",
    response_model=SegmentDetailResponse,
    summary="查询 Segment 详情",
    description="根据 segment_id 和 segment_type 查询片段的详细信息"
)
async def get_segment_detail(segment_type: str, segment_id: str):
    """
    查询片段详情
    
    返回片段的配置、状态、下载状态等信息
    """
    logger.info(f"查询片段详情: {segment_type}/{segment_id}")
    
    try:
        segment = segment_manager.get_segment(segment_id)
        
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"片段 {segment_id} 不存在"
            )
        
        # 验证类型匹配
        if segment["segment_type"] != segment_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"片段类型不匹配，期望 {segment_type}，实际 {segment['segment_type']}"
            )
        
        # 构建响应
        config = segment.get("config", {})
        material_url = config.get("material_url")
        
        # 构建属性信息
        properties = {
            "config": config,
            "operations": segment.get("operations", []),
            "status": segment.get("status"),
            "created_timestamp": segment.get("created_timestamp"),
            "last_modified": segment.get("last_modified")
        }
        
        return SegmentDetailResponse(
            segment_id=segment_id,
            segment_type=segment["segment_type"],
            material_url=material_url,
            download_status=segment.get("download_status", "none"),
            local_path=segment.get("local_path"),
            properties=properties
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询片段详情时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询片段详情失败: {str(e)}"
        )
