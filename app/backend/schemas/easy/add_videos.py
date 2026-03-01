from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AddVideosRequest(BaseModel):
	"""批量添加视频请求参数。"""

	draft_id: str = Field(..., description="草稿ID")
	video_infos: str = Field(..., description="视频信息列表，JSON字符串")
	alpha: float = Field(default=1.0, description="全局透明度[0, 1]")
	scale_x: float = Field(default=1.0, description="X轴缩放比例")
	scale_y: float = Field(default=1.0, description="Y轴缩放比例")
	transform_x: int = Field(default=0, description="X轴位置偏移(像素)")
	transform_y: int = Field(default=0, description="Y轴位置偏移(像素)")


class AddVideosResponse(BaseModel):
	"""添加视频响应参数。"""

	draft_id: str = Field(default="", description="草稿ID")
	track_id: str = Field(default="", description="轨道ID")
	video_ids: List[str] = Field(default_factory=list, description="视频素材ID列表")
	segment_ids: List[str] = Field(default_factory=list, description="片段ID列表")
