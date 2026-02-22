from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SegmentDetailResponse(BaseModel):
    """片段详情响应"""

    segment_id: str = Field(..., description="Segment UUID")
    segment_type: Optional[str] = Field(None, description="片段类型")
    material_url: Optional[str] = Field(None, description="素材 URL")
    status: str = Field(..., description="状态")
    operations: List[str] = Field(default_factory=list, description="可执行操作列表")
