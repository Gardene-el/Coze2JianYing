from pydantic import BaseModel, Field, ConfigDict

class AddTextKeyframeRequest(BaseModel):
    """添加文本关键帧请求（用于 TextSegment）"""

    time_offset: int = Field(
        ..., description="时间偏移量，单位：微秒（1秒 = 1,000,000微秒）", ge=0
    )
    value: float = Field(..., description="关键帧值")
    property: str = Field(
        ...,
        description=(
            "KeyframeProperty 枚举成员，格式：KeyframeProperty.<name>，"
            "可选属性："
            "KeyframeProperty.position_x / KeyframeProperty.position_y / "
            "KeyframeProperty.rotation / "
            "KeyframeProperty.scale_x / KeyframeProperty.scale_y / KeyframeProperty.uniform_scale"
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"time_offset": 2000000, "value": 0.5, "property": "KeyframeProperty.position_x"}
        }
    )

class AddTextKeyframeResponse(BaseModel):
    """添加文本关键帧响应"""

    pass
