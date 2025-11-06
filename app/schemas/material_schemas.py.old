"""
素材管理 API 的数据模型 (Pydantic Schemas)
定义添加视频、音频、图片、字幕等素材的请求和响应模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TimeRange(BaseModel):
    """时间范围模型（毫秒）"""
    start: int = Field(..., description="开始时间（毫秒）", ge=0)
    end: int = Field(..., description="结束时间（毫秒）", ge=0)
    
    @validator('end')
    def end_must_be_greater_than_start(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('end must be greater than start')
        return v
    
    @property
    def duration(self) -> int:
        """时长（毫秒）"""
        return self.end - self.start


class FitMode(str, Enum):
    """图片适应模式"""
    FILL = "fill"  # 填充（可能裁剪）
    FIT = "fit"    # 适应（保持比例，可能有黑边）
    STRETCH = "stretch"  # 拉伸（可能变形）


# ========== 视频相关模型 ==========

class VideoSegmentRequest(BaseModel):
    """视频片段请求模型"""
    material_url: str = Field(..., description="视频素材 URL")
    time_range: TimeRange = Field(..., description="时间轴范围")
    material_range: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    
    # 变换参数
    position_x: float = Field(0.0, description="X 轴位置")
    position_y: float = Field(0.0, description="Y 轴位置")
    scale_x: float = Field(1.0, description="X 轴缩放", gt=0)
    scale_y: float = Field(1.0, description="Y 轴缩放", gt=0)
    rotation: float = Field(0.0, description="旋转角度（度）")
    opacity: float = Field(1.0, description="不透明度", ge=0, le=1)
    
    # 播放参数
    speed: float = Field(1.0, description="播放速度", gt=0, le=10)
    volume: float = Field(1.0, description="音量", ge=0, le=2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/video.mp4",
                "time_range": {"start": 0, "end": 5000},
                "material_range": {"start": 0, "end": 5000},
                "position_x": 0.0,
                "position_y": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
                "rotation": 0.0,
                "opacity": 1.0,
                "speed": 1.0,
                "volume": 1.0
            }
        }


class AddVideosRequest(BaseModel):
    """添加视频请求模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    videos: List[VideoSegmentRequest] = Field(..., description="视频片段列表", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "12345678-1234-1234-1234-123456789abc",
                "videos": [
                    {
                        "material_url": "https://example.com/video.mp4",
                        "time_range": {"start": 0, "end": 5000}
                    }
                ]
            }
        }


# ========== 音频相关模型 ==========

class AudioSegmentRequest(BaseModel):
    """音频片段请求模型"""
    material_url: str = Field(..., description="音频素材 URL")
    time_range: TimeRange = Field(..., description="时间轴范围")
    material_range: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    
    # 音频参数
    volume: float = Field(1.0, description="音量", ge=0, le=2)
    fade_in: int = Field(0, description="淡入时长（毫秒）", ge=0)
    fade_out: int = Field(0, description="淡出时长（毫秒）", ge=0)
    speed: float = Field(1.0, description="播放速度", gt=0, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/audio.mp3",
                "time_range": {"start": 0, "end": 5000},
                "volume": 1.0,
                "fade_in": 500,
                "fade_out": 500
            }
        }


class AddAudiosRequest(BaseModel):
    """添加音频请求模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    audios: List[AudioSegmentRequest] = Field(..., description="音频片段列表", min_length=1)


# ========== 图片相关模型 ==========

class ImageSegmentRequest(BaseModel):
    """图片片段请求模型"""
    material_url: str = Field(..., description="图片素材 URL")
    time_range: TimeRange = Field(..., description="时间轴范围")
    
    # 变换参数
    position_x: float = Field(0.0, description="X 轴位置")
    position_y: float = Field(0.0, description="Y 轴位置")
    scale_x: float = Field(1.0, description="X 轴缩放", gt=0)
    scale_y: float = Field(1.0, description="Y 轴缩放", gt=0)
    rotation: float = Field(0.0, description="旋转角度（度）")
    opacity: float = Field(1.0, description="不透明度", ge=0, le=1)
    
    # 图片特有参数
    fit_mode: FitMode = Field(FitMode.FILL, description="适应模式")
    background_color: str = Field("#000000", description="背景颜色（十六进制）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/image.jpg",
                "time_range": {"start": 0, "end": 3000},
                "fit_mode": "fill",
                "background_color": "#000000"
            }
        }


class AddImagesRequest(BaseModel):
    """添加图片请求模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    images: List[ImageSegmentRequest] = Field(..., description="图片片段列表", min_length=1)


