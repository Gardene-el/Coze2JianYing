from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoFilterRequest(BaseModel):
    """添加视频滤镜请求（用于 VideoSegment）"""

    filter_type: str = Field(..., description="滤镜类型")
    intensity: float = Field(100.0, description="滤镜强度 0-100", ge=0, le=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"filter_type": "FilterType.XXX", "intensity": 100.0}
        }
    )

class AddVideoFilterResponse(BaseModel):
    """添加视频滤镜响应"""

    filter_id: str = Field(..., description="滤镜 UUID")
