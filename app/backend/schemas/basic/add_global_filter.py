from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.backend.schemas.common_types import TimeRange

class AddGlobalFilterRequest(BaseModel):
    """添加全局滤镜请求"""

    filter_type: str = Field(..., description="滤镜类型")
    target_timerange: TimeRange = Field(..., description="时间范围")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "filter_type": "FilterType.XXX",
                "target_timerange": {"start": 0, "duration": 5000000},
                "intensity": 100.0,
            }
        }

class AddGlobalFilterResponse(BaseModel):
    """添加全局滤镜响应"""

    filter_id: str = Field(..., description="滤镜 UUID")
