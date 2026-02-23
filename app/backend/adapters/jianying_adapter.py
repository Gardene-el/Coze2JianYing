"""
JianyingAdapter — 纯函数适配层

将内部 segment_config dict + 本地素材路径转换为 pyJianYingDraft 对象，
以及将记录的操作列表应用到已构造的片段对象上。

无任何 I/O 操作，无状态，可在任意上下文中直接导入使用。
上层调用方通常以别名 `conv` 导入本模块：

    from app.backend.adapters import jianying_adapter as conv
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pyJianYingDraft as draft
from pyJianYingDraft import (
    ClipSettings,
    CropSettings,
    FilterType,
    GroupAnimationType,
    IntroType,
    MaskType,
    OutroType,
    TextBackground,
    TextBorder,
    TextLoopAnim,
    TextOutro,
    TextIntro,
    TextShadow,
    TransitionType,
    VideoCharacterEffectType,
    VideoSceneEffectType,
    tim,
    trange,
)
from pyJianYingDraft.keyframe import KeyframeProperty

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import logger


# ---------------------------------------------------------------------------
# 颜色 / 时间 工具函数
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
    """将 '#RRGGBB'（或 '#RGB'）转换为 (r, g, b) 归一化浮点元组。"""
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (
        int(h[0:2], 16) / 255.0,
        int(h[2:4], 16) / 255.0,
        int(h[4:6], 16) / 255.0,
    )


def microseconds_to_trange(start_us: int, duration_us: int):
    """将微秒整数转换为 pyJianYingDraft Timerange。"""
    return trange(f"{start_us / 1_000_000}s", f"{duration_us / 1_000_000}s")


def microseconds_to_tim(offset_us: int):
    """将微秒整数转换为 pyJianYingDraft tim。"""
    return tim(f"{offset_us / 1_000_000}s")


def resolve_enum(enum_class, name: str, field_label: str = ""):
    """
    从 enum_class 中解析成员名（兼容 'ClassName.成员名' 格式）。
    找不到时抛 ValueError，错误信息中包含建议的合法值。
    """
    clean = name.split(".")[-1] if "." in name else name
    member = getattr(enum_class, clean, None)
    if member is None:
        valid = [m.name for m in enum_class][:50]
        raise CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            f"{field_label or enum_class.__name__} 不存在成员 '{clean}'，"
            f"合法值（前50个）: {valid}"
        )
    return member


def resolve_video_effect_enum(effect_type: str):
    """统一解析视频特效枚举（VideoSceneEffectType / VideoCharacterEffectType）。

    支持格式：
    - 带前缀：'VideoSceneEffectType.XXX' / 'VideoCharacterEffectType.XXX'
    - 无前缀：先精确匹配枚举名，再按 .value.name 模糊匹配

    Raises:
        ValueError: 无法匹配到任何已知特效
    """
    name = effect_type.split(".")[-1] if "." in effect_type else effect_type
    # 1. VideoSceneEffectType 精确匹配
    effect = getattr(VideoSceneEffectType, name, None)
    # 2. VideoCharacterEffectType 精确匹配
    if effect is None:
        effect = getattr(VideoCharacterEffectType, name, None)
    # 3. VideoSceneEffectType .value.name 模糊匹配
    if effect is None:
        for member in VideoSceneEffectType:
            if hasattr(member.value, "name") and member.value.name == name:
                effect = member
                break
    # 4. VideoCharacterEffectType .value.name 模糊匹配
    if effect is None:
        for member in VideoCharacterEffectType:
            if hasattr(member.value, "name") and member.value.name == name:
                effect = member
                break
    if effect is None:
        raise CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            f"未知的视频特效类型: '{effect_type}'。"
            "请使用 VideoSceneEffectType 或 VideoCharacterEffectType 中的成员名。"
        )
    return effect


def decode_timerange(tr: Dict[str, int]) -> tuple:
    """从 dict 解出 (start_us, duration_us)。"""
    return tr.get("start", 0), tr.get("duration", 1_000_000)


def _pick_f(primary: Dict[str, Any], pk: str, fallback: Dict[str, Any], fk: str, default: float) -> float:
    """从 primary[pk] 取值，None 时从 fallback[fk] 取，最终回落 default，返回 float。"""
    v = primary.get(pk)
    return float(v) if v is not None else float(fallback.get(fk) or default)


def _pick_i(primary: Dict[str, Any], pk: str, fallback: Dict[str, Any], fk: str, default: int) -> int:
    """从 primary[pk] 取值，None 时从 fallback[fk] 取，最终回落 default，返回 int。"""
    v = primary.get(pk)
    return int(v) if v is not None else int(fallback.get(fk) or default)


# ---------------------------------------------------------------------------
# ClipSettings / CropSettings 构造
# ---------------------------------------------------------------------------

def build_clip_settings(cfg: Optional[Dict[str, Any]]) -> Optional[ClipSettings]:
    if not cfg:
        return None
    return ClipSettings(
        alpha=cfg.get("alpha", 1.0),
        rotation=cfg.get("rotation", 0.0),
        scale_x=cfg.get("scale_x", 1.0),
        scale_y=cfg.get("scale_y", 1.0),
        transform_x=cfg.get("transform_x", 0.0),
        transform_y=cfg.get("transform_y", 0.0),
        flip_horizontal=cfg.get("flip_horizontal", False),
        flip_vertical=cfg.get("flip_vertical", False),
    )


def build_crop_settings(cfg: Optional[Dict[str, Any]]) -> Optional[CropSettings]:
    if not cfg:
        return None
    return CropSettings(
        upper_left_x=cfg.get("upper_left_x", 0.0),
        upper_left_y=cfg.get("upper_left_y", 0.0),
        upper_right_x=cfg.get("upper_right_x", 1.0),
        upper_right_y=cfg.get("upper_right_y", 0.0),
        lower_left_x=cfg.get("lower_left_x", 0.0),
        lower_left_y=cfg.get("lower_left_y", 1.0),
        lower_right_x=cfg.get("lower_right_x", 1.0),
        lower_right_y=cfg.get("lower_right_y", 1.0),
    )


# ---------------------------------------------------------------------------
# 片段构造函数（接受 config dict + 已解析的本地路径，返回 pyJianYingDraft 对象）
# ---------------------------------------------------------------------------

def build_audio_segment(config: Dict[str, Any], local_path: str):
    """构造 AudioSegment。local_path 由上层服务提前下载好后传入。"""
    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    target_tr = microseconds_to_trange(start_us, duration_us)

    source_tr = None
    src = config.get("source_timerange")
    if src and isinstance(src, dict) and src.get("duration"):
        src_start, src_dur = decode_timerange(src)
        source_tr = microseconds_to_trange(src_start, src_dur)

    return draft.AudioSegment(
        local_path,
        target_tr,
        source_timerange=source_tr,
        speed=config.get("speed"),  # None → 让库从 source_timerange 推导
        volume=config.get("volume", 1.0),
        change_pitch=bool(config.get("change_pitch", False)),
    )


def build_video_segment(config: Dict[str, Any], local_path: str):
    """构造 VideoSegment（含图片）。local_path 由上层服务提前下载好后传入。"""
    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    target_tr = microseconds_to_trange(start_us, duration_us)

    source_tr = None
    src = config.get("source_timerange")
    if src and isinstance(src, dict) and src.get("duration"):
        src_start, src_dur = decode_timerange(src)
        source_tr = microseconds_to_trange(src_start, src_dur)

    clip_settings = build_clip_settings(config.get("clip_settings"))
    crop_settings = build_crop_settings(config.get("crop_settings"))

    kw: Dict[str, Any] = dict(
        source_timerange=source_tr,
        speed=config.get("speed"),  # None → 让库从 source_timerange 推导
        volume=config.get("volume", 1.0),
        change_pitch=bool(config.get("change_pitch", False)),
        clip_settings=clip_settings,
    )

    if crop_settings:
        material = draft.VideoMaterial(local_path, crop_settings=crop_settings)
        return draft.VideoSegment(material, target_tr, **kw)
    else:
        return draft.VideoSegment(local_path, target_tr, **kw)


def build_text_segment(config: Dict[str, Any]):
    """构造 TextSegment（不需要本地路径）。

    config 同时支持两种格式：
    - 扁平格式（旧）：直接含 font_size / bold / color 等键
    - 嵌套格式（新，来自 CreateTextSegmentRequest.dict()）：
      含 text_style / text_border / text_shadow / text_background 子 dict
    两种格式均可正确解析，嵌套格式优先。
    """
    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    tr = microseconds_to_trange(start_us, duration_us)

    text_content = config.get("text_content", "")
    font_family = config.get("font_family") or "文轩体"

    # ---------- 解析 TextStyle ----------
    # 嵌套格式优先：text_style 子 dict
    ts_cfg: Dict[str, Any] = config.get("text_style") or {}

    # 颜色：text_style.color 为 [r,g,b] 列表 或 顶层 text_color / color 十六进制
    color_val = ts_cfg.get("color")
    if color_val and isinstance(color_val, (list, tuple)) and len(color_val) == 3:
        r, g, b = float(color_val[0]), float(color_val[1]), float(color_val[2])
    else:
        raw_color = config.get("text_color") or config.get("color", "#FFFFFF")
        r, g, b = hex_to_rgb(raw_color)

    text_style = draft.TextStyle(
        size=float(ts_cfg.get("font_size") or config.get("font_size") or 8.0),
        bold=bool(ts_cfg.get("bold") or config.get("bold", False)),
        italic=bool(ts_cfg.get("italic") or config.get("italic", False)),
        underline=bool(ts_cfg.get("underline") or config.get("underline", False)),
        color=(r, g, b),
        alpha=_pick_f(ts_cfg, "alpha", config, "alpha", 1.0),
        # 默认与 pyJianYingDraft 一致：0 = 左对齐
        align=_pick_i(ts_cfg, "align", config, "alignment", 0),  # type: ignore[arg-type]
        vertical=bool(ts_cfg.get("vertical") or config.get("vertical", False)),
        letter_spacing=_pick_i(ts_cfg, "letter_spacing", config, "letter_spacing", 0),
        line_spacing=_pick_i(ts_cfg, "line_spacing", config, "line_spacing", 0),
        auto_wrapping=bool(ts_cfg.get("auto_wrapping") or config.get("auto_wrapping", False)),
        max_line_width=_pick_f(ts_cfg, "max_line_width", config, "max_line_width", 0.82),
    )

    # ---------- TextBorder ----------
    border_obj: Optional[TextBorder] = None
    border_cfg: Optional[Dict[str, Any]] = config.get("text_border") or config.get("border")
    if border_cfg and isinstance(border_cfg, dict):
        bc = border_cfg.get("color", "#000000")
        if isinstance(bc, (list, tuple)) and len(bc) == 3:
            br, bg, bb = float(bc[0]), float(bc[1]), float(bc[2])
        elif isinstance(bc, str):
            br, bg, bb = hex_to_rgb(bc)
        else:
            br, bg, bb = 0.0, 0.0, 0.0
        border_obj = TextBorder(
            alpha=float(border_cfg.get("alpha", 1.0)),
            color=(br, bg, bb),
            width=float(border_cfg.get("width", 40.0)),
        )
    elif config.get("border_color"):
        # 向后兼容：仅提供 border_color 十六进制字符串
        br, bg, bb = hex_to_rgb(config["border_color"])
        border_obj = TextBorder(
            alpha=float(config.get("border_alpha", 1.0)),
            color=(br, bg, bb),
            width=float(config.get("border_width", 40.0)),
        )

    # ---------- TextShadow ----------
    shadow_obj: Optional[TextShadow] = None
    shadow_cfg = config.get("text_shadow") or config.get("shadow")
    if shadow_cfg and isinstance(shadow_cfg, dict):
        sc = shadow_cfg.get("color", "#000000")
        if isinstance(sc, (list, tuple)) and len(sc) == 3:
            sr, sg, sb = float(sc[0]), float(sc[1]), float(sc[2])
        elif isinstance(sc, str):
            sr, sg, sb = hex_to_rgb(sc)
        else:
            sr, sg, sb = 0.0, 0.0, 0.0
        shadow_obj = TextShadow(
            alpha=float(shadow_cfg.get("alpha", 0.9)),
            color=(sr, sg, sb),
            diffuse=float(shadow_cfg.get("diffuse", 15.0)),
            distance=float(shadow_cfg.get("distance", 5.0)),
            angle=float(shadow_cfg.get("angle", -45.0)),
        )

    # ---------- TextBackground ----------
    background_obj = None
    bg_cfg = config.get("text_background") or config.get("background")
    if bg_cfg and isinstance(bg_cfg, dict) and bg_cfg.get("color"):
        background_obj = TextBackground(
            color=bg_cfg["color"],
            style=int(bg_cfg.get("style", 1)),  # type: ignore[arg-type]
            alpha=float(bg_cfg.get("alpha", 1.0)),
            round_radius=float(bg_cfg.get("round_radius", 0.0)),
            height=float(bg_cfg.get("height", 0.14)),
            width=float(bg_cfg.get("width", 0.14)),
            horizontal_offset=float(bg_cfg.get("horizontal_offset", 0.5)),
            vertical_offset=float(bg_cfg.get("vertical_offset", 0.5)),
        )

    # ---------- ClipSettings ----------
    # 仅当 caller 明确传入时才构造，避免 always-non-None 副作用
    clip_settings = build_clip_settings(config.get("clip_settings"))

    # ---------- FontType ----------
    try:
        font_type = getattr(draft.FontType, font_family, draft.FontType.文轩体)
    except Exception:
        font_type = draft.FontType.文轩体

    kw: Dict[str, Any] = dict(font=font_type, style=text_style)
    if clip_settings is not None:
        kw["clip_settings"] = clip_settings
    if border_obj is not None:
        kw["border"] = border_obj
    if shadow_obj is not None:
        kw["shadow"] = shadow_obj
    if background_obj is not None:
        kw["background"] = background_obj

    return draft.TextSegment(text_content, tr, **kw)


def build_sticker_segment(config: Dict[str, Any]):
    """构造 StickerSegment（使用 resource_id，不需要下载）。"""
    resource_id = config.get("resource_id", "")
    if not resource_id:
        raise CustomException(CustomError.PARAM_VALIDATION_FAILED, "贴纸片段缺少 resource_id")

    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    tr = microseconds_to_trange(start_us, duration_us)

    clip_settings = build_clip_settings(config.get("clip_settings")) or ClipSettings(
        transform_x=config.get("position_x", 0.0),
        transform_y=config.get("position_y", 0.0),
        scale_x=config.get("scale_x", 1.0),
        scale_y=config.get("scale_y", 1.0),
        rotation=config.get("rotation", 0.0),
        alpha=config.get("opacity", 1.0),
        flip_horizontal=config.get("flip_horizontal", False),
        flip_vertical=config.get("flip_vertical", False),
    )

    return draft.StickerSegment(resource_id, tr, clip_settings=clip_settings)


def build_effect_segment(config: Dict[str, Any]):
    """构造 EffectSegment。"""
    effect_type = config.get("effect_type", "")
    if not effect_type:
        raise CustomException(CustomError.PARAM_VALIDATION_FAILED, "特效片段缺少 effect_type")

    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    tr = microseconds_to_trange(start_us, duration_us)

    effect = resolve_video_effect_enum(effect_type)

    params = config.get("params")
    if params:
        return draft.EffectSegment(effect, tr, params=params)
    return draft.EffectSegment(effect, tr)


def build_filter_segment(config: Dict[str, Any]):
    """构造 FilterSegment。

    注意：intensity 接受 0-100 范围（与 API 层和 VideoSegment.add_filter 一致），
    内部将其直接传给 FilterSegment，FilterSegment 内部不再做缩放。
    """
    filter_type_str = config.get("filter_type", "")
    if not filter_type_str:
        raise CustomException(CustomError.PARAM_VALIDATION_FAILED, "滤镜片段缺少 filter_type")

    filter_enum = resolve_enum(FilterType, filter_type_str, "filter_type")

    start_us, duration_us = decode_timerange(config.get("target_timerange", {}))
    tr = microseconds_to_trange(start_us, duration_us)
    # intensity 统一使用 0-100 范围；FilterSegment 内部不做二次缩放
    intensity = float(config.get("intensity", 100.0))

    return draft.FilterSegment(filter_enum, tr, intensity=intensity)


# ---------------------------------------------------------------------------
# 统一入口：根据 segment_type 分发
# ---------------------------------------------------------------------------

def build_segment(
    segment_type: str,
    config: Dict[str, Any],
    local_path: Optional[str] = None,
):
    """
    根据 segment_type 构造对应的 pyJianYingDraft 片段对象。

    Args:
        segment_type: 'audio' / 'video' / 'image' / 'text' / 'sticker' / 'effect' / 'filter'
        config:       segment_data['config'] 字典
        local_path:   已下载的本地文件路径（audio/video/image 类型必须提供）

    Returns:
        pyJianYingDraft 片段对象

    Raises:
        CustomException: 参数不合法或类型不支持
    """
    if segment_type in ("audio",):
        if not local_path:
            raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"segment_type='{segment_type}' 需要提供 local_path")
        return build_audio_segment(config, local_path)

    elif segment_type in ("video", "image"):
        if not local_path:
            raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"segment_type='{segment_type}' 需要提供 local_path")
        return build_video_segment(config, local_path)

    elif segment_type == "text":
        return build_text_segment(config)

    elif segment_type == "sticker":
        return build_sticker_segment(config)

    elif segment_type == "effect":
        return build_effect_segment(config)

    elif segment_type == "filter":
        return build_filter_segment(config)

    else:
        raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"不支持的片段类型: '{segment_type}'")


# ---------------------------------------------------------------------------
# 操作应用函数（将 operations 列表中的操作应用到已构造的 jy 片段对象）
# ---------------------------------------------------------------------------

def apply_operation(jy_seg, operation_type: str, data: Dict[str, Any]) -> None:
    """将单条操作记录应用到 pyJianYingDraft 片段对象。"""
    from pyJianYingDraft import VideoSegment, TextSegment, AudioSegment

    if operation_type == "add_fade":
        # AudioSegment / VideoSegment 均支持 add_fade
        fade_in = data.get("in_duration", "0s")
        fade_out = data.get("out_duration", "0s")
        jy_seg.add_fade(fade_in, fade_out)

    elif operation_type == "add_animation":
        anim_str = data.get("animation_type", "")
        duration_str = data.get("duration")
        if not duration_str or duration_str == "None":
            duration_str = None

        anim = _resolve_animation(anim_str, jy_seg)
        if anim is None:
            logger.warning("未找到动画类型: %s", anim_str)
            return

        if duration_str:
            jy_seg.add_animation(anim, duration=tim(duration_str))
        else:
            jy_seg.add_animation(anim)

    elif operation_type == "add_transition":
        # BUG-3 修复：正确传递 duration
        raw = data.get("transition_type", "")
        clean = raw.replace("TransitionType.", "")
        trans = resolve_enum(TransitionType, clean, "transition_type")
        duration_str = data.get("duration")
        if hasattr(jy_seg, "add_transition"):
            if duration_str and duration_str != "None":
                jy_seg.add_transition(trans, duration=tim(duration_str))
            else:
                jy_seg.add_transition(trans)

    elif operation_type == "add_background_filling":
        # BUG-4 修复：正确传递 color
        fill_type = data.get("fill_type", "blur")
        blur = float(data.get("blur", 0.0625))
        color = data.get("color", "#00000000")
        if hasattr(jy_seg, "add_background_filling"):
            jy_seg.add_background_filling(fill_type, blur, color)

    elif operation_type == "add_bubble":
        # TextSegment.add_bubble(effect_id, resource_id)
        effect_id = data.get("effect_id", "")
        resource_id = data.get("resource_id", "")
        if hasattr(jy_seg, "add_bubble"):
            jy_seg.add_bubble(effect_id, resource_id)

    elif operation_type == "add_effect":
        # BUG-2 修复：VideoSegment.add_effect 需要枚举；TextSegment.add_effect 需要字符串 effect_id
        if isinstance(jy_seg, TextSegment):
            effect_id = data.get("effect_id", "")
            jy_seg.add_effect(effect_id)
        elif isinstance(jy_seg, VideoSegment):
            effect_type_str = data.get("effect_type") or data.get("effect_id", "")
            params = data.get("params")
            effect_enum = resolve_video_effect_enum(effect_type_str)
            if params is not None:
                jy_seg.add_effect(effect_enum, params)
            else:
                jy_seg.add_effect(effect_enum)
        else:
            logger.warning("add_effect 不支持的片段类型: %s", type(jy_seg).__name__)

    elif operation_type == "add_audio_effect":
        # MISSING-7 修复：AudioSegment.add_effect 通过独立操作类型路由
        from app.backend.services.segments.audio_segment import _resolve_audio_effect_type
        effect_type_str = data.get("effect_type", "")
        params = data.get("params")
        effect_enum = _resolve_audio_effect_type(effect_type_str)
        if params is not None:
            jy_seg.add_effect(effect_enum, params)
        else:
            jy_seg.add_effect(effect_enum)

    elif operation_type == "add_filter":
        filter_str = data.get("filter_type", "")
        intensity = float(data.get("intensity", 100.0))
        filter_enum = resolve_enum(FilterType, filter_str, "filter_type")
        if hasattr(jy_seg, "add_filter"):
            jy_seg.add_filter(filter_enum, intensity)

    elif operation_type == "add_keyframe":
        # BUG-1 修复：AudioSegment.add_keyframe 只控制音量，签名不同
        if isinstance(jy_seg, AudioSegment):
            offset = int(data.get("offset", 0))
            volume = float(data.get("value", 1.0))
            jy_seg.add_keyframe(offset, volume)
        else:
            prop_str = data.get("property", "")
            offset = int(data.get("offset", 0))
            value = float(data.get("value", 0.0))
            try:
                prop_enum = KeyframeProperty(prop_str)
            except ValueError as exc:
                raise CustomException(CustomError.PARAM_VALIDATION_FAILED, f"未知的关键帧属性: '{prop_str}'") from exc
            if hasattr(jy_seg, "add_keyframe"):
                jy_seg.add_keyframe(prop_enum, offset, value)

    elif operation_type == "add_mask":
        mask_name = data.get("mask_type_name", "线性")
        mask_enum = resolve_enum(MaskType, mask_name, "mask_type_name")
        kw: Dict[str, Any] = dict(
            center_x=float(data.get("center_x", 0.0)),
            center_y=float(data.get("center_y", 0.0)),
            size=float(data.get("size", 0.5)),
            rotation=float(data.get("rotation", 0.0)),
            feather=float(data.get("feather", 0.0)),
            invert=bool(data.get("invert", False)),
        )
        if data.get("rect_width") is not None:
            kw["rect_width"] = float(data["rect_width"])
        if data.get("round_corner") is not None:
            kw["round_corner"] = float(data["round_corner"])
        if hasattr(jy_seg, "add_mask"):
            jy_seg.add_mask(mask_enum, **kw)

    else:
        logger.warning("未知操作类型（已忽略）: %s", operation_type)


def apply_all_operations(jy_seg, operations: List[Dict[str, Any]]) -> None:
    """将操作列表逐条应用到片段对象，单条失败时记录警告并继续。"""
    for op in operations:
        op_type = op.get("operation_type", "")
        op_data = op.get("data", {})
        try:
            apply_operation(jy_seg, op_type, op_data)
        except Exception as exc:
            logger.warning("应用操作失败 [%s]: %s", op_type, exc)


# ---------------------------------------------------------------------------
# 动画枚举解析（仅供本模块内部使用）
# ---------------------------------------------------------------------------

def _resolve_animation(anim_str: str, jy_seg):
    """
    解析动画类型字符串。

    支持：
    - 带前缀格式：'IntroType.斜切' / 'TextIntro.xxx'
    - 无前缀格式：按 seg 类型推断候选枚举列表
    """
    from pyJianYingDraft import VideoSegment, TextSegment

    if "." in anim_str:
        prefix, name = anim_str.split(".", 1)
        enum_map = {
            "IntroType": IntroType,
            "OutroType": OutroType,
            "GroupAnimationType": GroupAnimationType,
            "TextIntro": TextIntro,
            "TextOutro": TextOutro,
            "TextLoopAnim": TextLoopAnim,
        }
        ec = enum_map.get(prefix)
        if ec:
            return getattr(ec, name, None)
        return None

    # 无前缀：按 seg 类型推断
    clean = anim_str
    if isinstance(jy_seg, TextSegment):
        candidates = [TextIntro, TextOutro, TextLoopAnim]
    else:
        candidates = [IntroType, OutroType, GroupAnimationType]

    for ec in candidates:
        member = getattr(ec, clean, None)
        if member is not None:
            return member

    return None
