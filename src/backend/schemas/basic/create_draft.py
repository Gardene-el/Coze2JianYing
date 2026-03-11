from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CreateDraftRequest(BaseModel):
    """创建草稿请求"""

    draft_name: str = Field("Coze剪映项目", description="项目名称")
    width: int = Field(1920, description="视频宽度（像素）", gt=0)
    height: int = Field(1080, description="视频高度（像素）", gt=0)
    fps: int = Field(30, description="帧率", gt=0, le=120)
    allow_replace: bool = Field(True, description="是否允许替换同名草稿")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "draft_name": "我的视频项目",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "allow_replace": True,
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
