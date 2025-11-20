"""
Segment API 路由
提供符合 API_ENDPOINTS_REFERENCE.md 规范的 Segment 创建和操作 API 端点

更新说明：
- 所有响应使用 APIResponseManager 统一管理
- 始终返回 success=True（便于 Coze 插件测试）
- 错误详情通过 error_code 和 message 字段传递
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status

from app.schemas.segment_schemas import (
    # Segment 操作 - Audio
    AddAudioEffectRequest,
    AddAudioEffectResponse,
    AddAudioFadeRequest,
    AddAudioFadeResponse,
    AddAudioKeyframeRequest,
    AddAudioKeyframeResponse,
    # Segment 操作 - Sticker
    AddStickerKeyframeRequest,
    AddStickerKeyframeResponse,
    # Segment 操作 - Text
    AddTextAnimationRequest,
    AddTextAnimationResponse,
    AddTextBubbleRequest,
    AddTextBubbleResponse,
    AddTextEffectRequest,
    AddTextEffectResponse,
    AddTextKeyframeRequest,
    AddTextKeyframeResponse,
    AddVideoAnimationRequest,
    AddVideoAnimationResponse,
    AddVideoBackgroundFillingRequest,
    AddVideoBackgroundFillingResponse,
    # Segment 操作 - Video
    AddVideoEffectRequest,
    AddVideoEffectResponse,
    AddVideoFadeRequest,
    AddVideoFadeResponse,
    AddVideoFilterRequest,
    AddVideoFilterResponse,
    AddVideoKeyframeRequest,
    AddVideoKeyframeResponse,
    AddVideoMaskRequest,
    AddVideoMaskResponse,
    AddVideoTransitionRequest,
    AddVideoTransitionResponse,
    # Segment 创建
    CreateAudioSegmentRequest,
    CreateEffectSegmentRequest,
    CreateFilterSegmentRequest,
    CreateSegmentResponse,
    CreateStickerSegmentRequest,
    CreateTextSegmentRequest,
    CreateVideoSegmentRequest,
    # 查询
    SegmentDetailResponse,
)
from app.utils.api_response_manager import ErrorCode, get_response_manager
from app.utils.logger import get_logger
from app.utils.segment_manager import get_segment_manager

router = APIRouter(prefix="/api/segment", tags=["片段管理"])
logger = get_logger(__name__)
response_manager = get_response_manager()

# 获取全局片段管理器
segment_manager = get_segment_manager()


# ==================== Segment 创建端点 ====================


@router.post(
    "/audio/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建音频片段",
    description="创建音频片段并返回 UUID（总是返回 success=True）",
)
async def create_audio_segment(request: CreateAudioSegmentRequest) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment = draft.AudioSegment(
        "audio.mp3",
        trange("0s", "5s"),
        volume=0.6
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建音频片段, 并指定其时间信息、音量、播放速度等设置
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            material (`AudioMaterial` or `str`): 素材实例或素材路径, 若为路径则自动构造素材实例
            target_timerange (`Timerange`): 片段在轨道上的目标时间范围
            source_timerange (`Timerange`, optional): 截取的素材片段的时间范围, 默认从开头根据`speed`截取与`target_timerange`等长的一部分
            speed (`float`, optional): 播放速度, 默认为1.0. 此项与`source_timerange`同时指定时, 将覆盖`target_timerange`中的时长
            volume (`float`, optional): 音量, 默认为1.0
            change_pitch (`bool`, optional): 是否跟随变速改变音调, 默认为否

        Raises:
            `ValueError`: 指定的或计算出的`source_timerange`超出了素材的时长范围
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
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"音频片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建音频片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(CreateSegmentResponse, e, segment_id="")


@router.post(
    "/video/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建视频片段",
    description="创建视频片段并返回 UUID",
)
async def create_video_segment(request: CreateVideoSegmentRequest) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment = draft.VideoSegment(
        VideoMaterial("video.mp4"),
        trange("0s", "5s")
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建视频片段, 并指定其时间信息、音量、播放速度及图像调节设置
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            material (`VideoMaterial` or `str`): 素材实例或素材路径, 若为路径则自动构造素材实例(此时不能指定`cropSettings`参数)
            target_timerange (`Timerange`): 片段在轨道上的目标时间范围
            source_timerange (`Timerange`, optional): 截取的素材片段的时间范围, 默认从开头根据`speed`截取与`target_timerange`等长的一部分
            speed (`float`, optional): 播放速度, 默认为1.0. 此项与`source_timerange`同时指定时, 将覆盖`target_timerange`中的时长
            volume (`float`, optional): 音量, 默认为1.0
            change_pitch (`bool`, optional): 是否跟随变速改变音调, 默认为否
            clip_settings (`ClipSettings`, optional): 图像调节设置, 默认不作任何变换

        Raises:
            `ValueError`: 指定的或计算出的`source_timerange`超出了素材的时长范围
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
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"视频片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建视频片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateSegmentResponse,
            error=e,
            segment_id=""
        )


@router.post(
    "/text/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建文本片段",
    description="创建文本片段并返回 UUID",
)
async def create_text_segment(request: CreateTextSegmentRequest) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment = draft.TextSegment(
        "Hello World",
        trange("0s", "3s")
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建文本片段, 并指定其时间信息、字体样式及图像调节设置
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            text (`str`): 文本内容
            timerange (`Timerange`): 片段在轨道上的时间范围
            font (`Font_type`, optional): 字体类型, 默认为系统字体
            style (`TextStyle`, optional): 字体样式, 包含大小/颜色/对齐/透明度等.
            clip_settings (`ClipSettings`, optional): 图像调节设置, 默认不做任何变换
            border (`TextBorder`, optional): 文本描边参数, 默认无描边
            background (`TextBackground`, optional): 文本背景参数, 默认无背景
            shadow (`TextShadow`, optional): 文本阴影参数, 默认无阴影
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
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"文本片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建文本片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateSegmentResponse,
            error=e,
            segment_id=""
        )


@router.post(
    "/sticker/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建贴纸片段",
    description="创建贴纸片段并返回 UUID",
)
async def create_sticker_segment(
    request: CreateStickerSegmentRequest,
) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    sticker_segment = draft.StickerSegment(
        resource_id,
        trange("0s", "3s")
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建贴纸片段, 并指定其时间信息及图像调节设置
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            resource_id (`str`): 贴纸resource_id, 可通过`ScriptFile.inspect_material`从模板中获取
            target_timerange (`Timerange`): 片段在轨道上的目标时间范围
            clip_settings (`ClipSettings`, optional): 图像调节设置, 默认不作任何变换
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
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"贴纸片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建贴纸片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateSegmentResponse,
            error=e,
            segment_id=""
        )


@router.post(
    "/effect/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建特效片段",
    description="创建特效片段并返回 UUID",
)
async def create_effect_segment(request: CreateEffectSegmentRequest) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    effect_segment = draft.EffectSegment(
        VideoSceneEffectType.XXX,
        trange("0s", "5s"),
        params=[50.0, 75.0]
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建特效片段, 并指定其时间信息及特效参数
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            effect_type (`VideoSceneEffectType` or `VideoCharacterEffectType`): 特效类型
            target_timerange (`Timerange`): 片段在轨道上的时间范围
            params (`List[Optional[float]]`, optional): 特效参数列表, 参数列表中未提供或为None的项使用默认值. 参数取值范围(0~100)与剪映中一致. 某个特效类型有何参数以及具体参数顺序以枚举类成员的annotation为准.

        Raises:
            `ValueError`: 提供的参数数量超过了该特效类型的参数数量, 或参数值超出范围.
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建特效片段请求")
    logger.info(f"特效类型: {request.effect_type}")

    try:
        # 准备配置
        config = request.dict()

        # 创建片段
        result = segment_manager.create_segment("effect", config)

        if not result["success"]:
            logger.error(f"特效片段创建失败: {result['message']}")
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"特效片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建特效片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateSegmentResponse,
            error=e,
            segment_id=""
        )


@router.post(
    "/filter/create",
    response_model=CreateSegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="创建滤镜片段",
    description="创建滤镜片段并返回 UUID",
)
async def create_filter_segment(request: CreateFilterSegmentRequest) -> CreateSegmentResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    filter_segment = draft.FilterSegment(
        FilterType.XXX,
        trange("0s", "5s"),
        intensity=100.0
    )
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建滤镜片段, 并指定其时间信息及滤镜强度
        片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

        Args:
            filter_meta (`FilterType`): 滤镜类型
            target_timerange (`Timerange`): 片段在轨道上的时间范围
            intensity (`float`, optional): 滤镜强度(0-100). 仅当所选滤镜能够调节强度时有效. 默认为100.
    ```
    """
    logger.info("=" * 60)
    logger.info("收到创建滤镜片段请求")
    logger.info(f"滤镜类型: {request.filter_type}")

    try:
        # 准备配置
        config = request.dict()

        # 创建片段
        result = segment_manager.create_segment("filter", config)

        if not result["success"]:
            logger.error(f"滤镜片段创建失败: {result['message']}")
            logger.info("=" * 60)
            return response_manager.error_response(
                CreateSegmentResponse,
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]},
                segment_id=""
            )

        logger.info(f"滤镜片段创建成功: {result['segment_id']}")
        logger.info("=" * 60)

        return response_manager.success_response(
            CreateSegmentResponse,
            message=result["message"],
            segment_id=result["segment_id"]
        )

    except Exception as e:
        logger.error(f"创建滤镜片段时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            CreateSegmentResponse,
            error=e,
            segment_id=""
        )


