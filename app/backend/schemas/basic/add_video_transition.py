from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AddVideoTransitionRequest(BaseModel):
    """添加视频转场请求（用于 VideoSegment）"""

    transition_type: str = Field(..., description="转场类型")
    duration: Optional[str] = Field("1s", description="转场时长")

    class Config:
        json_schema_extra = {
            "example": {"transition_type": "TransitionType.XXX", "duration": "1s"}
        }

class AddVideoTransitionResponse(BaseModel):
    """添加视频转场响应"""

    transition_id: str = Field(..., description="转场 UUID")
