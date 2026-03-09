from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class EffectItem(BaseModel):
	"""单个特效信息。"""

	effect_title: str = Field(..., description="特效名称/标题")
	start: int = Field(..., description="特效开始时间（微秒）")
	end: int = Field(..., description="特效结束时间（微秒）")


class AddEffectsRequest(BaseModel):
	"""添加特效请求参数。"""

	draft_id: str = Field(..., description="草稿ID")
	effect_infos: str = Field(..., description="特效信息列表，JSON字符串")


class AddEffectsResponse(BaseModel):
	"""添加特效响应参数。"""

	segment_ids: List[str] = Field(default_factory=list, description="特效片段ID列表")
