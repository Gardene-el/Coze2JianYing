from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTextBubbleRequest(BaseModel):
    """添加文本气泡请求（用于 TextSegment）"""

    effect_id: str = Field(..., description="气泡特效 ID")
    resource_id: str = Field(..., description="资源 ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"effect_id": "bubble_effect_123", "resource_id": "resource_456"}
        }
    )

class AddTextBubbleResponse(BaseModel):
    """添加文本气泡响应"""

    bubble_id: str = Field(..., description="气泡 UUID")
