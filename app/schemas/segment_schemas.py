"""
Segment API 数据模型 (Pydantic Schemas)
定义符合 API_ENDPOINTS_REFERENCE.md 规范的 Segment 创建和操作模型

更新说明：
- 所有响应模型扩展支持 APIResponseManager 字段
- success 字段始终为 True（便于 Coze 插件测试）
- 添加 error_code、category、level 字段用于详细错误信息
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TimeRange(BaseModel):
    """时间范围模型（微秒）"""
    start: int = Field(..., description="开始时间（微秒）", ge=0)
    duration: int = Field(..., description="持续时长（微秒）", gt=0)


class ClipSettings(BaseModel):
    """图像调节设置"""
    brightness: float = Field(0.0, description="亮度 -1.0 到 1.0")
    contrast: float = Field(0.0, description="对比度 -1.0 到 1.0")
    saturation: float = Field(0.0, description="饱和度 -1.0 到 1.0")
    temperature: float = Field(0.0, description="色温 -1.0 到 1.0")
    hue: float = Field(0.0, description="色相 -1.0 到 1.0")


class TextStyle(BaseModel):
    """文本样式"""
    bold: bool = Field(False, description="是否加粗")
    italic: bool = Field(False, description="是否斜体")
    underline: bool = Field(False, description="是否下划线")


class Position(BaseModel):
    """位置信息"""
    x: float = Field(0.0, description="X 坐标")
    y: float = Field(0.0, description="Y 坐标")


# ========== Segment 创建请求模型 ==========

class CreateAudioSegmentRequest(BaseModel):
    """创建音频片段请求"""
    material_url: str = Field(..., description="音频素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    source_timerange: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    speed: float = Field(1.0, description="播放速度", gt=0)
    volume: float = Field(1.0, description="音量 0-2", ge=0, le=2)
    change_pitch: bool = Field(False, description="是否跟随变速改变音调")
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/audio.mp3",
                "target_timerange": {"start": 0, "duration": 5000000},
                "source_timerange": {"start": 0, "duration": 5000000},
                "speed": 1.0,
                "volume": 0.6,
                "change_pitch": False
            }
        }


class CreateVideoSegmentRequest(BaseModel):
    """创建视频片段请求"""
    material_url: str = Field(..., description="视频素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    source_timerange: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    speed: float = Field(1.0, description="播放速度", gt=0)
    volume: float = Field(1.0, description="音量 0-2", ge=0, le=2)
    change_pitch: bool = Field(False, description="是否跟随变速改变音调")
    clip_settings: Optional[ClipSettings] = Field(None, description="图像调节设置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/video.mp4",
                "target_timerange": {"start": 0, "duration": 5000000},
                "source_timerange": {"start": 0, "duration": 5000000},
                "speed": 1.0,
                "volume": 1.0,
                "change_pitch": False,
                "clip_settings": {
                    "brightness": 0.0,
                    "contrast": 0.0,
                    "saturation": 0.0,
                    "temperature": 0.0,
                    "hue": 0.0
                }
            }
        }


class CreateTextSegmentRequest(BaseModel):
    """创建文本片段请求"""
    text_content: str = Field(..., description="文本内容", min_length=1)
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    font_family: Optional[str] = Field("黑体", description="字体名称")
    font_size: Optional[float] = Field(24.0, description="字体大小", gt=0)
    color: Optional[str] = Field("#FFFFFF", description="文字颜色（十六进制）")
    text_style: Optional[TextStyle] = Field(None, description="文本样式")
    position: Optional[Position] = Field(None, description="位置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_content": "Hello World",
                "target_timerange": {"start": 0, "duration": 3000000},
                "font_family": "黑体",
                "font_size": 24.0,
                "color": "#FFFFFF",
                "text_style": {
                    "bold": False,
                    "italic": False,
                    "underline": False
                },
                "position": {
                    "x": 0.0,
                    "y": 0.0
                }
            }
        }


class CreateStickerSegmentRequest(BaseModel):
    """创建贴纸片段请求"""
    material_url: str = Field(..., description="贴纸素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    position: Optional[Position] = Field(None, description="位置")
    scale: Optional[float] = Field(1.0, description="缩放比例", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/sticker.png",
                "target_timerange": {"start": 0, "duration": 3000000},
                "position": {
                    "x": 0.0,
                    "y": 0.0
                },
                "scale": 1.0
            }
        }


class CreateEffectSegmentRequest(BaseModel):
    """创建特效片段请求"""
    effect_type: str = Field(..., description="特效类型（VideoSceneEffectType 或 VideoCharacterEffectType）")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    params: Optional[List[float]] = Field(None, description="特效参数列表（范围 0-100）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "effect_type": "VideoSceneEffectType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "params": [50.0, 75.0]
            }
        }


class CreateFilterSegmentRequest(BaseModel):
    """创建滤镜片段请求"""
    filter_type: str = Field(..., description="滤镜类型（FilterType）")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter_type": "FilterType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "intensity": 100.0
            }
        }


# ========== Segment 创建响应模型 ==========

class CreateSegmentResponse(BaseModel):
    """创建片段响应"""
    segment_id: str = Field(..., description="Segment UUID")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
                "success": True,
                "message": "音频片段创建成功",
                "timestamp": "2025-11-06T10:00:00"
            }
        }


# ========== Segment 操作请求模型 ==========

class AddSegmentToDraftRequest(BaseModel):
    """添加片段到草稿请求"""
    segment_id: str = Field(..., description="Segment UUID")
    track_index: Optional[int] = Field(None, description="目标轨道索引，None 则自动选择")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
                "track_index": 0
            }
        }


class AddSegmentToDraftResponse(BaseModel):
    """添加片段到草稿响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")
    timestamp: datetime = Field(default_factory=datetime.now, description="操作时间")


