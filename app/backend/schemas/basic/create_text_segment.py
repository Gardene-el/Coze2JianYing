from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.backend.core.common_types import (
    ClipSettings,
    TextBackground,
    TextBorder,
    TextShadow,
    TextStyle,
    TimeRange,
)

class CreateTextSegmentRequest(BaseModel):
    """创建文本片段请求"""

    text_content: str = Field(..., description="文本内容", min_length=1)
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    font_family: Optional[str] = Field("文轩体", description="字体名称")
    text_style: Optional[TextStyle] = Field(
        None, description="文本样式（字体大小、颜色、加粗等）"
    )
    text_border: Optional[TextBorder] = Field(None, description="文本描边，None 表示无描边")
    text_shadow: Optional[TextShadow] = Field(None, description="文本阴影，None 表示无阴影")
    text_background: Optional[TextBackground] = Field(None, description="文本背景，None 表示无背景")
    clip_settings: Optional[ClipSettings] = Field(
        None, description="图像调节设置（位置、缩放、旋转、透明度）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text_content": "Hello World",
                "target_timerange": {"start": 0, "duration": 3000000},
                "font_family": "文轩体",
                "text_style": {
                    "font_size": 8.0,
                    "color": [1.0, 1.0, 1.0],
                    "alpha": 1.0,
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "align": 0,
                    "vertical": False,
                    "letter_spacing": 0,
                    "line_spacing": 0,
                    "auto_wrapping": False,
                    "max_line_width": 0.82,
                },
                "text_border": None,
                "text_shadow": None,
                "text_background": None,
                "clip_settings": {
                    "alpha": 1.0,
                    "rotation": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "transform_x": 0.0,
                    "transform_y": 0.0,
                },
            }
        }

class CreateTextSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
