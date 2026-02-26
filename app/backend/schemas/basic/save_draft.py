from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SaveDraftResponse(BaseModel):
    """保存草稿响应"""

    draft_path: str = Field(..., description="草稿文件夹路径")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "draft_path": "/path/to/draft/folder",
            }
        }
    )
