from pydantic import BaseModel, Field, ConfigDict

class AddVideoKeyframeRequest(BaseModel):
    """添加视频关键帧请求（用于 VideoSegment）"""

    time_offset: int = Field(
        ..., description="时间偏移量，单位：微秒（1秒 = 1,000,000微秒）", ge=0
    )
    value: float = Field(..., description="关键帧值，具体范围依属性而定，见 property 说明")
    property: str = Field(
        ...,
        description=(
            "KeyframeProperty 枚举成员名称，可仅写名称（如 'position_x'）或带前缀（如 'KeyframeProperty.position_x'）。"
            "可选属性及值域："
            "position_x（右移为正，单位：剪映显示值/草稿宽度）/ "
            "position_y（上移为正，单位：剪映显示值/草稿高度）/ "
            "rotation（顺时针旋转角度）/ "
            "scale_x（X轴缩放比例，1.0不缩放，与 uniform_scale 互斥）/ "
            "scale_y（Y轴缩放比例，1.0不缩放，与 uniform_scale 互斥）/ "
            "uniform_scale（XY等比缩放，1.0不缩放）/ "
            "alpha（不透明度，1.0完全不透明，仅 VideoSegment 有效）/ "
            "saturation（饱和度，0.0为原始，范围 -1.0~1.0，仅 VideoSegment 有效）/ "
            "contrast（对比度，0.0为原始，范围 -1.0~1.0，仅 VideoSegment 有效）/ "
            "brightness（亮度，0.0为原始，范围 -1.0~1.0，仅 VideoSegment 有效）/ "
            "volume（音量，1.0为原始音量，仅 VideoSegment 和 AudioSegment 有效）"
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"time_offset": 2000000, "value": 0.8, "property": "KeyframeProperty.position_x"}
        }
    )

class AddVideoKeyframeResponse(BaseModel):
    """添加视频关键帧响应"""

    pass
