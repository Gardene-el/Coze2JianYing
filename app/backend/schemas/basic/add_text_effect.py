from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTextEffectRequest(BaseModel):
    """添加花字特效请求（用于 TextSegment）"""

    effect_id: str = Field(..., description="花字特效 ID")

    model_config = ConfigDict(
        json_schema_extra={"example": {"effect_id": "7296357486490144036"}}
    )

class AddTextEffectResponse(BaseModel):
    """添加花字特效响应"""

    effect_id: str = Field(..., description="特效 UUID")
