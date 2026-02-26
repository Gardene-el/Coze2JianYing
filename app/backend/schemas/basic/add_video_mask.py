from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoMaskRequest(BaseModel):
    """添加视频蒙版请求（用于 VideoSegment）"""

    mask_type: str = Field(..., description="蒙版类型（MaskType 枚举名）")
    center_x: Optional[float] = Field(0.0, description="蒙版中心 X 坐标（以素材像素为单位）")
    center_y: Optional[float] = Field(0.0, description="蒙版中心 Y 坐标（以素材像素为单位）")
    size: Optional[float] = Field(0.5, description="蒙版主尺寸（占素材高度比例）")
    feather: Optional[float] = Field(0.0, description="羽化程度 0-100", ge=0, le=100)
    invert: Optional[bool] = Field(False, description="是否反转蒙版")
    rotation: Optional[float] = Field(0.0, description="蒙版顺时针旋转角度")
    rect_width: Optional[float] = Field(
        None, description="矩形蒙版宽度（占素材宽度比例），仅在 mask_type=矩形 时生效"
    )
    round_corner: Optional[float] = Field(
        None, description="矩形蒙版圆角 0-100，仅在 mask_type=矩形 时生效"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mask_type": "线性",
                "center_x": 0.0,
                "center_y": 0.0,
                "size": 0.5,
                "feather": 0.0,
                "invert": False,
                "rotation": 0.0,
                "rect_width": None,
                "round_corner": None,
            }
        }
    )

class AddVideoMaskResponse(BaseModel):
    """添加视频蒙版响应"""

    mask_id: str = Field(..., description="蒙版 UUID")
