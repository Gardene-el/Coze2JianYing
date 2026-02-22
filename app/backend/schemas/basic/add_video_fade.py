from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AddVideoFadeRequest(BaseModel):
    """添加视频淡入淡出请求（用于 VideoSegment）"""

    in_duration: str = Field(..., description="淡入时长（字符串如 '1s' 或微秒数）")
    out_duration: str = Field(..., description="淡出时长")

    class Config:
        json_schema_extra = {"example": {"in_duration": "1s", "out_duration": "0s"}}

class AddVideoFadeResponse(BaseModel):
    """添加视频淡入淡出响应"""

    pass
