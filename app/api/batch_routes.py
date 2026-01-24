"""
批量片段 API 路由
提供批量添加各类片段的 API 端点，与 Coze 插件工具接口保持一致

这些 API 用于批量添加片段到草稿，每次调用创建一个新轨道并添加所有指定的片段。
对应的 Coze 插件工具包括：
- add_audios: 批量添加音频片段
- add_captions: 批量添加字幕片段
- add_effects: 批量添加特效片段
- add_images: 批量添加图片片段
- add_videos: 批量添加视频片段
- add_sticker: 添加贴纸片段
- add_keyframes: 添加关键帧
- add_masks: 添加蒙版
"""

import json
import time
import uuid

from fastapi import APIRouter, status
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.segment_manager import get_segment_manager
from app.utils.logger import get_logger
from app.utils.api_response_manager import get_response_manager, ErrorCode

router = APIRouter(prefix="/api/batch", tags=["批量片段操作"])
logger = get_logger(__name__)
response_manager = get_response_manager()

# 获取全局管理器
draft_manager = get_draft_state_manager()
segment_manager = get_segment_manager()


# ==================== Request/Response Models ====================


class AddAudiosRequest(BaseModel):
    """批量添加音频请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    audio_infos: List[str] = Field(..., description="音频信息 JSON 字符串列表")


class AddAudiosResponse(BaseModel):
    """批量添加音频响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_ids: List[str] = Field(default_factory=list, description="生成的片段 UUID 列表")


class AddCaptionsRequest(BaseModel):
    """批量添加字幕请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    caption_infos: List[str] = Field(..., description="字幕信息 JSON 字符串列表")


class AddCaptionsResponse(BaseModel):
    """批量添加字幕响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_ids: List[str] = Field(default_factory=list, description="生成的片段 UUID 列表")


class AddEffectsRequest(BaseModel):
    """批量添加特效请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    effect_infos: List[str] = Field(..., description="特效信息 JSON 字符串列表")


class AddEffectsResponse(BaseModel):
    """批量添加特效响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_ids: List[str] = Field(default_factory=list, description="生成的片段 UUID 列表")


class AddImagesRequest(BaseModel):
    """批量添加图片请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    image_infos: List[str] = Field(..., description="图片信息 JSON 字符串列表")


class AddImagesResponse(BaseModel):
    """批量添加图片响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_ids: List[str] = Field(default_factory=list, description="生成的片段 UUID 列表")


class AddVideosRequest(BaseModel):
    """批量添加视频请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    video_infos: List[str] = Field(..., description="视频信息 JSON 字符串列表")


class AddVideosResponse(BaseModel):
    """批量添加视频响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_ids: List[str] = Field(default_factory=list, description="生成的片段 UUID 列表")


class AddStickerRequest(BaseModel):
    """添加贴纸请求"""
    draft_id: str = Field(..., description="草稿 UUID")
    sticker_info: str = Field(..., description="贴纸信息 JSON 字符串")


class AddStickerResponse(BaseModel):
    """添加贴纸响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    segment_id: str = Field(default="", description="生成的片段 UUID")


class AddKeyframesRequest(BaseModel):
    """添加关键帧请求"""
    segment_id: str = Field(..., description="片段 UUID")
    keyframe_infos: List[Dict[str, Any]] = Field(..., description="关键帧信息列表")


class AddKeyframesResponse(BaseModel):
    """添加关键帧响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    keyframe_ids: List[str] = Field(default_factory=list, description="生成的关键帧 UUID 列表")


class AddMasksRequest(BaseModel):
    """添加蒙版请求"""
    segment_id: str = Field(..., description="片段 UUID")
    mask_info: Dict[str, Any] = Field(..., description="蒙版信息")


