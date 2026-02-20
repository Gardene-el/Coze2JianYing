"""
Pydantic Schemas 模块
包含所有 API 请求/响应数据模型定义
"""

from backend.schemas.segment_schemas import *

__all__ = [
    # Segment schemas
    "CreateAudioSegmentRequest",
    "CreateVideoSegmentRequest",
    "CreateTextSegmentRequest",
    "CreateStickerSegmentRequest",
    "CreateSegmentResponse",
    "AddSegmentToDraftRequest",
    "AddSegmentToDraftResponse",
    "CreateDraftRequest",
    "CreateDraftResponse",
    "AddTrackRequest",
    "AddTrackResponse",
    "SaveDraftResponse",
    "DraftStatusResponse",
    "SegmentDetailResponse",
    # Audio segment operation schemas
    "AddAudioEffectRequest",
    "AddAudioEffectResponse",
    "AddAudioFadeRequest",
    "AddAudioFadeResponse",
    "AddAudioKeyframeRequest",
    "AddAudioKeyframeResponse",
    # Video segment operation schemas
    "AddVideoEffectRequest",
    "AddVideoEffectResponse",
    "AddVideoFadeRequest",
    "AddVideoFadeResponse",
    "AddVideoKeyframeRequest",
    "AddVideoKeyframeResponse",
    "AddVideoAnimationRequest",
    "AddVideoAnimationResponse",
    "AddVideoFilterRequest",
    "AddVideoFilterResponse",
    "AddVideoMaskRequest",
    "AddVideoMaskResponse",
    "AddVideoTransitionRequest",
    "AddVideoTransitionResponse",
    "AddVideoBackgroundFillingRequest",
    "AddVideoBackgroundFillingResponse",
    # Text segment operation schemas
    "AddTextAnimationRequest",
    "AddTextAnimationResponse",
    "AddTextBubbleRequest",
    "AddTextBubbleResponse",
    "AddTextEffectRequest",
    "AddTextEffectResponse",
    "AddTextKeyframeRequest",
    "AddTextKeyframeResponse",
    # Sticker segment operation schemas
    "AddStickerKeyframeRequest",
    "AddStickerKeyframeResponse",
    # Draft-level operation schemas
    "AddGlobalEffectRequest",
    "AddGlobalEffectResponse",
    "AddGlobalFilterRequest",
    "AddGlobalFilterResponse",
]
