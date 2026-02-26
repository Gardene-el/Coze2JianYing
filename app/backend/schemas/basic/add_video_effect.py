from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoEffectRequest(BaseModel):
    """添加视频特效请求（用于 VideoSegment）"""

    effect_type: str = Field(
        ..., description="视频特效类型: VideoSceneEffectType | VideoCharacterEffectType"
    )
    params: Optional[List[float]] = Field(None, description="特效参数列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effect_type": "VideoSceneEffectType.GLITCH",
                "params": [50.0],
            }
        }
    )

class AddVideoEffectResponse(BaseModel):
    """添加视频特效响应"""

    effect_id: str = Field(..., description="特效 UUID")