class AddMasksResponse(BaseModel):
    """添加蒙版响应"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    error_code: str = Field(default="", description="错误代码")
    mask_id: str = Field(default="", description="生成的蒙版 UUID")


# ==================== API Endpoints ====================


@router.post(
    "/add_audios",
    response_model=AddAudiosResponse,
    status_code=status.HTTP_200_OK,
    summary="批量添加音频",
    description="批量添加音频片段到草稿，创建新的音频轨道"
)
async def add_audios(request: AddAudiosRequest) -> AddAudiosResponse:
    """
    批量添加音频片段
    
    与 Coze 插件工具 add_audios 接口保持一致
    每次调用创建一个包含所有指定音频的新轨道
    """
    logger.info("=" * 60)
    logger.info(f"收到批量添加音频请求: draft_id={request.draft_id}")
    logger.info(f"音频数量: {len(request.audio_infos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddAudiosResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_ids=[]
            )
        
        # 解析音频信息并创建片段
        
        segment_ids = []
        segments = []
        
        for i, audio_info_str in enumerate(request.audio_infos):
            try:
                # 解析 JSON 字符串
                audio_info = json.loads(audio_info_str)
                
                # 验证必需字段
                required_fields = ['audio_url', 'start', 'end']
                for field in required_fields:
                    if field not in audio_info:
                        raise ValueError(f"缺少必需字段 '{field}'")
                
                # 创建片段
                segment_id = str(uuid.uuid4())
                segment_ids.append(segment_id)
                
                segment = {
                    "id": segment_id,
                    "type": "audio",
                    "material_url": audio_info['audio_url'],
                    "time_range": {
                        "start": audio_info['start'],
                        "end": audio_info['end']
                    }
                }
                
                # 添加可选字段
                if 'material_start' in audio_info and 'material_end' in audio_info:
                    segment["material_range"] = {
                        "start": audio_info['material_start'],
                        "end": audio_info['material_end']
                    }
                
                # 音频属性
                audio_props = {}
                for key in ['volume', 'fade_in', 'fade_out', 'effect_type', 'effect_intensity', 'speed', 'change_pitch']:
                    if key in audio_info:
                        audio_props[key] = audio_info[key]
                
                if audio_props:
                    segment["audio"] = audio_props
                
                segments.append(segment)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析音频信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddAudiosResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": f"JSON 解析失败: {str(e)}"},
                    segment_ids=[]
                )
            except ValueError as e:
                logger.error(f"验证音频信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddAudiosResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    segment_ids=[]
                )
        
        # 创建音频轨道
        track = {
            "track_type": "audio",
            "segments": segments
        }
        
        # 添加轨道到草稿
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(track)
        
        # 更新时间戳
        config["last_modified"] = time.time()
        
        # 保存配置
        success = draft_manager.update_draft_config(request.draft_id, config)
        
        if not success:
            logger.error("保存草稿配置失败")
            return response_manager.error_response(
                AddAudiosResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "保存草稿配置失败"},
                segment_ids=[]
            )
        
        logger.info(f"成功添加 {len(segment_ids)} 个音频片段")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddAudiosResponse,
            message=f"成功添加 {len(segment_ids)} 个音频片段",
            segment_ids=segment_ids
        )
        
    except Exception as e:
        logger.error(f"批量添加音频时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddAudiosResponse,
            error=e,
            segment_ids=[]
        )


@router.post(
    "/add_captions",
    response_model=AddCaptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="批量添加字幕",
    description="批量添加字幕片段到草稿，创建新的文本轨道"
)
async def add_captions(request: AddCaptionsRequest) -> AddCaptionsResponse:
    """
    批量添加字幕片段
    
    与 Coze 插件工具 add_captions 接口保持一致
    每次调用创建一个包含所有指定字幕的新轨道
    """
    logger.info("=" * 60)
    logger.info(f"收到批量添加字幕请求: draft_id={request.draft_id}")
    logger.info(f"字幕数量: {len(request.caption_infos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddCaptionsResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_ids=[]
            )
        
        # 解析字幕信息并创建片段
        
        segment_ids = []
        segments = []
        
        for i, caption_info_str in enumerate(request.caption_infos):
            try:
                # 解析 JSON 字符串
                caption_info = json.loads(caption_info_str)
                
                # 验证必需字段
                required_fields = ['content', 'start', 'end']
                for field in required_fields:
                    if field not in caption_info:
                        raise ValueError(f"缺少必需字段 '{field}'")
                
                # 创建片段
                segment_id = str(uuid.uuid4())
                segment_ids.append(segment_id)
                
                segment = {
                    "id": segment_id,
                    "type": "text",
                    "content": caption_info['content'],
                    "time_range": {
                        "start": caption_info['start'],
                        "end": caption_info['end']
                    }
                }
                
                # 添加变换属性
                transform = {}
                for key in ['position_x', 'position_y', 'scale', 'rotation', 'opacity']:
                    if key in caption_info:
                        transform[key] = caption_info[key]
                if transform:
                    segment["transform"] = transform
                
                # 添加样式属性
                style = {}
                for key in ['font_family', 'font_size', 'font_weight', 'font_style', 'color']:
                    if key in caption_info:
                        style[key] = caption_info[key]
                
                # 描边
                if caption_info.get('stroke_enabled'):
                    stroke = {'enabled': True}
                    for key in ['stroke_color', 'stroke_width']:
                        if key in caption_info:
                            stroke[key.replace('stroke_', '')] = caption_info[key]
                    style['stroke'] = stroke
                
                # 阴影
                if caption_info.get('shadow_enabled'):
                    shadow = {'enabled': True}
                    for key in ['shadow_color', 'shadow_offset_x', 'shadow_offset_y', 'shadow_blur']:
                        if key in caption_info:
                            shadow[key.replace('shadow_', '')] = caption_info[key]
                    style['shadow'] = shadow
                
                # 背景
                if caption_info.get('background_enabled'):
                    background = {'enabled': True}
                    for key in ['background_color', 'background_opacity']:
                        if key in caption_info:
                            background[key.replace('background_', '')] = caption_info[key]
                    style['background'] = background
                
                if style:
                    segment["style"] = style
                
                # 对齐
                if 'alignment' in caption_info:
                    segment["alignment"] = caption_info['alignment']
                
                # 动画
                animations = {}
                for key in ['intro_animation', 'outro_animation', 'loop_animation']:
                    if key in caption_info:
                        animations[key.replace('_animation', '')] = caption_info[key]
                if animations:
                    segment["animations"] = animations
                
                segments.append(segment)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析字幕信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddCaptionsResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": f"JSON 解析失败: {str(e)}"},
                    segment_ids=[]
                )
            except ValueError as e:
                logger.error(f"验证字幕信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddCaptionsResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    segment_ids=[]
                )
        
        # 创建文本轨道
        track = {
            "track_type": "text",
            "segments": segments
        }
        
        # 添加轨道到草稿
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(track)
        
        # 更新时间戳
        config["last_modified"] = time.time()
        
        # 保存配置
        success = draft_manager.update_draft_config(request.draft_id, config)
        
        if not success:
            logger.error("保存草稿配置失败")
            return response_manager.error_response(
                AddCaptionsResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "保存草稿配置失败"},
                segment_ids=[]
            )
        
        logger.info(f"成功添加 {len(segment_ids)} 个字幕片段")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddCaptionsResponse,
            message=f"成功添加 {len(segment_ids)} 个字幕片段",
            segment_ids=segment_ids
        )
        
    except Exception as e:
        logger.error(f"批量添加字幕时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddCaptionsResponse,
            error=e,
            segment_ids=[]
        )


@router.post(
    "/add_effects",
    response_model=AddEffectsResponse,
    status_code=status.HTTP_200_OK,
    summary="批量添加特效",
    description="批量添加特效片段到草稿，创建新的特效轨道"
)
async def add_effects(request: AddEffectsRequest) -> AddEffectsResponse:
    """
    批量添加特效片段
    
    与 Coze 插件工具 add_effects 接口保持一致
    每次调用创建一个包含所有指定特效的新轨道
    """
    logger.info("=" * 60)
    logger.info(f"收到批量添加特效请求: draft_id={request.draft_id}")
    logger.info(f"特效数量: {len(request.effect_infos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddEffectsResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_ids=[]
            )
        
        # 解析特效信息并创建片段
        
        segment_ids = []
        segments = []
        
        for i, effect_info_str in enumerate(request.effect_infos):
            try:
                # 解析 JSON 字符串
                effect_info = json.loads(effect_info_str)
                
                # 验证必需字段
                required_fields = ['effect_type', 'start', 'end']
                for field in required_fields:
                    if field not in effect_info:
                        raise ValueError(f"缺少必需字段 '{field}'")
                
                # 创建片段
                segment_id = str(uuid.uuid4())
                segment_ids.append(segment_id)
                
                segment = {
                    "id": segment_id,
                    "type": "effect",
                    "effect_type": effect_info['effect_type'],
                    "time_range": {
                        "start": effect_info['start'],
                        "end": effect_info['end']
                    }
                }
                
                # 添加可选字段
                if 'params' in effect_info:
                    segment["params"] = effect_info['params']
                
                segments.append(segment)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析特效信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddEffectsResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": f"JSON 解析失败: {str(e)}"},
                    segment_ids=[]
                )
            except ValueError as e:
                logger.error(f"验证特效信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddEffectsResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    segment_ids=[]
                )
        
        # 创建特效轨道
        track = {
            "track_type": "effect",
            "segments": segments
        }
        
        # 添加轨道到草稿
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(track)
        
        # 更新时间戳
        config["last_modified"] = time.time()
        
        # 保存配置
        success = draft_manager.update_draft_config(request.draft_id, config)
        
        if not success:
            logger.error("保存草稿配置失败")
            return response_manager.error_response(
                AddEffectsResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "保存草稿配置失败"},
                segment_ids=[]
            )
        
        logger.info(f"成功添加 {len(segment_ids)} 个特效片段")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddEffectsResponse,
            message=f"成功添加 {len(segment_ids)} 个特效片段",
            segment_ids=segment_ids
        )
        
    except Exception as e:
        logger.error(f"批量添加特效时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddEffectsResponse,
            error=e,
            segment_ids=[]
        )


@router.post(
    "/add_images",
    response_model=AddImagesResponse,
    status_code=status.HTTP_200_OK,
    summary="批量添加图片",
    description="批量添加图片片段到草稿，创建新的视频轨道（图片作为静态视频）"
)
async def add_images(request: AddImagesRequest) -> AddImagesResponse:
    """
    批量添加图片片段
    
    与 Coze 插件工具 add_images 接口保持一致
    每次调用创建一个包含所有指定图片的新视频轨道（图片作为静态视频）
    """
    logger.info("=" * 60)
    logger.info(f"收到批量添加图片请求: draft_id={request.draft_id}")
    logger.info(f"图片数量: {len(request.image_infos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddImagesResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_ids=[]
            )
        
        # 解析图片信息并创建片段
        
        segment_ids = []
        segments = []
        
        for i, image_info_str in enumerate(request.image_infos):
            try:
                # 解析 JSON 字符串
                image_info = json.loads(image_info_str)
                
                # 验证必需字段
                required_fields = ['image_url', 'start', 'end']
                for field in required_fields:
                    if field not in image_info:
                        raise ValueError(f"缺少必需字段 '{field}'")
                
                # 创建片段（图片作为视频类型）
                segment_id = str(uuid.uuid4())
                segment_ids.append(segment_id)
                
                segment = {
                    "id": segment_id,
                    "type": "video",  # 图片在 pyJianYingDraft 中作为 VideoSegment 处理
                    "material_url": image_info['image_url'],
                    "time_range": {
                        "start": image_info['start'],
                        "end": image_info['end']
                    }
                }
                
                # 添加变换属性
                transform = {}
                for key in ['position_x', 'position_y', 'scale_x', 'scale_y', 'rotation', 'opacity']:
                    if key in image_info:
                        transform[key] = image_info[key]
                if transform:
                    segment["transform"] = transform
                
                # 添加可选字段
                if 'crop_enabled' in image_info and image_info['crop_enabled']:
                    segment["crop"] = {
                        "enabled": True,
                        "left": image_info.get('crop_left', 0.0),
                        "top": image_info.get('crop_top', 0.0),
                        "right": image_info.get('crop_right', 1.0),
                        "bottom": image_info.get('crop_bottom', 1.0)
                    }
                
                # 特效
                effects = {}
                if 'filter_type' in image_info:
                    effects['filter_type'] = image_info['filter_type']
                    if 'filter_intensity' in image_info:
                        effects['filter_intensity'] = image_info['filter_intensity']
                if 'transition_type' in image_info:
                    effects['transition_type'] = image_info['transition_type']
                    if 'transition_duration' in image_info:
                        effects['transition_duration'] = image_info['transition_duration']
                if effects:
                    segment["effects"] = effects
                
                segments.append(segment)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析图片信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddImagesResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": f"JSON 解析失败: {str(e)}"},
                    segment_ids=[]
                )
            except ValueError as e:
                logger.error(f"验证图片信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddImagesResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    segment_ids=[]
                )
        
        # 创建视频轨道（包含图片）
        track = {
            "track_type": "video",
            "segments": segments
        }
        
        # 添加轨道到草稿
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(track)
        
        # 更新时间戳
        config["last_modified"] = time.time()
        
        # 保存配置
        success = draft_manager.update_draft_config(request.draft_id, config)
        
        if not success:
            logger.error("保存草稿配置失败")
            return response_manager.error_response(
                AddImagesResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "保存草稿配置失败"},
                segment_ids=[]
            )
        
        logger.info(f"成功添加 {len(segment_ids)} 个图片片段")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddImagesResponse,
            message=f"成功添加 {len(segment_ids)} 个图片片段",
            segment_ids=segment_ids
        )
        
    except Exception as e:
        logger.error(f"批量添加图片时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddImagesResponse,
            error=e,
            segment_ids=[]
        )


@router.post(
    "/add_videos",
    response_model=AddVideosResponse,
    status_code=status.HTTP_200_OK,
    summary="批量添加视频",
    description="批量添加视频片段到草稿，创建新的视频轨道"
)
async def add_videos(request: AddVideosRequest) -> AddVideosResponse:
    """
    批量添加视频片段
    
    与 Coze 插件工具 add_videos 接口保持一致
    每次调用创建一个包含所有指定视频的新轨道
    """
    logger.info("=" * 60)
    logger.info(f"收到批量添加视频请求: draft_id={request.draft_id}")
    logger.info(f"视频数量: {len(request.video_infos)}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddVideosResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_ids=[]
            )
        
        # 解析视频信息并创建片段
        
        segment_ids = []
        segments = []
        
        for i, video_info_str in enumerate(request.video_infos):
            try:
                # 解析 JSON 字符串
                video_info = json.loads(video_info_str)
                
                # 验证必需字段
                required_fields = ['video_url', 'start', 'end']
                for field in required_fields:
                    if field not in video_info:
                        raise ValueError(f"缺少必需字段 '{field}'")
                
                # 创建片段
                segment_id = str(uuid.uuid4())
                segment_ids.append(segment_id)
                
                segment = {
                    "id": segment_id,
                    "type": "video",
                    "material_url": video_info['video_url'],
                    "time_range": {
                        "start": video_info['start'],
                        "end": video_info['end']
                    }
                }
                
                # 添加可选字段
                if 'material_start' in video_info and 'material_end' in video_info:
                    segment["material_range"] = {
                        "start": video_info['material_start'],
                        "end": video_info['material_end']
                    }
                
                # 变换属性
                transform = {}
                for key in ['position_x', 'position_y', 'scale_x', 'scale_y', 'rotation', 'opacity']:
                    if key in video_info:
                        transform[key] = video_info[key]
                if transform:
                    segment["transform"] = transform
                
                # 裁剪
                if video_info.get('crop_enabled'):
                    segment["crop"] = {
                        "enabled": True,
                        "left": video_info.get('crop_left', 0.0),
                        "top": video_info.get('crop_top', 0.0),
                        "right": video_info.get('crop_right', 1.0),
                        "bottom": video_info.get('crop_bottom', 1.0)
                    }
                
                # 特效
                effects = {}
                if 'filter_type' in video_info:
                    effects['filter_type'] = video_info['filter_type']
                    if 'filter_intensity' in video_info:
                        effects['filter_intensity'] = video_info['filter_intensity']
                if 'transition_type' in video_info:
                    effects['transition_type'] = video_info['transition_type']
                    if 'transition_duration' in video_info:
                        effects['transition_duration'] = video_info['transition_duration']
                if effects:
                    segment["effects"] = effects
                
                # 速度
                speed = {}
                if 'speed' in video_info:
                    speed['speed'] = video_info['speed']
                if 'reverse' in video_info:
                    speed['reverse'] = video_info['reverse']
                if speed:
                    segment["speed"] = speed
                
                # 背景
                background = {}
                if 'background_blur' in video_info:
                    background['blur'] = video_info['background_blur']
                if 'background_color' in video_info:
                    background['color'] = video_info['background_color']
                if background:
                    segment["background"] = background
                
                segments.append(segment)
                
            except json.JSONDecodeError as e:
                logger.error(f"解析视频信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddVideosResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": f"JSON 解析失败: {str(e)}"},
                    segment_ids=[]
                )
            except ValueError as e:
                logger.error(f"验证视频信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddVideosResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    segment_ids=[]
                )
        
        # 创建视频轨道
        track = {
            "track_type": "video",
            "segments": segments
        }
        
        # 添加轨道到草稿
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(track)
        
        # 更新时间戳
        config["last_modified"] = time.time()
        
        # 保存配置
        success = draft_manager.update_draft_config(request.draft_id, config)
        
        if not success:
            logger.error("保存草稿配置失败")
            return response_manager.error_response(
                AddVideosResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "保存草稿配置失败"},
                segment_ids=[]
            )
        
        logger.info(f"成功添加 {len(segment_ids)} 个视频片段")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddVideosResponse,
            message=f"成功添加 {len(segment_ids)} 个视频片段",
            segment_ids=segment_ids
        )
        
    except Exception as e:
        logger.error(f"批量添加视频时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddVideosResponse,
            error=e,
            segment_ids=[]
        )


@router.post(
    "/add_sticker",
    response_model=AddStickerResponse,
    status_code=status.HTTP_200_OK,
    summary="添加贴纸",
    description="添加贴纸片段到草稿"
)
async def add_sticker(request: AddStickerRequest) -> AddStickerResponse:
    """
    添加贴纸片段
    
    创建贴纸片段并添加到草稿的贴纸轨道
    """
    logger.info("=" * 60)
    logger.info(f"收到添加贴纸请求: draft_id={request.draft_id}")
    
    try:
        # 验证草稿是否存在
        config = draft_manager.get_draft_config(request.draft_id)
        if config is None:
            logger.error(f"草稿不存在: {request.draft_id}")
            return response_manager.not_found_response(
                AddStickerResponse,
                resource_type="draft",
                resource_id=request.draft_id,
                segment_id=""
            )
        
        # 解析贴纸信息
        
        try:
            sticker_info = json.loads(request.sticker_info)
            
            # 验证必需字段
            required_fields = ['sticker_url', 'start', 'end']
            for field in required_fields:
                if field not in sticker_info:
                    raise ValueError(f"缺少必需字段 '{field}'")
            
            # 创建片段
            segment_id = str(uuid.uuid4())
            
            segment = {
                "id": segment_id,
                "type": "sticker",
                "material_url": sticker_info['sticker_url'],
                "time_range": {
                    "start": sticker_info['start'],
                    "end": sticker_info['end']
                }
            }
            
            # 添加变换属性
            transform = {}
            for key in ['position_x', 'position_y', 'scale', 'rotation', 'opacity']:
                if key in sticker_info:
                    transform[key] = sticker_info[key]
            if transform:
                segment["transform"] = transform
            
            # 查找或创建贴纸轨道
            tracks = config.get("tracks", [])
            sticker_track = None
            
            for track in tracks:
                if track["track_type"] == "sticker":
                    sticker_track = track
                    break
            
            if sticker_track is None:
                # 创建新的贴纸轨道
                sticker_track = {
                    "track_type": "sticker",
                    "segments": []
                }
                if "tracks" not in config:
                    config["tracks"] = []
                config["tracks"].append(sticker_track)
            
            # 添加片段到轨道
            sticker_track["segments"].append(segment)
            
            # 更新时间戳
            import time
            config["last_modified"] = time.time()
            
            # 保存配置
            success = draft_manager.update_draft_config(request.draft_id, config)
            
            if not success:
                logger.error("保存草稿配置失败")
                return response_manager.error_response(
                    AddStickerResponse,
                    error_code=ErrorCode.OPERATION_FAILED,
                    details={"reason": "保存草稿配置失败"},
                    segment_id=""
                )
            
            logger.info(f"成功添加贴纸片段: {segment_id}")
            logger.info("=" * 60)
            
            return response_manager.success_response(
                AddStickerResponse,
                message="成功添加贴纸片段",
                segment_id=segment_id
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"解析贴纸信息失败: {e}")
            return response_manager.error_response(
                AddStickerResponse,
                error_code=ErrorCode.INVALID_INPUT,
                details={"reason": f"JSON 解析失败: {str(e)}"},
                segment_id=""
            )
        except ValueError as e:
            logger.error(f"验证贴纸信息失败: {e}")
            return response_manager.error_response(
                AddStickerResponse,
                error_code=ErrorCode.INVALID_INPUT,
                details={"reason": str(e)},
                segment_id=""
            )
        
    except Exception as e:
        logger.error(f"添加贴纸时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddStickerResponse,
            error=e,
            segment_id=""
        )


@router.post(
    "/add_keyframes",
    response_model=AddKeyframesResponse,
    status_code=status.HTTP_200_OK,
    summary="添加关键帧",
    description="向片段添加关键帧"
)
async def add_keyframes(request: AddKeyframesRequest) -> AddKeyframesResponse:
    """
    向片段添加关键帧
    
    支持为视频、文本、贴纸片段添加各种属性的关键帧
    """
    logger.info("=" * 60)
    logger.info(f"收到添加关键帧请求: segment_id={request.segment_id}")
    logger.info(f"关键帧数量: {len(request.keyframe_infos)}")
    
    try:
        # 验证片段是否存在
        segment = segment_manager.get_segment(request.segment_id)
        if not segment:
            logger.error(f"片段不存在: {request.segment_id}")
            return response_manager.not_found_response(
                AddKeyframesResponse,
                resource_type="segment",
                resource_id=request.segment_id,
                keyframe_ids=[]
            )
        
        # 为每个关键帧信息添加操作
        import uuid
        keyframe_ids = []
        
        for i, keyframe_info in enumerate(request.keyframe_infos):
            try:
                # 验证必需字段
                required_fields = ['property', 'time_offset', 'value']
                for field in required_fields:
                    if field not in keyframe_info:
                        raise ValueError(f"关键帧信息 [{i}] 缺少必需字段 '{field}'")
                
                # 记录操作
                operation_data = {
                    "property": keyframe_info['property'],
                    "time_offset": keyframe_info['time_offset'],
                    "value": keyframe_info['value']
                }
                
                success = segment_manager.add_operation(
                    request.segment_id,
                    "add_keyframe",
                    operation_data
                )
                
                if not success:
                    raise Exception(f"添加关键帧 [{i}] 失败")
                
                keyframe_id = str(uuid.uuid4())
                keyframe_ids.append(keyframe_id)
                
            except ValueError as e:
                logger.error(f"验证关键帧信息 [{i}] 失败: {e}")
                return response_manager.error_response(
                    AddKeyframesResponse,
                    error_code=ErrorCode.INVALID_INPUT,
                    details={"index": i, "reason": str(e)},
                    keyframe_ids=[]
                )
        
        logger.info(f"成功添加 {len(keyframe_ids)} 个关键帧")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddKeyframesResponse,
            message=f"成功添加 {len(keyframe_ids)} 个关键帧",
            keyframe_ids=keyframe_ids
        )
        
    except Exception as e:
        logger.error(f"添加关键帧时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddKeyframesResponse,
            error=e,
            keyframe_ids=[]
        )


@router.post(
    "/add_masks",
    response_model=AddMasksResponse,
    status_code=status.HTTP_200_OK,
    summary="添加蒙版",
    description="向视频片段添加蒙版"
)
async def add_masks(request: AddMasksRequest) -> AddMasksResponse:
    """
    向视频片段添加蒙版
    
    支持各种蒙版类型和参数配置
    """
    logger.info("=" * 60)
    logger.info(f"收到添加蒙版请求: segment_id={request.segment_id}")
    
    try:
        # 验证片段是否存在且类型正确
        segment = segment_manager.get_segment(request.segment_id)
        if not segment:
            logger.error(f"片段不存在: {request.segment_id}")
            return response_manager.not_found_response(
                AddMasksResponse,
                resource_type="segment",
                resource_id=request.segment_id,
                mask_id=""
            )
        
        if segment["segment_type"] != "video":
            logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
            return response_manager.error_response(
                AddMasksResponse,
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
                mask_id=""
            )
        
        # 验证必需字段
        if 'mask_type' not in request.mask_info:
            return response_manager.error_response(
                AddMasksResponse,
                error_code=ErrorCode.INVALID_INPUT,
                details={"reason": "缺少必需字段 'mask_type'"},
                mask_id=""
            )
        
        # 记录操作
        operation_data = request.mask_info
        success = segment_manager.add_operation(
            request.segment_id,
            "add_mask",
            operation_data
        )
        
        if not success:
            logger.error("添加蒙版失败")
            return response_manager.error_response(
                AddMasksResponse,
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加蒙版失败"},
                mask_id=""
            )
        
        # 生成蒙版 ID
        import uuid
        mask_id = str(uuid.uuid4())
        
        logger.info(f"成功添加蒙版: {mask_id}")
        logger.info("=" * 60)
        
        return response_manager.success_response(
            AddMasksResponse,
            message="成功添加蒙版",
            mask_id=mask_id
        )
        
    except Exception as e:
        logger.error(f"添加蒙版时发生错误: {e}", exc_info=True)
        return response_manager.internal_error_response(
            AddMasksResponse,
            error=e,
            mask_id=""
        )
