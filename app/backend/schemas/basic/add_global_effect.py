from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.backend.schemas.common_types import TimeRange

class AddGlobalEffectRequest(BaseModel):
    """添加全局特效请求"""

    effect_type: str = Field(..., description="特效类型")
    target_timerange: TimeRange = Field(..., description="时间范围")
    params: Optional[List[Optional[float]]] = Field(None, description="特效参数列表")

    class Config:
        json_schema_extra = {
            "example": {
                "effect_type": "VideoSceneEffectType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "params": [0.5, 1.0],
            }
        }

class AddGlobalEffectResponse(BaseModel):
    """添加全局特效响应"""

    effect_id: str = Field(..., description="特效 UUID")
