from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CreateDraftRequest(BaseModel):
    """创建草稿请求"""

    width: int = Field(1920, description="视频宽度（像素）", gt=0)
    height: int = Field(1080, description="视频高度（像素）", gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "width": 1920,
                "height": 1080,
            }
        }
    )


class CreateDraftResponse(BaseModel):
    """创建草稿响应"""

    draft_id: str = Field(..., description="草稿 UUID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "draft_id": "12345678-1234-1234-1234-123456789abc",
            }
        }
    )
