from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AddVideoBackgroundFillingRequest(BaseModel):
    """添加视频背景填充请求（用于 VideoSegment）"""

    fill_type: str = Field(..., description="填充类型: blur 或 color")
    blur: Optional[float] = Field(0.0625, description="模糊程度（fill_type=blur 时）")
    color: Optional[str] = Field(
        "#00000000", description="填充颜色（fill_type=color 时）"
    )

    class Config:
        json_schema_extra = {"example": {"fill_type": "blur", "blur": 0.0625}}

class AddVideoBackgroundFillingResponse(BaseModel):
    """添加视频背景填充响应"""

    pass
