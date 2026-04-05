from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoAnimationRequest(BaseModel):
    """添加视频动画请求（用于 VideoSegment）"""

    animation_type: str = Field(
        ..., description="动画类型: IntroType | OutroType | GroupAnimationType，格式为枚举成员名称（如 '渐显'、'渐隐'），或带类前缀（如 'IntroType.渐显'）"
    )
    duration: Optional[str] = Field(None, description="动画时长，省略则使用动画内置时长（字符串如 '1s' 或微秒整数）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"animation_type": "IntroType.渐显", "duration": "1s"}
        }
    )

class AddVideoAnimationResponse(BaseModel):
    """添加视频动画响应"""

    pass
