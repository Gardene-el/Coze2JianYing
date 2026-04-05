from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddSegmentRequest(BaseModel):
    """添加片段到草稿请求"""

    segment_id: str = Field(..., description="Segment UUID")
    track_name: Optional[str] = Field(
        None, description="目标轨道名称（通过 add_track 创建时指定的名称），同类型轨道只有一条时可省略"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
                "track_name": None,
            }
        }
    )

class AddSegmentResponse(BaseModel):
    """添加片段到草稿响应"""

    pass
