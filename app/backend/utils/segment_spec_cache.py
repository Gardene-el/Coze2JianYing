from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union

import pyJianYingDraft as draft
from pyJianYingDraft.segment import BaseSegment
from pyJianYingDraft.metadata import (
    AudioSceneEffectType,
    ToneEffectType,
    SpeechToSongType,
    VideoSceneEffectType,
    VideoCharacterEffectType,
    IntroType,
    OutroType,
    GroupAnimationType,
    TextIntro,
    TextOutro,
    TextLoopAnim,
    FilterType,
    TransitionType,
    MaskType,
    FontType,
)
from pyJianYingDraft.keyframe import KeyframeProperty


class SegmentSpec(TypedDict, total=False):
    version: int
    kind: Literal["audio", "video", "sticker", "text", "effect", "filter"]
    payload: Dict[str, Any]
    track_hint: Optional[str]
    tags: List[str]


SEGMENT_SPEC_CACHE: "OrderedDict[str, SegmentSpec]" = OrderedDict()
MAX_CACHE_SIZE = 10000
SPEC_VERSION = 1


MaterialResolver = Callable[[Dict[str, Any]], Union[str, draft.VideoMaterial, draft.AudioMaterial]]


def _timerange_to_dict(timerange: draft.Timerange) -> Dict[str, int]:
    return {"start": timerange.start, "duration": timerange.duration}


def _timerange_from_dict(data: Dict[str, Any]) -> draft.Timerange:
    return draft.Timerange(start=int(data["start"]), duration=int(data["duration"]))


def _clip_to_dict(clip: draft.ClipSettings) -> Dict[str, Any]:
    return {
        "alpha": clip.alpha,
        "flip_horizontal": clip.flip_horizontal,
        "flip_vertical": clip.flip_vertical,
        "rotation": clip.rotation,
        "scale_x": clip.scale_x,
        "scale_y": clip.scale_y,
        "transform_x": clip.transform_x,
        "transform_y": clip.transform_y,
    }


def _clip_from_dict(data: Dict[str, Any]) -> draft.ClipSettings:
    return draft.ClipSettings(
        alpha=float(data.get("alpha", 1.0)),
        flip_horizontal=bool(data.get("flip_horizontal", False)),
        flip_vertical=bool(data.get("flip_vertical", False)),
        rotation=float(data.get("rotation", 0.0)),
        scale_x=float(data.get("scale_x", 1.0)),
        scale_y=float(data.get("scale_y", 1.0)),
        transform_x=float(data.get("transform_x", 0.0)),
        transform_y=float(data.get("transform_y", 0.0)),
    )


def _style_to_dict(style: draft.TextStyle) -> Dict[str, Any]:
    return {
        "size": style.size,
        "bold": style.bold,
        "italic": style.italic,
        "underline": style.underline,
        "color": list(style.color),
        "alpha": style.alpha,
        "align": style.align,
        "vertical": style.vertical,
        "letter_spacing": style.letter_spacing,
        "line_spacing": style.line_spacing,
        "auto_wrapping": style.auto_wrapping,
        "max_line_width": style.max_line_width,
    }


def _style_from_dict(data: Dict[str, Any]) -> draft.TextStyle:
    return draft.TextStyle(
        size=float(data.get("size", 8.0)),
        bold=bool(data.get("bold", False)),
        italic=bool(data.get("italic", False)),
        underline=bool(data.get("underline", False)),
        color=tuple(data.get("color", [1.0, 1.0, 1.0])),
        alpha=float(data.get("alpha", 1.0)),
        align=int(data.get("align", 0)),
        vertical=bool(data.get("vertical", False)),
        letter_spacing=int(data.get("letter_spacing", 0)),
        line_spacing=int(data.get("line_spacing", 0)),
        auto_wrapping=bool(data.get("auto_wrapping", False)),
        max_line_width=float(data.get("max_line_width", 0.82)),
    )


def _border_to_dict(border: Optional[draft.TextBorder]) -> Optional[Dict[str, Any]]:
    if border is None:
        return None
    return {"alpha": border.alpha, "color": list(border.color), "width": border.width * 500.0}


def _border_from_dict(data: Optional[Dict[str, Any]]) -> Optional[draft.TextBorder]:
    if data is None:
        return None
    return draft.TextBorder(alpha=float(data.get("alpha", 1.0)), color=tuple(data.get("color", [0.0, 0.0, 0.0])), width=float(data.get("width", 40.0)))