# ==================== AudioSegment 操作端点 ====================


@router.post(
    "/audio/{segment_id}/add_effect",
    response_model=AddAudioEffectResponse,
    status_code=status.HTTP_200_OK,
    summary="添加音频特效",
    description="向音频片段添加音效",
)
async def add_audio_effect(segment_id: str, request: AddAudioEffectRequest) -> AddAudioEffectResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_effect(AudioSceneEffectType.XXX, params)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为音频片段添加音效, 可配置音效类型及参数
        音效将应用于整个片段, 每种类型的音效只能添加一次

        Args:
            effect_type (`AudioSceneEffectType` | `ToneEffectType` | `SpeechToSongType`): 音效类型, 一类音效只能添加一个.
            params (`List[Optional[float]]`, optional): 音效参数列表, 参数列表中未提供或为None的项使用默认值.
                参数取值范围(0~100)与剪映中一致. 某个特效类型有何参数以及具体参数顺序以枚举类成员的annotation为准.

        Raises:
            `ValueError`: 试图添加一个已经存在的音效类型、提供的参数数量超过了该音效类型的参数数量, 或参数值超出范围.
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加特效: {request.effect_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.not_found_response(AddAudioEffectResponse, "segment", segment_id, effect_id="")

        if segment["segment_type"] != "audio":
            logger.error(f"片段类型错误: 期望 audio，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddAudioEffectResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "audio", "actual": segment["segment_type"]},
                effect_id=""
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_effect", operation_data
        )

        if not success:
            logger.error("添加特效失败")
            return response_manager.error_response(
                AddAudioEffectResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加特效失败"},
                effect_id=""
            )

        # 生成特效 ID
        import uuid

        effect_id = str(uuid.uuid4())

        logger.info(f"音频特效添加成功: {effect_id}")

        return response_manager.success_response(
            AddAudioEffectResponse,
            message="音频特效添加成功",
            effect_id=effect_id
        )

    except Exception as e:
        logger.error(f"添加音频特效失败: {e}", exc_info=True)
        return response_manager.internal_error_response(AddAudioEffectResponse, e, effect_id="")


@router.post(
    "/audio/{segment_id}/add_fade",
    response_model=AddAudioFadeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加淡入淡出",
    description="向音频片段添加淡入淡出效果",
)
async def add_audio_fade(segment_id: str, request: AddAudioFadeRequest) -> AddAudioFadeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_fade("1s", "0s")
    ```
    对应 pyJianYingDraft 注释：
    ```
        为音频片段添加淡入淡出效果, 可配置淡入淡出的时长
        淡入淡出将应用于片段的开头和结尾部分

        Args:
            in_duration (`int` or `str`): 音频淡入时长, 单位为微秒, 若为字符串则会调用`tim()`函数进行解析
            out_duration (`int` or `str`): 音频淡出时长, 单位为微秒, 若为字符串则会调用`tim()`函数进行解析

        Raises:
            `ValueError`: 当前片段已存在淡入淡出效果
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加淡入淡出")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.not_found_response(AddAudioFadeResponse, "segment", segment_id)

        if segment["segment_type"] != "audio":
            logger.error(f"片段类型错误: 期望 audio，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddAudioFadeResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "audio", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_fade", operation_data)

        if not success:
            logger.error("添加淡入淡出失败")
            return response_manager.error_response(
                AddAudioFadeResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加淡入淡出失败"},
            )

        logger.info("淡入淡出添加成功")

        return response_manager.success_response(AddAudioFadeResponse, message="淡入淡出添加成功")

    except Exception as e:
        logger.error(f"添加淡入淡出失败: {e}", exc_info=True)
        return response_manager.internal_error_response(AddAudioFadeResponse, e)


@router.post(
    "/audio/{segment_id}/add_keyframe",
    response_model=AddAudioKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加音量关键帧",
    description="向音频片段添加音量关键帧",
)
async def add_audio_keyframe(segment_id: str, request: AddAudioKeyframeRequest) -> AddAudioKeyframeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment.add_keyframe("2s", 0.8)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为音频片段添加音量关键帧, 可精确控制音量随时间变化
        关键帧可用于实现复杂的音量变化效果

        Args:
            time_offset (`int`): 关键帧的时间偏移量, 单位为微秒
            volume (`float`): 音量在`time_offset`处的值
    ```
    """
    logger.info(f"为音频片段 {segment_id} 添加关键帧")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.not_found_response(AddAudioKeyframeResponse, "segment", segment_id, keyframe_id="")

        if segment["segment_type"] != "audio":
            logger.error(f"片段类型错误: 期望 audio，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddAudioKeyframeResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "audio", "actual": segment["segment_type"]},
                keyframe_id=""
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )

        if not success:
            logger.error("添加关键帧失败")
            return response_manager.error_response(
                AddAudioKeyframeResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
                keyframe_id=""
            )

        # 生成关键帧 ID
        import uuid

        keyframe_id = str(uuid.uuid4())

        logger.info(f"关键帧添加成功: {keyframe_id}")

        return response_manager.success_response(
            AddAudioKeyframeResponse,
            message="关键帧添加成功",
            keyframe_id=keyframe_id
        )

    except Exception as e:
        logger.error(f"添加关键帧失败: {e}", exc_info=True)
        return response_manager.internal_error_response(AddAudioKeyframeResponse, e, keyframe_id="")


# ==================== VideoSegment 操作端点 ====================


@router.post(
    "/video/{segment_id}/add_animation",
    response_model=AddVideoAnimationResponse,
    status_code=status.HTTP_200_OK,
    summary="添加动画",
    description="向视频片段添加入场/出场动画",
)
async def add_video_animation(segment_id: str, request: AddVideoAnimationRequest) -> AddVideoAnimationResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_animation(IntroType.XXX, duration="1s")
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加动画效果, 可配置动画类型及参数
        动画将应用于片段的进出场或全程

        Args:
            animation_type (`IntroType`, `OutroType`, or `GroupAnimationType`): 动画类型
            duration (`int` or `str`, optional): 动画持续时间, 单位为微秒. 若传入字符串则会调用`tim()`函数进行解析.
                若不指定则使用动画类型定义的默认值. 理论上只适用于入场和出场动画.
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加动画: {request.animation_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.not_found_response(AddVideoAnimationResponse, "segment", segment_id, animation_id="")

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddVideoAnimationResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
                animation_id=""
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_animation", operation_data
        )

        if not success:
            logger.error("添加动画失败")
            return response_manager.error_response(
                AddVideoAnimationResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加动画失败"},
                animation_id=""
            )

        # 生成动画 ID
        import uuid

        animation_id = str(uuid.uuid4())

        logger.info(f"动画添加成功: {animation_id}")

        return response_manager.success_response(
            AddVideoAnimationResponse,
            message="动画添加成功",
            animation_id=animation_id
        )

    except Exception as e:
        logger.error(f"添加动画失败: {e}", exc_info=True)
        return response_manager.internal_error_response(AddVideoAnimationResponse, e, animation_id="")


@router.post(
    "/video/{segment_id}/add_effect",
    response_model=AddVideoEffectResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视频特效",
    description="向视频片段添加视频特效",
)
async def add_video_effect(segment_id: str, request: AddVideoEffectRequest) -> AddVideoEffectResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_effect(VideoSceneEffectType.XXX, params)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加视频特效, 可配置特效类型及参数
        特效将应用于整个片段或指定时间段

        Args:
            effect_type (`VideoSceneEffectType` or `VideoCharacterEffectType`): 特效类型
            params (`List[Optional[float]]`, optional): 特效参数列表, 参数列表中未提供或为None的项使用默认值.
                参数取值范围(0~100)与剪映中一致. 某个特效类型有何参数以及具体参数顺序以枚举类成员的annotation为准.

        Raises:
            `ValueError`: 提供的参数数量超过了该特效类型的参数数量, 或参数值超出范围.
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加特效: {request.effect_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.not_found_response(AddVideoEffectResponse, "segment", segment_id, effect_id="")

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddVideoEffectResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
                effect_id=""
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_effect", operation_data
        )

        if not success:
            logger.error("添加特效失败")
            return response_manager.error_response(
                AddVideoEffectResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加特效失败"},
                effect_id=""
            )

        # 生成特效 ID
        import uuid

        effect_id = str(uuid.uuid4())

        logger.info(f"视频特效添加成功: {effect_id}")

        return response_manager.success_response(
            AddVideoEffectResponse,
            message="视频特效添加成功",
            effect_id=effect_id
        )

    except Exception as e:
        logger.error(f"添加视频特效失败: {e}", exc_info=True)
        return response_manager.internal_error_response(AddVideoEffectResponse, e, effect_id="")


@router.post(
    "/video/{segment_id}/add_fade",
    response_model=AddVideoFadeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加淡入淡出",
    description="向视频片段添加淡入淡出效果",
)
async def add_video_fade(segment_id: str, request: AddVideoFadeRequest) -> AddVideoFadeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    # VideoSegment 没有 add_fade 方法
    # 此 API 可能与实际的 pyJianYingDraft 功能不对应
    ```
    对应 pyJianYingDraft 注释：
    ```
        VideoSegment 没有 add_fade 方法
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加淡入淡出")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_fade", operation_data)

        if not success:
            logger.error("添加淡入淡出失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加淡入淡出失败"},
            )

        logger.info("淡入淡出添加成功")

        return response_manager.success(message="淡入淡出添加成功")

    except Exception as e:
        logger.error(f"添加淡入淡出失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/video/{segment_id}/add_filter",
    response_model=AddVideoFilterResponse,
    status_code=status.HTTP_200_OK,
    summary="添加滤镜",
    description="向视频片段添加滤镜",
)
async def add_video_filter(segment_id: str, request: AddVideoFilterRequest) -> AddVideoFilterResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_filter(FilterType.XXX, intensity=100.0)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加淡入淡出效果, 可配置淡入淡出的时长
        淡入淡出将应用于片段的开头和结尾部分

        Args:
            filter_type (`FilterType`): 滤镜类型
            intensity (`float`, optional): 滤镜强度(0-100), 仅当所选滤镜能够调节强度时有效. 默认为100.
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加滤镜: {request.filter_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_filter", operation_data
        )

        if not success:
            logger.error("添加滤镜失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加滤镜失败"},
            )

        # 生成滤镜 ID
        import uuid

        filter_id = str(uuid.uuid4())

        logger.info(f"滤镜添加成功: {filter_id}")

        success_response = response_manager.success(message="滤镜添加成功")
        return {"filter_id": filter_id, **success_response}

    except Exception as e:
        logger.error(f"添加滤镜失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/video/{segment_id}/add_mask",
    response_model=AddVideoMaskResponse,
    status_code=status.HTTP_200_OK,
    summary="添加蒙版",
    description="向视频片段添加蒙版",
)
async def add_video_mask(segment_id: str, request: AddVideoMaskRequest) -> AddVideoMaskResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_mask(MaskType.XXX, center_x=0.0, center_y=0.0, size=0.5)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加滤镜效果, 可配置滤镜类型及强度
        滤镜将应用于整个片段或指定时间段

        Args:
            mask_type (`MaskType`): 蒙版类型
            center_x (`float`, optional): 蒙版中心点X坐标(以素材的像素为单位), 默认设置在素材中心
            center_y (`float`, optional): 蒙版中心点Y坐标(以素材的像素为单位), 默认设置在素材中心
            size (`float`, optional): 蒙版的"主要尺寸"(镜面的可视部分高度/圆形直径/爱心高度等), 以占素材高度的比例表示, 默认为0.5
            rotation (`float`, optional): 蒙版顺时针旋转的**角度**, 默认不旋转
            feather (`float`, optional): 蒙版的羽化参数, 取值范围0~100, 默认无羽化
            invert (`bool`, optional): 是否反转蒙版, 默认不反转
            rect_width (`float`, optional): 矩形蒙版的宽度, 仅在蒙版类型为矩形时允许设置, 以占素材宽度的比例表示, 默认与`size`相同
            round_corner (`float`, optional): 矩形蒙版的圆角参数, 仅在蒙版类型为矩形时允许设置, 取值范围0~100, 默认为0

        Raises:
            `ValueError`: 试图添加多个蒙版或不正确地设置了`rect_width`及`round_corner`
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加蒙版: {request.mask_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(segment_id, "add_mask", operation_data)

        if not success:
            logger.error("添加蒙版失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加蒙版失败"},
            )

        # 生成蒙版 ID
        import uuid

        mask_id = str(uuid.uuid4())

        logger.info(f"蒙版添加成功: {mask_id}")

        success_response = response_manager.success(message="蒙版添加成功")
        return {"mask_id": mask_id, **success_response}

    except Exception as e:
        logger.error(f"添加蒙版失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/video/{segment_id}/add_transition",
    response_model=AddVideoTransitionResponse,
    status_code=status.HTTP_200_OK,
    summary="添加转场",
    description="向视频片段添加转场",
)
async def add_video_transition(segment_id: str, request: AddVideoTransitionRequest) -> AddVideoTransitionResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_transition(TransitionType.XXX, duration="1s")
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加蒙版效果, 可配置蒙版类型及参数
        蒙版可用于实现各种遮罩和形状效果

        Args:
            transition_type (`TransitionType`): 转场类型
            duration (`int` or `str`, optional): 转场持续时间, 单位为微秒. 若传入字符串则会调用`tim()`函数进行解析. 若不指定则使用转场类型定义的默认值.

        Raises:
            `ValueError`: 试图添加多个转场.
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加转场: {request.transition_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_transition", operation_data
        )

        if not success:
            logger.error("添加转场失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加转场失败"},
            )

        # 生成转场 ID
        import uuid

        transition_id = str(uuid.uuid4())

        logger.info(f"转场添加成功: {transition_id}")

        success_response = response_manager.success(message="转场添加成功")
        return {"transition_id": transition_id, **success_response}

    except Exception as e:
        logger.error(f"添加转场失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/video/{segment_id}/add_background_filling",
    response_model=AddVideoBackgroundFillingResponse,
    status_code=status.HTTP_200_OK,
    summary="添加背景填充",
    description="向视频片段添加背景填充",
)
async def add_video_background_filling(
    segment_id: str, request: AddVideoBackgroundFillingRequest
) -> AddVideoBackgroundFillingResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_background_filling("blur", blur=0.0625)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加转场效果, 可配置转场类型及时长
        转场将应用于片段与下一片段的衔接处

        Args:
            fill_type (`blur` or `color`): 填充类型, `blur`表示模糊, `color`表示颜色.
            blur (`float`, optional): 模糊程度, 0.0-1.0. 仅在`fill_type`为`blur`时有效. 剪映中的四档模糊数值分别为0.0625, 0.375, 0.75和1.0, 默认为0.0625.
            color (`str`, optional): 填充颜色, 格式为'#RRGGBBAA'. 仅在`fill_type`为`color`时有效.

        Raises:
            `ValueError`: 当前片段已有背景填充效果或`fill_type`无效.
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加背景填充: {request.fill_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_background_filling", operation_data
        )

        if not success:
            logger.error("添加背景填充失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加背景填充失败"},
            )

        logger.info("背景填充添加成功")

        return AddVideoBackgroundFillingResponse(
            success=True, message="背景填充添加成功"
        )

    except Exception as e:
        logger.error(f"添加背景填充失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/video/{segment_id}/add_keyframe",
    response_model=AddVideoKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视频关键帧",
    description="向视频片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_video_keyframe(segment_id: str, request: AddVideoKeyframeRequest) -> AddVideoKeyframeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加关键帧, 可精确控制位置、大小、旋转等参数随时间变化
        关键帧可用于实现复杂的动画效果

        Args:
            _property (`KeyframeProperty`): 要控制的属性
            time_offset (`int` or `str`): 关键帧的时间偏移量, 单位为微秒. 若传入字符串则会调用`tim()`函数进行解析.
            value (`float`): 属性在`time_offset`处的值

        Raises:
            `ValueError`: 试图同时设置`uniform_scale`以及`scale_x`或`scale_y`其中一者
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加关键帧")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )

        if not success:
            logger.error("添加关键帧失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )

        # 生成关键帧 ID
        import uuid

        keyframe_id = str(uuid.uuid4())

        logger.info(f"关键帧添加成功: {keyframe_id}")

        success_response = response_manager.success(message="关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}

    except Exception as e:
        logger.error(f"添加关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


# ==================== TextSegment 操作端点 ====================


# ==================== StickerSegment 操作端点 ====================


@router.post(
    "/sticker/{segment_id}/add_keyframe",
    response_model=AddStickerKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧",
    description="向贴纸片段添加视觉属性关键帧",
)
async def add_sticker_keyframe(segment_id: str, request: AddStickerKeyframeRequest) -> AddStickerKeyframeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    sticker_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为视频片段添加关键帧, 可精确控制位置、大小、旋转等参数随时间变化
        关键帧可用于实现复杂的动画效果

        Args:
            _property (`KeyframeProperty`): 要控制的属性
            time_offset (`int` or `str`): 关键帧的时间偏移量, 单位为微秒. 若传入字符串则会调用`tim()`函数进行解析.
            value (`float`): 属性在`time_offset`处的值

        Raises:
            `ValueError`: 试图同时设置`uniform_scale`以及`scale_x`或`scale_y`其中一者
    ```
    """
    logger.info(f"为贴纸片段 {segment_id} 添加关键帧")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "sticker":
            logger.error(f"片段类型错误: 期望 sticker，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "sticker", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )

        if not success:
            logger.error("添加关键帧失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )

        # 生成关键帧 ID
        import uuid

        keyframe_id = str(uuid.uuid4())

        logger.info(f"关键帧添加成功: {keyframe_id}")

        success_response = response_manager.success(message="关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}

    except Exception as e:
        logger.error(f"添加关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


# ==================== TextSegment 操作端点 ====================


@router.post(
    "/text/{segment_id}/add_animation",
    response_model=AddTextAnimationResponse,
    status_code=status.HTTP_200_OK,
    summary="添加文本动画",
    description="向文本片段添加入场/出场动画",
)
async def add_text_animation(segment_id: str, request: AddTextAnimationRequest) -> AddTextAnimationResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_animation(TextIntro.XXX, duration="1s")
    ```
    对应 pyJianYingDraft 注释：
    ```
        为贴纸片段添加关键帧, 可精确控制位置、大小、旋转等参数随时间变化
        关键帧可用于实现复杂的动画效果

        Args:
            animation_type (`TextIntro`, `TextOutro` or `TextLoopAnim`): 文本动画类型.
            duration (`str` or `float`, optional): 动画持续时间, 单位为微秒, 仅对入场/出场动画有效.
                若传入字符串则会调用`tim()`函数进行解析. 默认使用动画的时长
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加动画: {request.animation_type}")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "text":
            logger.error(f"片段类型错误: 期望 text，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "text", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_animation", operation_data
        )

        if not success:
            logger.error("添加动画失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加动画失败"},
            )

        # 生成动画 ID
        import uuid

        animation_id = str(uuid.uuid4())

        logger.info(f"文字动画添加成功: {animation_id}")

        success_response = response_manager.success(message="文字动画添加成功")
        return {"animation_id": animation_id, **success_response}

    except Exception as e:
        logger.error(f"添加文字动画失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/text/{segment_id}/add_bubble",
    response_model=AddTextBubbleResponse,
    status_code=status.HTTP_200_OK,
    summary="添加气泡",
    description="向文本片段添加气泡",
)
async def add_text_bubble(segment_id: str, request: AddTextBubbleRequest) -> AddTextBubbleResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_bubble(effect_id, resource_id)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为文本片段添加动画效果, 可配置动画类型及参数
        动画将应用于文本的进出场或全程

        Args:
            effect_id (`str`): 气泡效果的effect_id
            resource_id (`str`): 气泡效果的resource_id
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加气泡")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "text":
            logger.error(f"片段类型错误: 期望 text，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "text", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_bubble", operation_data
        )

        if not success:
            logger.error("添加气泡失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加气泡失败"},
            )

        # 生成气泡 ID
        import uuid

        bubble_id = str(uuid.uuid4())

        logger.info(f"气泡添加成功: {bubble_id}")

        success_response = response_manager.success(message="气泡添加成功")
        return {"bubble_id": bubble_id, **success_response}

    except Exception as e:
        logger.error(f"添加气泡失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/text/{segment_id}/add_effect",
    response_model=AddTextEffectResponse,
    status_code=status.HTTP_200_OK,
    summary="添加花字特效",
    description="向文本片段添加花字特效",
)
async def add_text_effect(segment_id: str, request: AddTextEffectRequest) -> AddTextEffectResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_effect("7296357486490144036")
    ```
    对应 pyJianYingDraft 注释：
    ```
        为文本片段添加气泡效果, 可配置气泡样式及参数
        气泡可用于实现对话框和标注效果

        Args:
            effect_id (`str`): 花字效果的effect_id, 也同时是其resource_id
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加花字特效")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "text":
            logger.error(f"片段类型错误: 期望 text，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "text", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_effect", operation_data
        )

        if not success:
            logger.error("添加花字特效失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加花字特效失败"},
            )

        # 生成特效 ID
        import uuid

        effect_id = str(uuid.uuid4())

        logger.info(f"花字特效添加成功: {effect_id}")

        return AddTextEffectResponse(
            success=True, effect_id=effect_id, message="花字特效添加成功"
        )

    except Exception as e:
        logger.error(f"添加花字特效失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


@router.post(
    "/text/{segment_id}/add_keyframe",
    response_model=AddTextKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧",
    description="向文本片段添加视觉属性关键帧",
)
async def add_text_keyframe(segment_id: str, request: AddTextKeyframeRequest) -> AddTextKeyframeResponse:
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    对应 pyJianYingDraft 注释：
    ```
        为文本片段添加文本特效, 可配置特效类型及参数
        特效将应用于整个文本或指定部分

        Args:
            _property (`KeyframeProperty`): 要控制的属性
            time_offset (`int` or `str`): 关键帧的时间偏移量, 单位为微秒. 若传入字符串则会调用`tim()`函数进行解析.
            value (`float`): 属性在`time_offset`处的值

        Raises:
            `ValueError`: 试图同时设置`uniform_scale`以及`scale_x`或`scale_y`其中一者
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加关键帧")

    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        if segment["segment_type"] != "text":
            logger.error(f"片段类型错误: 期望 text，实际 {segment['segment_type']}")
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "text", "actual": segment["segment_type"]},
            )

        # 记录操作
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )

        if not success:
            logger.error("添加关键帧失败")
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )

        # 生成关键帧 ID
        import uuid

        keyframe_id = str(uuid.uuid4())

        logger.info(f"关键帧添加成功: {keyframe_id}")

        success_response = response_manager.success(message="关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}

    except Exception as e:
        logger.error(f"添加关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)


# ==================== 查询端点 ====================


@router.get(
    "/{segment_type}/{segment_id}",
    response_model=SegmentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="查询 Segment 详情",
    description="根据 segment_id 和 segment_type 查询片段的详细信息（总是返回 success=True）",
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
            logger.error(f"片段不存在: {segment_id}")
            return response_manager.format_not_found_error("segment", segment_id)

        # 验证类型匹配
        if segment["segment_type"] != segment_type:
            logger.error(
                f"片段类型不匹配: 期望 {segment_type}，实际 {segment['segment_type']}"
            )
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": segment_type, "actual": segment["segment_type"]},
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
            "last_modified": segment.get("last_modified"),
        }

        success_response = response_manager.success(message="查询成功")
        return {
            "segment_id": segment_id,
            "segment_type": segment["segment_type"],
            "material_url": material_url,
            "download_status": segment.get("download_status", "none"),
            "local_path": segment.get("local_path"),
            "properties": properties,
            **success_response,
        }

    except Exception as e:
        logger.error(f"查询片段详情失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)
