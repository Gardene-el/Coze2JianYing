from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SegmentInfo(BaseModel):
    """片段信息"""

    segment_id: str = Field(..., description="Segment UUID")
    segment_type: str = Field(..., description="片段类型")
    material_url: Optional[str] = Field(None, description="素材 URL")
    download_status: str = Field(
        ..., description="下载状态: pending/downloading/completed/failed"
    )

class TrackInfo(BaseModel):
    """轨道信息"""

    track_type: str = Field(..., description="轨道类型")
    track_index: int = Field(..., description="轨道索引")
    segment_count: int = Field(..., description="片段数量")

class DownloadStatusInfo(BaseModel):
    """下载状态信息"""

    total: int = Field(..., description="总数量")
    completed: int = Field(..., description="已完成数量")
    pending: int = Field(..., description="待处理数量")
    failed: int = Field(..., description="失败数量")

class DraftStatusResponse(BaseModel):
    """草稿状态响应"""

    draft_id: str = Field(..., description="草稿 UUID")
    draft_name: str = Field(..., description="项目名称")
    tracks: List[TrackInfo] = Field(..., description="轨道列表")
    segments: List[SegmentInfo] = Field(..., description="片段列表")
    download_status: DownloadStatusInfo = Field(..., description="下载状态")