def _background_to_dict(bg: Optional[draft.TextBackground]) -> Optional[Dict[str, Any]]:
    if bg is None:
        return None
    return {
        "style": bg.style,
        "alpha": bg.alpha,
        "color": bg.color,
        "round_radius": bg.round_radius,
        "height": bg.height,
        "width": bg.width,
        "horizontal_offset": (bg.horizontal_offset + 1) / 2,
        "vertical_offset": (bg.vertical_offset + 1) / 2,
    }


def _background_from_dict(data: Optional[Dict[str, Any]]) -> Optional[draft.TextBackground]:
    if data is None:
        return None
    return draft.TextBackground(
        style=int(data.get("style", 1)),
        alpha=float(data.get("alpha", 1.0)),
        color=str(data.get("color", "#ffffff")),
        round_radius=float(data.get("round_radius", 0.0)),
        height=float(data.get("height", 0.14)),
        width=float(data.get("width", 0.14)),
        horizontal_offset=float(data.get("horizontal_offset", 0.5)),
        vertical_offset=float(data.get("vertical_offset", 0.5)),
    )


def _shadow_to_dict(shadow: Optional[draft.TextShadow]) -> Optional[Dict[str, Any]]:
    if shadow is None:
        return None
    return {
        "alpha": shadow.alpha,
        "color": list(shadow.color),
        "diffuse": shadow.diffuse,
        "distance": shadow.distance,
        "angle": shadow.angle,
    }


def _shadow_from_dict(data: Optional[Dict[str, Any]]) -> Optional[draft.TextShadow]:
    if data is None:
        return None
    return draft.TextShadow(
        alpha=float(data.get("alpha", 1.0)),
        color=tuple(data.get("color", [0.0, 0.0, 0.0])),
        diffuse=float(data.get("diffuse", 15.0)),
        distance=float(data.get("distance", 5.0)),
        angle=float(data.get("angle", -45.0)),
    )


def _enum_name(member: Any) -> str:
    return str(member.name)


def _enum_by_name(enum_cls: Any, name: str) -> Any:
    return enum_cls[name]


def _find_by_effect_id(enum_cls: Any, effect_id: str) -> Any:
    for member in enum_cls:
        if member.value.effect_id == effect_id:
            return member
    raise ValueError(f"No enum member in {enum_cls.__name__} for effect_id={effect_id}")


def _find_by_resource_id(enum_cls: Any, resource_id: str) -> Any:
    for member in enum_cls:
        if member.value.resource_id == resource_id:
            return member
    raise ValueError(f"No enum member in {enum_cls.__name__} for resource_id={resource_id}")


def _encode_params(values: List[float], meta_params: List[Any]) -> List[float]:
    encoded: List[float] = []
    for index, param in enumerate(meta_params):
        if index >= len(values):
            break
        actual = values[index]
        span = float(param.max_value - param.min_value)
        if span == 0:
            encoded.append(0.0)
        else:
            encoded.append(max(0.0, min(100.0, (actual - param.min_value) / span * 100.0)))
    return encoded


def _serialize_keyframes(segment: BaseSegment) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for kf_list in segment.common_keyframes:
        serialized.append(
            {
                "property": kf_list.keyframe_property.name,
                "points": [
                    {"time_offset": kf.time_offset, "value": float(kf.values[0])}
                    for kf in kf_list.keyframes
                ],
            }
        )
    return serialized


def _apply_keyframes(segment: BaseSegment, keyframes: List[Dict[str, Any]]) -> None:
    if not keyframes:
        return

    if isinstance(segment, draft.AudioSegment):
        for entry in keyframes:
            if entry.get("property") != KeyframeProperty.volume.name:
                continue
            for point in entry.get("points", []):
                segment.add_keyframe(int(point["time_offset"]), float(point["value"]))
        return

    if isinstance(segment, (draft.VideoSegment, draft.StickerSegment, draft.TextSegment)):
        for entry in keyframes:
            prop = KeyframeProperty[entry["property"]]
            for point in entry.get("points", []):
                segment.add_keyframe(prop, int(point["time_offset"]), float(point["value"]))


def _default_material_resolver(material_ref: Dict[str, Any]) -> Union[str, draft.VideoMaterial, draft.AudioMaterial]:
    if material_ref.get("type") != "path" or "path" not in material_ref:
        raise ValueError("material_ref must provide a valid local path or a custom resolver")
    return str(material_ref["path"])


