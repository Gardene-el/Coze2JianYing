from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoBackgroundFillingRequest(BaseModel):
    """添加视频背景填充请求（用于 VideoSegment）"""

    fill_type: str = Field(..., description="填充类型: blur（模糊）或 color（纯色），背景填充仅对底层视频轨道上的片段生效")
    blur: float = Field(0.0625, description="模糊程度，范围 0.0-1.0，仅在 fill_type=blur 时有效。剪映四档模糊对应值为 0.0625（低）、0.375（中）、0.75（高）、1.0（最高）")
    color: str = Field(
        "#00000000", description="填充颜色，格式为 '#RRGGBBAA'，仅在 fill_type=color 时有效"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"fill_type": "blur", "blur": 0.0625}}
    )

class AddVideoBackgroundFillingResponse(BaseModel):
    """添加视频背景填充响应"""

    pass
