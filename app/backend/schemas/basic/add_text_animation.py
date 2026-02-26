from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTextAnimationRequest(BaseModel):
    """添加文本动画请求（用于 TextSegment）"""

    animation_type: str = Field(..., description="动画类型: TextAnimationType")
    duration: Optional[str] = Field("1s", description="动画时长")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "animation_type": "TextAnimationType.TYPEWRITER",
                "duration": "1s",
            }
        }
    )

class AddTextAnimationResponse(BaseModel):
    """添加文本动画响应"""

    animation_id: str = Field(..., description="动画 UUID")