class AddTrackRequest(BaseModel):
    """添加轨道请求"""
    track_type: str = Field(..., description="轨道类型: audio/video/text/sticker/effect/filter")
    track_name: Optional[str] = Field(None, description="轨道名称")
    
    class Config:
        json_schema_extra = {
            "example": {
                "track_type": "audio",
                "track_name": "背景音乐"
            }
        }


class AddTrackResponse(BaseModel):
    """添加轨道响应"""
    success: bool = Field(..., description="是否成功")
    track_index: int = Field(..., description="轨道索引")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddEffectRequest(BaseModel):
    """添加特效请求（用于 AudioSegment/VideoSegment）"""
    effect_type: str = Field(..., description="特效类型")
    params: Optional[List[float]] = Field(None, description="特效参数列表（范围 0-100）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "effect_type": "AudioSceneEffectType.XXX",
                "params": [50.0, 75.0]
            }
        }


class AddEffectResponse(BaseModel):
    """添加特效响应"""
    success: bool = Field(..., description="是否成功")
    effect_id: str = Field(..., description="特效 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddFadeRequest(BaseModel):
    """添加淡入淡出请求（用于 AudioSegment/VideoSegment）"""
    in_duration: str = Field(..., description="淡入时长（字符串如 '1s' 或微秒数）")
    out_duration: str = Field(..., description="淡出时长")
    
    class Config:
        json_schema_extra = {
            "example": {
                "in_duration": "1s",
                "out_duration": "0s"
            }
        }


class AddFadeResponse(BaseModel):
    """添加淡入淡出响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddKeyframeRequest(BaseModel):
    """添加关键帧请求"""
    time_offset: Any = Field(..., description="时间偏移量（微秒或字符串如 '2s'）")
    value: float = Field(..., description="关键帧值")
    property: Optional[str] = Field(None, description="属性名称（VideoSegment 需要）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "time_offset": "2s",
                "value": 0.8,
                "property": "position_x"
            }
        }


class AddKeyframeResponse(BaseModel):
    """添加关键帧响应"""
    success: bool = Field(..., description="是否成功")
    keyframe_id: str = Field(..., description="关键帧 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddAnimationRequest(BaseModel):
    """添加动画请求（用于 VideoSegment/TextSegment）"""
    animation_type: str = Field(..., description="动画类型")
    duration: Optional[str] = Field("1s", description="动画时长")
    
    class Config:
        json_schema_extra = {
            "example": {
                "animation_type": "IntroType.XXX",
                "duration": "1s"
            }
        }


class AddAnimationResponse(BaseModel):
    """添加动画响应"""
    success: bool = Field(..., description="是否成功")
    animation_id: str = Field(..., description="动画 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddFilterRequest(BaseModel):
    """添加滤镜请求（用于 VideoSegment）"""
    filter_type: str = Field(..., description="滤镜类型")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter_type": "FilterType.XXX",
                "intensity": 100.0
            }
        }


class AddFilterResponse(BaseModel):
    """添加滤镜响应"""
    success: bool = Field(..., description="是否成功")
    filter_id: str = Field(..., description="滤镜 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddMaskRequest(BaseModel):
    """添加蒙版请求（用于 VideoSegment）"""
    mask_type: str = Field(..., description="蒙版类型")
    center_x: Optional[float] = Field(0.0, description="蒙版中心 X 坐标")
    center_y: Optional[float] = Field(0.0, description="蒙版中心 Y 坐标")
    size: Optional[float] = Field(0.5, description="蒙版大小")
    feather: Optional[float] = Field(0.0, description="羽化程度 0-1", ge=0, le=1)
    invert: Optional[bool] = Field(False, description="是否反转")
    rotation: Optional[float] = Field(0.0, description="旋转角度")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mask_type": "MaskType.XXX",
                "center_x": 0.0,
                "center_y": 0.0,
                "size": 0.5,
                "feather": 0.0,
                "invert": False,
                "rotation": 0.0
            }
        }


class AddMaskResponse(BaseModel):
    """添加蒙版响应"""
    success: bool = Field(..., description="是否成功")
    mask_id: str = Field(..., description="蒙版 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddTransitionRequest(BaseModel):
    """添加转场请求（用于 VideoSegment）"""
    transition_type: str = Field(..., description="转场类型")
    duration: Optional[str] = Field("1s", description="转场时长")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transition_type": "TransitionType.XXX",
                "duration": "1s"
            }
        }


class AddTransitionResponse(BaseModel):
    """添加转场响应"""
    success: bool = Field(..., description="是否成功")
    transition_id: str = Field(..., description="转场 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddBackgroundFillingRequest(BaseModel):
    """添加背景填充请求（用于 VideoSegment）"""
    fill_type: str = Field(..., description="填充类型: blur 或 color")
    blur: Optional[float] = Field(0.0625, description="模糊程度（fill_type=blur 时）")
    color: Optional[str] = Field("#00000000", description="填充颜色（fill_type=color 时）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fill_type": "blur",
                "blur": 0.0625
            }
        }


class AddBackgroundFillingResponse(BaseModel):
    """添加背景填充响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddBubbleRequest(BaseModel):
    """添加气泡请求（用于 TextSegment）"""
    effect_id: str = Field(..., description="气泡特效 ID")
    resource_id: str = Field(..., description="资源 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "effect_id": "bubble_effect_123",
                "resource_id": "resource_456"
            }
        }