def _material_ref_from_segment(segment: Union[draft.AudioSegment, draft.VideoSegment]) -> Dict[str, Any]:
    material = segment.material_instance
    return {
        "type": "path",
        "path": material.path,
        "material_name": material.material_name,
    }


def segment_to_spec(
    segment: BaseSegment,
    *,
    track_hint: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> SegmentSpec:
    payload: Dict[str, Any]

    if isinstance(segment, draft.AudioSegment):
        effects = []
        for effect in segment.effects:
            if effect.category_id == "sound_effect":
                enum_member = _find_by_resource_id(AudioSceneEffectType, effect.resource_id)
            elif effect.category_id == "tone":
                enum_member = _find_by_resource_id(ToneEffectType, effect.resource_id)
            else:
                enum_member = _find_by_resource_id(SpeechToSongType, effect.resource_id)
            raw_values = [p.value for p in effect.audio_adjust_params]
            effects.append({
                "enum_class": enum_member.__class__.__name__,
                "enum_name": _enum_name(enum_member),
                "params": _encode_params(raw_values, enum_member.value.params),
            })

        payload = {
            "material_ref": _material_ref_from_segment(segment),
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "source_timerange": _timerange_to_dict(segment.source_timerange),
            "speed": segment.speed.speed,
            "volume": segment.volume,
            "change_pitch": segment.change_pitch,
            "fade": None if segment.fade is None else {
                "in_duration": segment.fade.in_duration,
                "out_duration": segment.fade.out_duration,
            },
            "effects": effects,
            "keyframes": _serialize_keyframes(segment),
        }
        kind: SegmentSpec["kind"] = "audio"

    elif isinstance(segment, draft.VideoSegment):
        effects = []
        for effect in segment.effects:
            enum_cls = VideoSceneEffectType if effect.effect_type == "video_effect" else VideoCharacterEffectType
            enum_member = _find_by_effect_id(enum_cls, effect.effect_id)
            raw_values = [p.value for p in effect.adjust_params]
            effects.append({
                "enum_class": enum_member.__class__.__name__,
                "enum_name": _enum_name(enum_member),
                "params": _encode_params(raw_values, enum_member.value.params),
            })

        filters = []
        for filter_inst in segment.filters:
            filter_type = _find_by_effect_id(FilterType, filter_inst.effect_meta.effect_id)
            filters.append({
                "filter": _enum_name(filter_type),
                "intensity": filter_inst.intensity * 100.0,
            })

        animations = []
        if segment.animations_instance is not None:
            for anim in segment.animations_instance.animations:
                if anim.animation_type == "in":
                    enum_member = _find_by_effect_id(IntroType, anim.effect_id)
                elif anim.animation_type == "out":
                    enum_member = _find_by_effect_id(OutroType, anim.effect_id)
                else:
                    enum_member = _find_by_effect_id(GroupAnimationType, anim.effect_id)
                animations.append(
                    {
                        "enum_class": enum_member.__class__.__name__,
                        "enum_name": _enum_name(enum_member),
                        "duration": anim.duration,
                    }
                )

        mask_dict = None
        if segment.mask is not None:
            mask_type = _find_by_resource_id(MaskType, segment.mask.mask_meta.resource_id)
            mask_dict = {
                "mask_type": _enum_name(mask_type),
                "center_x": segment.mask.center_x * (segment.material_size[0] / 2),
                "center_y": segment.mask.center_y * (segment.material_size[1] / 2),
                "size": segment.mask.height,
                "rotation": segment.mask.rotation,
                "feather": segment.mask.feather * 100.0,
                "invert": segment.mask.invert,
                "rect_width": segment.mask.width if mask_type.name == "矩形" else None,
                "round_corner": segment.mask.round_corner * 100.0 if mask_type.name == "矩形" else None,
            }

        transition_dict = None
        if segment.transition is not None:
            transition_type = _find_by_effect_id(TransitionType, segment.transition.effect_id)
            transition_dict = {
                "transition": _enum_name(transition_type),
                "duration": segment.transition.duration,
            }

        background = None
        if segment.background_filling is not None:
            background = {
                "fill_type": "blur" if segment.background_filling.fill_type == "canvas_blur" else "color",
                "blur": segment.background_filling.blur,
                "color": segment.background_filling.color,
            }

        payload = {
            "material_ref": _material_ref_from_segment(segment),
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "source_timerange": _timerange_to_dict(segment.source_timerange),
            "speed": segment.speed.speed,
            "volume": segment.volume,
            "change_pitch": segment.change_pitch,
            "clip_settings": _clip_to_dict(segment.clip_settings),
            "effects": effects,
            "filters": filters,
            "animations": animations,
            "mask": mask_dict,
            "transition": transition_dict,
            "background": background,
            "keyframes": _serialize_keyframes(segment),
        }
        kind = "video"

    elif isinstance(segment, draft.StickerSegment):
        animations = []
        if segment.animations_instance is not None:
            for anim in segment.animations_instance.animations:
                if anim.animation_type == "in":
                    enum_member = _find_by_effect_id(IntroType, anim.effect_id)
                elif anim.animation_type == "out":
                    enum_member = _find_by_effect_id(OutroType, anim.effect_id)
                else:
                    enum_member = _find_by_effect_id(GroupAnimationType, anim.effect_id)
                animations.append(
                    {
                        "enum_class": enum_member.__class__.__name__,
                        "enum_name": _enum_name(enum_member),
                        "duration": anim.duration,
                    }
                )

        payload = {
            "resource_id": segment.resource_id,
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "clip_settings": _clip_to_dict(segment.clip_settings),
            "animations": animations,
            "keyframes": _serialize_keyframes(segment),
        }
        kind = "sticker"

    elif isinstance(segment, draft.TextSegment):
        animations = []
        if segment.animations_instance is not None:
            for anim in segment.animations_instance.animations:
                if anim.animation_type == "in":
                    enum_member = _find_by_effect_id(TextIntro, anim.effect_id)
                elif anim.animation_type == "out":
                    enum_member = _find_by_effect_id(TextOutro, anim.effect_id)
                else:
                    enum_member = _find_by_effect_id(TextLoopAnim, anim.effect_id)
                animations.append(
                    {
                        "enum_class": enum_member.__class__.__name__,
                        "enum_name": _enum_name(enum_member),
                        "duration": anim.duration,
                    }
                )

        font_name = None
        if segment.font is not None:
            for font in FontType:
                if font.value.resource_id == segment.font.resource_id:
                    font_name = font.name
                    break

        payload = {
            "text": segment.text,
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "font": font_name,
            "style": _style_to_dict(segment.style),
            "clip_settings": _clip_to_dict(segment.clip_settings),
            "border": _border_to_dict(segment.border),
            "background": _background_to_dict(segment.background),
            "shadow": _shadow_to_dict(segment.shadow),
            "bubble": None if segment.bubble is None else {
                "effect_id": segment.bubble.effect_id,
                "resource_id": segment.bubble.resource_id,
            },
            "effect": None if segment.effect is None else {"effect_id": segment.effect.effect_id},
            "extra_styles": deepcopy(segment.extra_styles),
            "animations": animations,
            "keyframes": _serialize_keyframes(segment),
        }
        kind = "text"

    elif isinstance(segment, draft.EffectSegment):
        effect = segment.effect_inst
        enum_cls = VideoSceneEffectType if effect.effect_type == "video_effect" else VideoCharacterEffectType
        enum_member = _find_by_effect_id(enum_cls, effect.effect_id)
        payload = {
            "effect": _enum_name(enum_member),
            "enum_class": enum_member.__class__.__name__,
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "params": _encode_params([p.value for p in effect.adjust_params], enum_member.value.params),
        }
        kind = "effect"

    elif isinstance(segment, draft.FilterSegment):
        filter_type = _find_by_effect_id(FilterType, segment.material.effect_meta.effect_id)
        payload = {
            "filter": _enum_name(filter_type),
            "target_timerange": _timerange_to_dict(segment.target_timerange),
            "intensity": segment.material.intensity,
        }
        kind = "filter"

    else:
        raise TypeError(f"Unsupported segment type: {type(segment)}")

    spec: SegmentSpec = {
        "version": SPEC_VERSION,
        "kind": kind,
        "payload": payload,
        "track_hint": track_hint,
        "tags": tags or [],
    }
    return spec


def build_segment_from_spec(
    spec: SegmentSpec,
    *,
    material_resolver: Optional[MaterialResolver] = None,
) -> BaseSegment:
    if spec.get("version") != SPEC_VERSION:
        raise ValueError(f"Unsupported spec version: {spec.get('version')}")

    kind = spec["kind"]
    payload = spec["payload"]
    resolver = material_resolver or _default_material_resolver

    segment: BaseSegment

    if kind == "audio":
        material = resolver(payload["material_ref"])
        segment = draft.AudioSegment(
            material,
            _timerange_from_dict(payload["target_timerange"]),
            source_timerange=_timerange_from_dict(payload["source_timerange"]),
            speed=float(payload.get("speed", 1.0)),
            volume=float(payload.get("volume", 1.0)),
            change_pitch=bool(payload.get("change_pitch", False)),
        )

        fade = payload.get("fade")
        if fade:
            segment.add_fade(int(fade["in_duration"]), int(fade["out_duration"]))

        for effect in payload.get("effects", []):
            enum_class_name = effect["enum_class"]
            if enum_class_name == "AudioSceneEffectType":
                enum_member = _enum_by_name(AudioSceneEffectType, effect["enum_name"])
            elif enum_class_name == "ToneEffectType":
                enum_member = _enum_by_name(ToneEffectType, effect["enum_name"])
            else:
                enum_member = _enum_by_name(SpeechToSongType, effect["enum_name"])
            segment.add_effect(enum_member, [float(v) for v in effect.get("params", [])])

        _apply_keyframes(segment, payload.get("keyframes", []))
        return segment

    if kind == "video":
        material = resolver(payload["material_ref"])
        segment = draft.VideoSegment(
            material,
            _timerange_from_dict(payload["target_timerange"]),
            source_timerange=_timerange_from_dict(payload["source_timerange"]),
            speed=float(payload.get("speed", 1.0)),
            volume=float(payload.get("volume", 1.0)),
            change_pitch=bool(payload.get("change_pitch", False)),
            clip_settings=_clip_from_dict(payload.get("clip_settings", {})),
        )

        for effect in payload.get("effects", []):
            enum_class_name = effect["enum_class"]
            if enum_class_name == "VideoSceneEffectType":
                enum_member = _enum_by_name(VideoSceneEffectType, effect["enum_name"])
            else:
                enum_member = _enum_by_name(VideoCharacterEffectType, effect["enum_name"])
            segment.add_effect(enum_member, [float(v) for v in effect.get("params", [])])

        for filter_data in payload.get("filters", []):
            filter_member = _enum_by_name(FilterType, filter_data["filter"])
            segment.add_filter(filter_member, float(filter_data.get("intensity", 100.0)))

        mask_data = payload.get("mask")
        if mask_data:
            segment.add_mask(
                _enum_by_name(MaskType, mask_data["mask_type"]),
                center_x=float(mask_data.get("center_x", 0.0)),
                center_y=float(mask_data.get("center_y", 0.0)),
                size=float(mask_data.get("size", 0.5)),
                rotation=float(mask_data.get("rotation", 0.0)),
                feather=float(mask_data.get("feather", 0.0)),
                invert=bool(mask_data.get("invert", False)),
                rect_width=mask_data.get("rect_width"),
                round_corner=mask_data.get("round_corner"),
            )

        transition_data = payload.get("transition")
        if transition_data:
            segment.add_transition(
                _enum_by_name(TransitionType, transition_data["transition"]),
                duration=int(transition_data["duration"]),
            )

        background_data = payload.get("background")
        if background_data:
            segment.add_background_filling(
                fill_type=str(background_data.get("fill_type", "blur")),
                blur=float(background_data.get("blur", 0.0625)),
                color=str(background_data.get("color", "#00000000")),
            )

        for animation in payload.get("animations", []):
            enum_class_name = animation["enum_class"]
            if enum_class_name == "IntroType":
                enum_member = _enum_by_name(IntroType, animation["enum_name"])
            elif enum_class_name == "OutroType":
                enum_member = _enum_by_name(OutroType, animation["enum_name"])
            else:
                enum_member = _enum_by_name(GroupAnimationType, animation["enum_name"])
            segment.add_animation(enum_member, int(animation["duration"]))

        _apply_keyframes(segment, payload.get("keyframes", []))
        return segment

    if kind == "sticker":
        segment = draft.StickerSegment(
            resource_id=str(payload["resource_id"]),
            target_timerange=_timerange_from_dict(payload["target_timerange"]),
            clip_settings=_clip_from_dict(payload.get("clip_settings", {})),
        )

        for animation in payload.get("animations", []):
            enum_class_name = animation["enum_class"]
            if enum_class_name == "IntroType":
                enum_member = _enum_by_name(IntroType, animation["enum_name"])
            elif enum_class_name == "OutroType":
                enum_member = _enum_by_name(OutroType, animation["enum_name"])
            else:
                enum_member = _enum_by_name(GroupAnimationType, animation["enum_name"])
            segment.add_animation(enum_member, int(animation["duration"]))

        _apply_keyframes(segment, payload.get("keyframes", []))
        return segment

    if kind == "text":
        font_name = payload.get("font")
        font = _enum_by_name(FontType, font_name) if font_name else None
        segment = draft.TextSegment(
            text=str(payload["text"]),
            timerange=_timerange_from_dict(payload["target_timerange"]),
            font=font,
            style=_style_from_dict(payload.get("style", {})),
            clip_settings=_clip_from_dict(payload.get("clip_settings", {})),
            border=_border_from_dict(payload.get("border")),
            background=_background_from_dict(payload.get("background")),
            shadow=_shadow_from_dict(payload.get("shadow")),
        )

        bubble = payload.get("bubble")
        if bubble:
            segment.add_bubble(effect_id=str(bubble["effect_id"]), resource_id=str(bubble["resource_id"]))

        effect = payload.get("effect")
        if effect:
            segment.add_effect(effect_id=str(effect["effect_id"]))

        segment.extra_styles = deepcopy(payload.get("extra_styles", []))

        for animation in payload.get("animations", []):
            enum_class_name = animation["enum_class"]
            if enum_class_name == "TextIntro":
                enum_member = _enum_by_name(TextIntro, animation["enum_name"])
            elif enum_class_name == "TextOutro":
                enum_member = _enum_by_name(TextOutro, animation["enum_name"])
            else:
                enum_member = _enum_by_name(TextLoopAnim, animation["enum_name"])
            segment.add_animation(enum_member, int(animation["duration"]))

        _apply_keyframes(segment, payload.get("keyframes", []))
        return segment

    if kind == "effect":
        enum_class_name = payload["enum_class"]
        if enum_class_name == "VideoSceneEffectType":
            enum_member = _enum_by_name(VideoSceneEffectType, payload["effect"])
        else:
            enum_member = _enum_by_name(VideoCharacterEffectType, payload["effect"])
        segment = draft.EffectSegment(
            effect_type=enum_member,
            target_timerange=_timerange_from_dict(payload["target_timerange"]),
            params=[float(v) for v in payload.get("params", [])],
        )
        return segment

    if kind == "filter":
        segment = draft.FilterSegment(
            meta=_enum_by_name(FilterType, payload["filter"]),
            target_timerange=_timerange_from_dict(payload["target_timerange"]),
            intensity=float(payload.get("intensity", 1.0)),
        )
        return segment

    raise ValueError(f"Unsupported segment kind: {kind}")


def put_segment_spec(key: str, spec: SegmentSpec) -> None:
    if key in SEGMENT_SPEC_CACHE:
        SEGMENT_SPEC_CACHE.pop(key)
    elif len(SEGMENT_SPEC_CACHE) >= MAX_CACHE_SIZE:
        SEGMENT_SPEC_CACHE.popitem(last=False)
    SEGMENT_SPEC_CACHE[key] = deepcopy(spec)


def get_segment_spec(key: str) -> Optional[SegmentSpec]:
    if key not in SEGMENT_SPEC_CACHE:
        return None
    value = SEGMENT_SPEC_CACHE.pop(key)
    SEGMENT_SPEC_CACHE[key] = value
    return deepcopy(value)


def pop_segment_spec(key: str) -> Optional[SegmentSpec]:
    value = SEGMENT_SPEC_CACHE.pop(key, None)
    return deepcopy(value) if value is not None else None


def has_segment_spec(key: str) -> bool:
    return key in SEGMENT_SPEC_CACHE


def clear_segment_spec_cache() -> None:
    SEGMENT_SPEC_CACHE.clear()


def cache_segment(
    key: str,
    segment: BaseSegment,
    *,
    track_hint: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> SegmentSpec:
    spec = segment_to_spec(segment, track_hint=track_hint, tags=tags)
    put_segment_spec(key, spec)
    return spec


def build_segment_from_cache(
    key: str,
    *,
    material_resolver: Optional[MaterialResolver] = None,
) -> Optional[BaseSegment]:
    spec = get_segment_spec(key)
    if spec is None:
        return None
    return build_segment_from_spec(spec, material_resolver=material_resolver)
