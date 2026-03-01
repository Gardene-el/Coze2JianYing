from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AddAudiosRequest(BaseModel):
	"""批量添加音频请求参数。"""

	draft_id: str = Field(..., description="草稿ID")
	audio_infos: str = Field(..., description="音频信息列表，JSON字符串")


class AddAudiosResponse(BaseModel):
	"""批量添加音频响应参数。"""

	draft_id: str = Field(default="", description="草稿ID")
	track_id: str = Field(default="", description="音频轨道ID")
	audio_ids: List[str] = Field(default_factory=list, description="音频素材ID列表")
