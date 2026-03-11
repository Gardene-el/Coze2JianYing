from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ShadowInfo(BaseModel):
	"""文本阴影参数。"""

	shadow_alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="阴影不透明度")
	shadow_color: str = Field(default="#000000", description="阴影颜色（十六进制）")
	shadow_diffuse: float = Field(default=15.0, ge=0.0, le=100.0, description="阴影扩散程度")
	shadow_distance: float = Field(default=5.0, ge=0.0, le=100.0, description="阴影距离")
	shadow_angle: float = Field(default=-45.0, ge=-180.0, le=180.0, description="阴影角度")


class AddCaptionsRequest(BaseModel):
	"""批量添加字幕请求参数。"""

	captions: str = Field(..., description="字幕信息列表，JSON字符串")
	text_color: str = Field(default="#ffffff", description="文本颜色（十六进制）")
	border_color: Optional[str] = Field(default=None, description="边框颜色（十六进制）")
	alignment: int = Field(default=1, ge=0, le=5, description="文本对齐方式")
	alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="文本透明度")
	font: Optional[str] = Field(default=None, description="字体名称")
	font_size: int = Field(default=15, ge=1, description="字体大小")
	letter_spacing: Optional[float] = Field(default=None, description="字间距")
	line_spacing: Optional[float] = Field(default=None, description="行间距")
	scale_x: float = Field(default=1.0, description="水平缩放")
	scale_y: float = Field(default=1.0, description="垂直缩放")
	transform_x: float = Field(default=0.0, description="水平位移")
	transform_y: float = Field(default=0.0, description="垂直位移")
	style_text: bool = Field(default=False, description="是否使用样式文本")
	underline: bool = Field(default=False, description="文字下划线开关")
	italic: bool = Field(default=False, description="文本斜体开关")
	bold: bool = Field(default=False, description="文本加粗开关")
	has_shadow: bool = Field(default=False, description="是否启用文本阴影")
	shadow_info: Optional[ShadowInfo] = Field(default=None, description="文本阴影参数")


class AddCaptionsResponse(BaseModel):
	"""批量添加字幕响应参数。"""

	segment_ids: List[str] = Field(default_factory=list, description="字幕片段ID列表")
