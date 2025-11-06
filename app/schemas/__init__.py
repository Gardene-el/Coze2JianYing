"""
Pydantic Schemas 模块
包含所有 API 请求/响应数据模型定义
"""
from app.schemas.segment_schemas import *

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
    # All other segment operation schemas
    "AddEffectRequest",
    "AddEffectResponse",
    "AddFadeRequest",
    "AddFadeResponse",
    "AddKeyframeRequest",
    "AddKeyframeResponse",
    "AddAnimationRequest",
    "AddAnimationResponse",
    "AddFilterRequest",
    "AddFilterResponse",
    "AddMaskRequest",
    "AddMaskResponse",
    "AddTransitionRequest",
    "AddTransitionResponse",
    "AddBackgroundFillingRequest",
    "AddBackgroundFillingResponse",
    "AddBubbleRequest",
    "AddBubbleResponse",
    "AddTextEffectRequest",
    "AddTextEffectResponse",
    "AddGlobalEffectRequest",
    "AddGlobalEffectResponse",
    "AddGlobalFilterRequest",
    "AddGlobalFilterResponse",
]
