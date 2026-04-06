from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class CreateDraftRequest(BaseModel):
    """创建草稿请求"""

    width: int = Field(1920, description="视频宽度（像素）", gt=0)
    height: int = Field(1080, description="视频高度（像素）", gt=0)
    fps: int = Field(30, description="视频帧率", gt=0)
    draft_name: Optional[str] = Field(None, description="草稿名称（剪映中显示的名称），默认使用自动生成的唯一 ID")
    maintrack_adsorb: bool = Field(True, description="是否开启主轨道吸附（无空隙拼接），默认为 True")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "draft_name": "我的草稿",
                "maintrack_adsorb": True,
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
