from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddAudioEffectRequest(BaseModel):
    """添加音频特效请求（用于 AudioSegment）"""

    effect_type: str = Field(
        ...,
        description="音效类型: AudioSceneEffectType | ToneEffectType | SpeechToSongType，格式为枚举成员名称（如 '8bit'），或带类前缀（如 'AudioSceneEffectType._8bit'）。成员名称与剪映中显示的名称一致",
    )
    params: Optional[List[Optional[float]]] = Field(
        None, description="特效参数列表（范围 0-100），参数顺序以对应枚举类成员的 annotation 为准，未提供或为 None 的项使用默认值"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effect_type": "AudioSceneEffectType._8bit",
                "params": [50.0, 75.0, 80.0],
            }
        }
    )

class AddAudioEffectResponse(BaseModel):
    """添加音频特效响应"""

    pass
