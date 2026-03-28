"""
旧版 Coze 插件脚本兼容层

将 main 分支时代生成的脚本（from app.schemas.segment_schemas import *）
映射到当前新版 src/backend 接口。

脚本中的函数均为 async，接收 *Request 对象；此层将其桥接到
src.backend.services.basic 中同名的 sync 函数（flat 参数）。
"""
from __future__ import annotations

from typing import Optional

# ── 内部别名导入新服务，避免与下方 async wrapper 同名冲突 ──────────────
from src.backend.services.basic.create_draft import create_draft as _create_draft
from src.backend.services.basic.add_track import add_track as _add_track
from src.backend.services.basic.create_audio_segment import create_audio_segment as _create_audio_segment
from src.backend.services.basic.create_video_segment import create_video_segment as _create_video_segment
from src.backend.services.basic.create_text_segment import create_text_segment as _create_text_segment
from src.backend.services.basic.create_sticker_segment import create_sticker_segment as _create_sticker_segment
from src.backend.services.basic.add_segment import add_segment as _add_segment
from src.backend.services.basic.save_draft import save_draft as _save_draft
from src.backend.services.basic.add_audio_effect import add_audio_effect as _add_audio_effect
from src.backend.services.basic.add_audio_fade import add_audio_fade as _add_audio_fade
from src.backend.services.basic.add_audio_keyframe import add_audio_keyframe as _add_audio_keyframe
from src.backend.services.basic.add_video_effect import add_video_effect as _add_video_effect
from src.backend.services.basic.add_video_fade import add_video_fade as _add_video_fade
from src.backend.services.basic.add_video_keyframe import add_video_keyframe as _add_video_keyframe
from src.backend.services.basic.add_video_animation import add_video_animation as _add_video_animation
from src.backend.services.basic.add_video_filter import add_video_filter as _add_video_filter
from src.backend.services.basic.add_video_mask import add_video_mask as _add_video_mask
from src.backend.services.basic.add_video_transition import add_video_transition as _add_video_transition
from src.backend.services.basic.add_video_background_filling import add_video_background_filling as _add_video_background_filling
from src.backend.services.basic.add_text_animation import add_text_animation as _add_text_animation
from src.backend.services.basic.add_text_bubble import add_text_bubble as _add_text_bubble
from src.backend.services.basic.add_text_effect import add_text_effect as _add_text_effect
from src.backend.services.basic.add_text_keyframe import add_text_keyframe as _add_text_keyframe
from src.backend.services.basic.add_sticker_keyframe import add_sticker_keyframe as _add_sticker_keyframe
from src.backend.services.basic.add_effect import add_effect as _add_effect
from src.backend.services.basic.add_filter import add_filter as _add_filter

# ── 导出当前版本的所有 Request/Response 类型供脚本使用 ─────────────────
from src.backend.schemas import *  # noqa: F401, F403
from src.backend.core.common_types import (  # noqa: F401
    TimeRange,
    ClipSettings,
    CropSettings,
    TextStyle,
    TextBorder,
    TextShadow,
    TextBackground,
)

# 旧脚本使用 AddSegmentToDraftRequest，当前仅有 AddSegmentRequest
from src.backend.schemas.basic.add_segment import AddSegmentRequest as AddSegmentToDraftRequest  # noqa: F401

# 旧脚本使用单一的 CreateSegmentResponse，此处提供别名
from src.backend.schemas.basic.create_audio_segment import CreateAudioSegmentResponse as CreateSegmentResponse  # noqa: F401

# ── async wrapper 函数 ────────────────────────────────────────────────

async def create_draft(req: "CreateDraftRequest") -> "CreateDraftResponse":  # type: ignore[name-defined]
    """兼容旧版: create_draft(req) -> CreateDraftResponse"""
    draft_id = _create_draft(req.width, req.height)
    return CreateDraftResponse(draft_id=draft_id)  # type: ignore[name-defined]


