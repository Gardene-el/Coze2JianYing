from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SaveDraftResponse(BaseModel):
    """保存草稿响应"""

    draft_path: str = Field(..., description="草稿文件夹路径")

    class Config:
        json_schema_extra = {
            "example": {
                "draft_path": "/path/to/draft/folder",
            }
        }
