from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoTransitionRequest(BaseModel):
    """添加视频转场请求（用于 VideoSegment）。注意：转场应添加在前一个片段上，效果发生在该片段与其后一个片段之间"""

    transition_type: str = Field(..., description="转场类型（TransitionType 枚举成员名称，如 '信号故障'），格式可带前缀（如 'TransitionType.信号故障'）")
    duration: Optional[str] = Field(None, description="转场时长，省略则使用转场内置时长（字符串如 '0.5s' 或微秒整数）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"transition_type": "TransitionType.XXX", "duration": "1s"}
        }
    )

class AddVideoTransitionResponse(BaseModel):
    """添加视频转场响应"""

    pass
