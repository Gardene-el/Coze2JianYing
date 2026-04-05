from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AddTextAnimationRequest(BaseModel):
    """添加文本动画请求（用于 TextSegment）"""

    animation_type: str = Field(..., description="动画类型: TextIntro | TextOutro | TextLoopAnim，格式为枚举成员名称（如 '打字机'），或带类前缀（如 'TextIntro.打字机'）。注意：若需同时使用入场/出场动画（TextIntro/TextOutro）与循环动画（TextLoopAnim），必须先添加入场/出场动画，再添加循环动画；顺序颠倒会导致循环动画时间范围计算错误")
    duration: Optional[str] = Field(None, description="动画时长，省略则使用动画内置时长（字符串如 '1s' 或微秒整数），循环动画忽略此参数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "animation_type": "TextAnimationType.TYPEWRITER",
                "duration": "1s",
            }
        }
    )

class AddTextAnimationResponse(BaseModel):
    """添加文本动画响应"""

    pass
