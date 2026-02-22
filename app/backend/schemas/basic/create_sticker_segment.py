from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.backend.schemas.common_types import ClipSettings, TimeRange

class CreateStickerSegmentRequest(BaseModel):
    """创建贴纸片段请求"""

    material_url: str = Field(..., description="贴纸素材 URL")
    target_timerange: TimeRange = Field(..., description="在轨道上的时间范围")
    clip_settings: Optional[ClipSettings] = Field(
        None, description="图像调节设置（位置、缩放、旋转、透明度）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "material_url": "https://example.com/sticker.png",
                "target_timerange": {"start": 0, "duration": 3000000},
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

class CreateStickerSegmentResponse(BaseModel):
    """创建片段响应"""

    segment_id: str = Field(..., description="Segment UUID")

    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "87654321-4321-4321-4321-cba987654321",
            }
        }
