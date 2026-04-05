from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoFadeRequest(BaseModel):
    """为视频片段添加音频淡入淡出请求（用于 VideoSegment，仅对有音轨的视频片段有效）"""

    in_duration: str = Field(..., description="音频淡入时长（字符串如 '1s' 或微秒整数）")
    out_duration: str = Field(..., description="音频淡出时长（字符串如 '2s' 或微秒整数）")

    model_config = ConfigDict(
        json_schema_extra={"example": {"in_duration": "1s", "out_duration": "0s"}}
    )

class AddVideoFadeResponse(BaseModel):
    """添加视频音频淡入淡出响应"""

    pass
