from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.backend.core.common_types import TimeRange

class CreateEffectSegmentRequest(BaseModel):
    """创建特效片段请求"""

    effect_type: str = Field(
        ..., description="特效类型（VideoSceneEffectType 或 VideoCharacterEffectType）"
    )
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    params: Optional[List[float]] = Field(
        None, description="特效参数列表（范围 0-100）"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effect_type": "VideoSceneEffectType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "params": [50.0, 75.0],
            }
        }
    )

class CreateEffectSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
    )
