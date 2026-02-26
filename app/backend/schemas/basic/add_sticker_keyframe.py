from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddStickerKeyframeRequest(BaseModel):
    """添加贴纸关键帧请求（用于 StickerSegment）"""

    time_offset: int = Field(
        ..., description="时间偏移量，单位：微秒（1秒 = 1,000,000微秒）", ge=0
    )
    value: float = Field(..., description="关键帧值")
    property: str = Field(
        ..., description="属性名称: position_x, position_y, scale, rotation, opacity 等"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"time_offset": 2000000, "value": 1.0, "property": "scale"}
        }
    )

class AddStickerKeyframeResponse(BaseModel):
    """添加贴纸关键帧响应"""

    keyframe_id: str = Field(..., description="关键帧 UUID")
