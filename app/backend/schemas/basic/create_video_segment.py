from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.backend.schemas.common_types import ClipSettings, CropSettings, TimeRange

class CreateVideoSegmentRequest(BaseModel):
    """创建视频片段请求"""

    material_url: str = Field(..., description="视频素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    source_timerange: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    speed: float = Field(1.0, description="播放速度", gt=0)
    volume: float = Field(1.0, description="音量 0-2", ge=0, le=2)
    change_pitch: bool = Field(False, description="是否跟随变速改变音调")
    clip_settings: Optional[ClipSettings] = Field(None, description="图像调节设置")
    crop_settings: Optional[CropSettings] = Field(None, description="裁剪设置")

    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/video.mp4",
                "target_timerange": {"start": 0, "duration": 5000000},
                "source_timerange": {"start": 1000000, "duration": 5000000},
                "speed": 1.0,
                "volume": 0.8,
                "change_pitch": False,
                "clip_settings": {
                    "alpha": 1.0,
                    "rotation": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "transform_x": 0.0,
                    "transform_y": 0.0,
                },
                "crop_settings": {
                    "upper_left_x": 0.0,
                    "upper_left_y": 0.0,
                    "upper_right_x": 1.0,
                    "upper_right_y": 0.0,
                    "lower_left_x": 0.0,
                    "lower_left_y": 1.0,
                    "lower_right_x": 1.0,
                    "lower_right_y": 1.0,
                },
            }
        }

class CreateVideoSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