class AddBubbleResponse(BaseModel):
    """添加气泡响应"""
    success: bool = Field(..., description="是否成功")
    bubble_id: str = Field(..., description="气泡 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddTextEffectRequest(BaseModel):
    """添加花字特效请求（用于 TextSegment）"""
    effect_id: str = Field(..., description="花字特效 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "effect_id": "7296357486490144036"
            }
        }


class AddTextEffectResponse(BaseModel):
    """添加花字特效响应"""
    success: bool = Field(..., description="是否成功")
    effect_id: str = Field(..., description="特效 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


# ========== Draft 级别操作 ==========

class CreateDraftRequest(BaseModel):
    """创建草稿请求"""
    draft_name: str = Field("Coze剪映项目", description="项目名称")
    width: int = Field(1920, description="视频宽度（像素）", gt=0)
    height: int = Field(1080, description="视频高度（像素）", gt=0)
    fps: int = Field(30, description="帧率", gt=0, le=120)
    allow_replace: bool = Field(True, description="是否允许替换同名草稿")
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_name": "我的视频项目",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "allow_replace": True
            }
        }


class CreateDraftResponse(BaseModel):
    """创建草稿响应"""
    draft_id: str = Field(..., description="草稿 UUID")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="创建时间")
    # 可选字段，用于详细错误信息（使用 APIResponseManager 时会填充）
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "12345678-1234-1234-1234-123456789abc",
                "success": True,
                "message": "草稿创建成功",
                "timestamp": "2025-11-06T10:00:00",
                "error_code": "SUCCESS",
                "category": "success",
                "level": "info"
            }
        }


