from pydantic import BaseModel, Field, ConfigDict


class SaveDraftRequest(BaseModel):
    """保存草稿请求"""

    draft_id: str = Field(..., description="草稿ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "draft_id": "20260226123456abcd1234",
            }
        }
    )

class SaveDraftResponse(BaseModel):
    """保存草稿响应"""

    pass
