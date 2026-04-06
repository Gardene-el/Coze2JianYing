from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTrackRequest(BaseModel):
    """添加轨道请求"""

    track_type: str = Field(
        ..., description="轨道类型: audio/video/text/sticker/effect/filter"
    )
    track_name: Optional[str] = Field(None, description="轨道名称")
    mute: bool = Field(False, description="是否静音（仅 audio/video 轨道有效）")
    relative_index: int = Field(0, description="轨道相对层序，数值越大越靠上")
    absolute_index: Optional[int] = Field(None, description="轨道绝对层序，指定后忽略 relative_index")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"track_type": "audio", "track_name": "背景音乐", "mute": False, "relative_index": 0}
        }
    )

class AddTrackResponse(BaseModel):
    """添加轨道响应"""

pass