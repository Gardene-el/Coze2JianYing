from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddAudioEffectRequest(BaseModel):
    """添加音频特效请求（用于 AudioSegment）"""

    effect_type: str = Field(
        ...,
        description="音效类型: AudioSceneEffectType | ToneEffectType | SpeechToSongType",
    )
    params: Optional[List[float]] = Field(
        None, description="特效参数列表（范围 0-100）"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "effect_type": "AudioSceneEffectType.VOICE_CHANGER",
                "params": [50.0, 75.0],
            }
        }
    )

class AddAudioEffectResponse(BaseModel):
    """添加音频特效响应"""

    effect_id: str = Field(..., description="特效 UUID")