async def add_track(draft_id: str, req: "AddTrackRequest") -> "AddTrackResponse":  # type: ignore[name-defined]
    """兼容旧版: add_track(draft_id, req) -> AddTrackResponse"""
    _add_track(
        draft_id,
        req.track_type,
        track_name=req.track_name if req.track_name and req.track_name != "None" else None,
    )
    return AddTrackResponse()  # type: ignore[name-defined]


async def create_audio_segment(req: "CreateAudioSegmentRequest") -> "CreateAudioSegmentResponse":  # type: ignore[name-defined]
    """兼容旧版: create_audio_segment(req) -> CreateAudioSegmentResponse"""
    segment_id = _create_audio_segment(
        material_url=req.material_url,
        target_timerange=req.target_timerange,
        source_timerange=req.source_timerange,
        speed=req.speed,
        volume=req.volume,
        change_pitch=req.change_pitch,
    )
    return CreateAudioSegmentResponse(segment_id=segment_id)  # type: ignore[name-defined]


async def create_video_segment(req: "CreateVideoSegmentRequest") -> "CreateVideoSegmentResponse":  # type: ignore[name-defined]
    """兼容旧版: create_video_segment(req) -> CreateVideoSegmentResponse"""
    segment_id = _create_video_segment(
        material_url=req.material_url,
        target_timerange=req.target_timerange,
        source_timerange=req.source_timerange,
        speed=req.speed,
        volume=req.volume,
        change_pitch=req.change_pitch,
        clip_settings=getattr(req, "clip_settings", None),
        crop_settings=getattr(req, "crop_settings", None),
    )
    return CreateVideoSegmentResponse(segment_id=segment_id)  # type: ignore[name-defined]


async def create_text_segment(req: "CreateTextSegmentRequest") -> "CreateTextSegmentResponse":  # type: ignore[name-defined]
    """兼容旧版: create_text_segment(req) -> CreateTextSegmentResponse"""
    segment_id = _create_text_segment(
        text_content=req.text_content,
        target_timerange=req.target_timerange,
        font_family=getattr(req, "font_family", "文轩体"),
        text_style=getattr(req, "text_style", None),
        text_border=getattr(req, "text_border", None),
        text_shadow=getattr(req, "text_shadow", None),
        text_background=getattr(req, "text_background", None),
        clip_settings=getattr(req, "clip_settings", None),
    )
    return CreateTextSegmentResponse(segment_id=segment_id)  # type: ignore[name-defined]


async def create_sticker_segment(req: "CreateStickerSegmentRequest") -> "CreateStickerSegmentResponse":  # type: ignore[name-defined]
    """兼容旧版: create_sticker_segment(req) -> CreateStickerSegmentResponse"""
    segment_id = _create_sticker_segment(
        material_url=req.material_url,
        target_timerange=req.target_timerange,
        clip_settings=getattr(req, "clip_settings", None),
    )
    return CreateStickerSegmentResponse(segment_id=segment_id)  # type: ignore[name-defined]


async def add_segment(draft_id: str, req: "AddSegmentToDraftRequest") -> None:
    """兼容旧版: add_segment(draft_id, req) -> None
    旧版字段 track_index (int) 在新版中不使用，track_name=None 时自动选轨。
    """
    _add_segment(
        draft_id=draft_id,
        segment_id=req.segment_id,
        track_name=getattr(req, "track_name", None),
    )


async def save_draft(draft_id: str) -> "SaveDraftResponse":  # type: ignore[name-defined]
    """兼容旧版: save_draft(draft_id) -> SaveDraftResponse"""
    _save_draft(draft_id)
    return SaveDraftResponse()  # type: ignore[name-defined]


# ── 其余操作型函数（签名未变，直接映射为 async wrapper） ─────────────