class AddGlobalEffectRequest(BaseModel):
    """添加全局特效请求"""
    effect_type: str = Field(..., description="特效类型")
    target_timerange: TimeRange = Field(..., description="时间范围")
    params: Optional[List[float]] = Field(None, description="特效参数列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "effect_type": "VideoSceneEffectType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "params": [0.5, 1.0]
            }
        }


class AddGlobalEffectResponse(BaseModel):
    """添加全局特效响应"""
    success: bool = Field(..., description="是否成功")
    effect_id: str = Field(..., description="特效 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class AddGlobalFilterRequest(BaseModel):
    """添加全局滤镜请求"""
    filter_type: str = Field(..., description="滤镜类型")
    target_timerange: TimeRange = Field(..., description="时间范围")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter_type": "FilterType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "intensity": 100.0
            }
        }


class AddGlobalFilterResponse(BaseModel):
    """添加全局滤镜响应"""
    success: bool = Field(..., description="是否成功")
    filter_id: str = Field(..., description="滤镜 UUID")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")


class SaveDraftResponse(BaseModel):
    """保存草稿响应"""
    success: bool = Field(..., description="是否成功")
    draft_path: str = Field(..., description="草稿文件夹路径")
    message: str = Field(..., description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "draft_path": "/path/to/draft/folder",
                "message": "草稿保存成功"
            }
        }


# ========== 查询模型 ==========

class SegmentInfo(BaseModel):
    """片段信息"""
    segment_id: str = Field(..., description="Segment UUID")
    segment_type: str = Field(..., description="片段类型")
    material_url: Optional[str] = Field(None, description="素材 URL")
    download_status: str = Field(..., description="下载状态: pending/downloading/completed/failed")


class TrackInfo(BaseModel):
    """轨道信息"""
    track_type: str = Field(..., description="轨道类型")
    track_index: int = Field(..., description="轨道索引")
    segment_count: int = Field(..., description="片段数量")


class DownloadStatusInfo(BaseModel):
    """下载状态信息"""
    total: int = Field(..., description="总数量")
    completed: int = Field(..., description="已完成数量")
    pending: int = Field(..., description="待处理数量")
    failed: int = Field(..., description="失败数量")


class DraftStatusResponse(BaseModel):
    """草稿状态响应"""
    draft_id: str = Field(..., description="草稿 UUID")
    draft_name: str = Field(..., description="项目名称")
    tracks: List[TrackInfo] = Field(..., description="轨道列表")
    segments: List[SegmentInfo] = Field(..., description="片段列表")
    download_status: DownloadStatusInfo = Field(..., description="下载状态")


class SegmentDetailResponse(BaseModel):
    """片段详情响应"""
    segment_id: str = Field(..., description="Segment UUID")
    segment_type: str = Field(..., description="片段类型")
    material_url: Optional[str] = Field(None, description="素材 URL")
    download_status: str = Field(..., description="下载状态")
    local_path: Optional[str] = Field(None, description="本地路径")
    properties: Dict[str, Any] = Field(..., description="片段属性")
    # Response fields
    success: bool = Field(True, description="是否成功")
    message: str = Field("查询成功", description="响应消息")
    # Optional fields from APIResponseManager
    error_code: Optional[str] = Field(None, description="错误代码")
    category: Optional[str] = Field(None, description="错误类别")
    level: Optional[str] = Field(None, description="响应级别")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: Optional[str] = Field(None, description="时间戳")
