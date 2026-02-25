from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.backend.core.common_types import TimeRange

class CreateFilterSegmentRequest(BaseModel):
    """创建滤镜片段请求"""

    filter_type: str = Field(..., description="滤镜类型（FilterType）")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "filter_type": "FilterType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "intensity": 100.0,
            }
        }

class CreateFilterSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
