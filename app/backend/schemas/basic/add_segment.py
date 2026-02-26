from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddSegmentRequest(BaseModel):
    """添加片段到草稿请求"""

    segment_id: str = Field(..., description="Segment UUID")
    track_index: Optional[int] = Field(
        None, description="目标轨道索引，None 则自动选择"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
                "track_index": 0,
            }
        }
    )

class AddSegmentResponse(BaseModel):
    """添加片段到草稿响应"""

    pass
