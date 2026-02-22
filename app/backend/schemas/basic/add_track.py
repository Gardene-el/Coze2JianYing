from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AddTrackRequest(BaseModel):
    """添加轨道请求"""

    track_type: str = Field(
        ..., description="轨道类型: audio/video/text/sticker/effect/filter"
    )
    track_name: Optional[str] = Field(None, description="轨道名称")

    class Config:
        json_schema_extra = {
            "example": {"track_type": "audio", "track_name": "背景音乐"}
        }

class AddTrackResponse(BaseModel):
    """添加轨道响应"""

    track_index: int = Field(..., description="轨道索引")
