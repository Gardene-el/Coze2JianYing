from __future__ import annotations

from pydantic import BaseModel, Field


class KeyframeItem(BaseModel):
	"""单个关键帧信息。"""

	segment_id: str = Field(..., description="目标片段的唯一标识ID")
	property: str = Field(..., description="动画属性类型")
	offset: float = Field(..., ge=0.0, description="关键帧时间偏移（微秒）")
	value: float = Field(..., description="属性在该时间点的值")


class AddKeyframesRequest(BaseModel):
	"""添加关键帧请求参数。"""

	draft_id: str = Field(..., description="草稿ID")
	keyframes: str = Field(..., description="关键帧信息列表，JSON字符串")


class AddKeyframesResponse(BaseModel):
	"""添加关键帧响应参数。"""

	pass
