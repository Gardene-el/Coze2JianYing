from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTrackRequest(BaseModel):
    """添加轨道请求"""

    track_type: str = Field(
        ..., description="轨道类型: audio/video/text/sticker/effect/filter"
    )
    track_name: Optional[str] = Field(None, description="轨道名称")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"track_type": "audio", "track_name": "背景音乐"}
        }
    )

class AddTrackResponse(BaseModel):
    """添加轨道响应"""

pass