"""
segments 包 — 与 pyJianYingDraft 各 Segment 类一一对应的操作模块。

每个模块对应 pyJianYingDraft 中的一个 Segment 类，
暴露与该类方法同名的模块级函数。
额外的 API 适配职责（UUID、持久化、枚举预校验）由各函数内联处理。
"""
from app.backend.services.segments import (  # noqa: F401
    audio_segment,
    video_segment,
    sticker_segment,
    text_segment,
    effect_segment,
    filter_segment,
)
