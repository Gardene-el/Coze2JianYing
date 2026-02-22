from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AddAudioKeyframeRequest(BaseModel):
    """添加音频关键帧请求（用于 AudioSegment）"""

    time_offset: int = Field(
        ..., description="时间偏移量，单位：微秒（1秒 = 1,000,000微秒）", ge=0
    )
    volume: float = Field(..., description="音量值 0-2")

    class Config:
        json_schema_extra = {"example": {"time_offset": 2000000, "value": 0.8}}

class AddAudioKeyframeResponse(BaseModel):
    """添加音频关键帧响应"""

    keyframe_id: str = Field(..., description="关键帧 UUID")