# ========== 字幕相关模型 ==========

class CaptionSegmentRequest(BaseModel):
    """字幕片段请求模型"""
    text: str = Field(..., description="字幕文本内容", min_length=1)
    time_range: TimeRange = Field(..., description="时间轴范围")
    
    # 文字样式
    font_family: str = Field("黑体", description="字体名称")
    font_size: float = Field(24.0, description="字体大小", gt=0)
    color: str = Field("#FFFFFF", description="文字颜色（十六进制）")
    
    # 位置参数
    position_x: float = Field(0.0, description="X 轴位置")
    position_y: float = Field(0.0, description="Y 轴位置")
    
    # 样式参数
    bold: bool = Field(False, description="是否加粗")
    italic: bool = Field(False, description="是否斜体")
    underline: bool = Field(False, description="是否下划线")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello World",
                "time_range": {"start": 0, "end": 2000},
                "font_family": "黑体",
                "font_size": 24.0,
                "color": "#FFFFFF"
            }
        }


class AddCaptionsRequest(BaseModel):
    """添加字幕请求模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    captions: List[CaptionSegmentRequest] = Field(..., description="字幕片段列表", min_length=1)


# ========== 通用响应模型 ==========

class DownloadStatus(BaseModel):
    """素材下载状态"""
    total: int = Field(..., description="总数量")
    completed: int = Field(..., description="已完成数量")
    failed: int = Field(..., description="失败数量")
    pending: int = Field(..., description="待处理数量")


class AddMaterialResponse(BaseModel):
    """添加素材响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    segments_added: int = Field(..., description="添加的片段数量")
    download_status: DownloadStatus = Field(..., description="下载状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "成功添加 2 个视频片段",
                "segments_added": 2,
                "download_status": {
                    "total": 2,
                    "completed": 2,
                    "failed": 0,
                    "pending": 0
                },
                "timestamp": "2025-11-05T08:00:00"
            }
        }


# ========== 草稿创建模型 ==========

class CreateDraftRequest(BaseModel):
    """创建草稿请求模型"""
    draft_name: str = Field("Coze剪映项目", description="项目名称")
    width: int = Field(1920, description="视频宽度（像素）", gt=0)
    height: int = Field(1080, description="视频高度（像素）", gt=0)
    fps: int = Field(30, description="帧率", gt=0, le=120)
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_name": "我的视频项目",
                "width": 1920,
                "height": 1080,
                "fps": 30
            }
        }


class CreateDraftResponse(BaseModel):
    """创建草稿响应模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "12345678-1234-1234-1234-123456789abc",
                "success": True,
                "message": "草稿创建成功",
                "timestamp": "2025-11-05T08:00:00"
            }
        }


# ========== 草稿状态查询模型 ==========

class DraftDetailResponse(BaseModel):
    """草稿详情响应模型"""
    draft_id: str = Field(..., description="草稿 UUID")
    project_name: str = Field(..., description="项目名称")
    status: str = Field(..., description="草稿状态")
    
    # 项目设置
    width: int = Field(..., description="视频宽度")
    height: int = Field(..., description="视频高度")
    fps: int = Field(..., description="帧率")
    
    # 统计信息
    tracks_count: int = Field(..., description="轨道数量")
    materials_count: int = Field(..., description="素材数量")
    download_status: DownloadStatus = Field(..., description="下载状态")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    last_modified: datetime = Field(..., description="最后修改时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "12345678-1234-1234-1234-123456789abc",
                "project_name": "我的视频项目",
                "status": "ready",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "tracks_count": 3,
                "materials_count": 5,
                "download_status": {
                    "total": 5,
                    "completed": 5,
                    "failed": 0,
                    "pending": 0
                },
                "created_at": "2025-11-05T08:00:00",
                "last_modified": "2025-11-05T08:05:00"
            }
        }