async def add_audio_effect(segment_id: str, req: "AddAudioEffectRequest") -> "AddAudioEffectResponse":  # type: ignore[name-defined]
    _add_audio_effect(segment_id=segment_id, effect_type=req.effect_type, params=getattr(req, "params", None))
    return AddAudioEffectResponse()  # type: ignore[name-defined]


async def add_audio_fade(segment_id: str, req: "AddAudioFadeRequest") -> "AddAudioFadeResponse":  # type: ignore[name-defined]
    _add_audio_fade(segment_id=segment_id, in_duration=req.in_duration, out_duration=req.out_duration)
    return AddAudioFadeResponse()  # type: ignore[name-defined]


async def add_audio_keyframe(segment_id: str, req: "AddAudioKeyframeRequest") -> "AddAudioKeyframeResponse":  # type: ignore[name-defined]
    _add_audio_keyframe(segment_id=segment_id, time_offset=req.time_offset, volume=req.volume)
    return AddAudioKeyframeResponse()  # type: ignore[name-defined]


async def add_video_effect(segment_id: str, req: "AddVideoEffectRequest") -> "AddVideoEffectResponse":  # type: ignore[name-defined]
    _add_video_effect(segment_id=segment_id, effect_type=req.effect_type, params=getattr(req, "params", None))
    return AddVideoEffectResponse()  # type: ignore[name-defined]


async def add_video_fade(segment_id: str, req: "AddVideoFadeRequest") -> "AddVideoFadeResponse":  # type: ignore[name-defined]
    _add_video_fade(segment_id=segment_id, in_duration=req.in_duration, out_duration=req.out_duration)
    return AddVideoFadeResponse()  # type: ignore[name-defined]


async def add_video_keyframe(segment_id: str, req: "AddVideoKeyframeRequest") -> "AddVideoKeyframeResponse":  # type: ignore[name-defined]
    _add_video_keyframe(segment_id=segment_id, time_offset=req.time_offset, value=req.value, property=req.property)
    return AddVideoKeyframeResponse()  # type: ignore[name-defined]


async def add_video_animation(segment_id: str, req: "AddVideoAnimationRequest") -> "AddVideoAnimationResponse":  # type: ignore[name-defined]
    _add_video_animation(segment_id=segment_id, animation_type=req.animation_type, duration=getattr(req, "duration", "1s"))
    return AddVideoAnimationResponse()  # type: ignore[name-defined]


async def add_video_filter(segment_id: str, req: "AddVideoFilterRequest") -> "AddVideoFilterResponse":  # type: ignore[name-defined]
    _add_video_filter(segment_id=segment_id, filter_type=req.filter_type, intensity=getattr(req, "intensity", 100.0))
    return AddVideoFilterResponse()  # type: ignore[name-defined]


async def add_video_mask(segment_id: str, req: "AddVideoMaskRequest") -> "AddVideoMaskResponse":  # type: ignore[name-defined]
    _add_video_mask(
        segment_id=segment_id,
        mask_type=req.mask_type,
        center_x=getattr(req, "center_x", 0.0),
        center_y=getattr(req, "center_y", 0.0),
        size=getattr(req, "size", 0.5),
        feather=getattr(req, "feather", 0.0),
        invert=getattr(req, "invert", False),
        rotation=getattr(req, "rotation", 0.0),
        rect_width=getattr(req, "rect_width", None),
        round_corner=getattr(req, "round_corner", None),
    )
    return AddVideoMaskResponse()  # type: ignore[name-defined]


async def add_video_transition(segment_id: str, req: "AddVideoTransitionRequest") -> "AddVideoTransitionResponse":  # type: ignore[name-defined]
    _add_video_transition(
        segment_id=segment_id,
        transition_type=req.transition_type,
        duration=getattr(req, "duration", "1s"),
    )
    return AddVideoTransitionResponse()  # type: ignore[name-defined]


