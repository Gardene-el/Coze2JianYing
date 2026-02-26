from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.backend.core.common_types import TimeRange

class CreateAudioSegmentRequest(BaseModel):
    """创建音频片段请求"""

    material_url: str = Field(..., description="音频素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    source_timerange: Optional[TimeRange] = Field(None, description="素材裁剪范围")
    speed: float = Field(1.0, description="播放速度", gt=0)
    volume: float = Field(1.0, description="音量 0-2", ge=0, le=2)
    change_pitch: bool = Field(False, description="是否跟随变速改变音调")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "material_url": "https://example.com/audio.mp3",
                "target_timerange": {"start": 0, "duration": 5000000},
                "source_timerange": {"start": 0, "duration": 5000000},
                "speed": 1.0,
                "volume": 0.6,
                "change_pitch": False,
            }
        }
    )

class CreateAudioSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
    )
