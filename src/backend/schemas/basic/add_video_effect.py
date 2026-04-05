from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddVideoEffectRequest(BaseModel):
    """添加视频特效请求（用于 VideoSegment）"""

    effect_type: str = Field(
        ..., description="视频特效类型: VideoSceneEffectType | VideoCharacterEffectType，格式为枚举成员名称（如 '1998'），或带类前缀（如 'VideoSceneEffectType._1998'）。成员名称与剪映中显示的名称一致"
    )
    params: Optional[List[Optional[float]]] = Field(None, description="特效参数列表（范围 0-100），参数顺序以对应枚举类成员的 annotation 为准，未提供或为 None 的项使用默认值")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effect_type": "VideoSceneEffectType._1998",
                "params": [100.0, 100.0],
            }
        }
    )

class AddVideoEffectResponse(BaseModel):
    """添加视频特效响应"""

    pass