async def add_video_background_filling(segment_id: str, req: "AddVideoBackgroundFillingRequest") -> "AddVideoBackgroundFillingResponse":  # type: ignore[name-defined]
    _add_video_background_filling(
        segment_id=segment_id,
        fill_type=req.fill_type,
        blur=getattr(req, "blur", 0.0625),
        color=getattr(req, "color", "#00000000"),
    )
    return AddVideoBackgroundFillingResponse()  # type: ignore[name-defined]


async def add_text_animation(segment_id: str, req: "AddTextAnimationRequest") -> "AddTextAnimationResponse":  # type: ignore[name-defined]
    _add_text_animation(segment_id=segment_id, animation_type=req.animation_type, duration=getattr(req, "duration", "1s"))
    return AddTextAnimationResponse()  # type: ignore[name-defined]


async def add_text_bubble(segment_id: str, req: "AddTextBubbleRequest") -> "AddTextBubbleResponse":  # type: ignore[name-defined]
    _add_text_bubble(segment_id=segment_id, effect_id=req.effect_id, resource_id=req.resource_id)
    return AddTextBubbleResponse()  # type: ignore[name-defined]


async def add_text_effect(segment_id: str, req: "AddTextEffectRequest") -> "AddTextEffectResponse":  # type: ignore[name-defined]
    _add_text_effect(segment_id=segment_id, effect_id=req.effect_id)
    return AddTextEffectResponse()  # type: ignore[name-defined]


async def add_text_keyframe(segment_id: str, req: "AddTextKeyframeRequest") -> "AddTextKeyframeResponse":  # type: ignore[name-defined]
    _add_text_keyframe(segment_id=segment_id, time_offset=req.time_offset, value=req.value, property=req.property)
    return AddTextKeyframeResponse()  # type: ignore[name-defined]


async def add_sticker_keyframe(segment_id: str, req: "AddStickerKeyframeRequest") -> "AddStickerKeyframeResponse":  # type: ignore[name-defined]
    _add_sticker_keyframe(segment_id=segment_id, time_offset=req.time_offset, value=req.value, property=req.property)
    return AddStickerKeyframeResponse()  # type: ignore[name-defined]


async def add_effect(draft_id: str, req: "AddEffectRequest") -> "AddEffectResponse":  # type: ignore[name-defined]
    _add_effect(
        draft_id=draft_id,
        effect_type=req.effect_type,
        target_timerange=req.target_timerange,
        params=getattr(req, "params", None),
    )
    return AddEffectResponse()  # type: ignore[name-defined]


async def add_filter(draft_id: str, req: "AddFilterRequest") -> "AddFilterResponse":  # type: ignore[name-defined]
    _add_filter(
        draft_id=draft_id,
        filter_type=req.filter_type,
        target_timerange=req.target_timerange,
        intensity=getattr(req, "intensity", 100.0),
    )
    return AddFilterResponse()  # type: ignore[name-defined]


# 旧版全局特效/滤镜函数名为 add_global_effect / add_global_filter
# Request 类名也不同，提供别名和 wrapper
from src.backend.schemas.basic.add_effect import AddEffectRequest as AddGlobalEffectRequest  # noqa: F401, E402
from src.backend.schemas.basic.add_effect import AddEffectResponse as AddGlobalEffectResponse  # noqa: F401, E402
from src.backend.schemas.basic.add_filter import AddFilterRequest as AddGlobalFilterRequest  # noqa: F401, E402
from src.backend.schemas.basic.add_filter import AddFilterResponse as AddGlobalFilterResponse  # noqa: F401, E402


async def add_global_effect(draft_id: str, req: "AddGlobalEffectRequest") -> "AddGlobalEffectResponse":  # type: ignore[name-defined]
    """兼容旧版函数名 add_global_effect -> add_effect"""
    return await add_effect(draft_id, req)


async def add_global_filter(draft_id: str, req: "AddGlobalFilterRequest") -> "AddGlobalFilterResponse":  # type: ignore[name-defined]
    """兼容旧版函数名 add_global_filter -> add_filter"""
    return await add_filter(draft_id, req)
