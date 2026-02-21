"""
Easy Service — 薄编排层

调用 SegmentManager + DraftStateManager 实现批量片段添加，
不直接调用 pyJianYingDraft（留给 DraftSaver 在 save_draft 时处理）。

流程：
  add_xxs(draft_id, ...)
    ├─ _add_track(draft_id, track_type)          → track_index (int)
    ├─ loop: segment_manager.create_segment(...)  → segment_id (UUID)
    │        [optional] segment_manager.add_operation(...)
    └─ _append_segment(draft_id, seg_id, idx)
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.backend.core.draft_state_manager import get_draft_state_manager
from app.backend.core.segment_manager import get_segment_manager
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# 内部辅助 — 草稿轨道 / 片段操作
# ============================================================

def _parse_json_list(json_str: str, label: str) -> List[Dict]:
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"{label} JSON 解析失败: {e}")
    if not isinstance(data, list):
        raise ValueError(f"{label} 应为 JSON 数组")
    return data


def _get_draft_project(draft_id: str) -> Dict[str, Any]:
    """获取草稿 project 字段，同时验证草稿存在。"""
    config = get_draft_state_manager().get_draft_config(draft_id)
    if config is None:
        raise ValueError(f"draft_id 不存在: {draft_id}")
    return config.get("project", {})


def _add_track(draft_id: str, track_type: str) -> int:
    """向草稿追加一个新轨道，返回 track_index。"""
    mgr = get_draft_state_manager()
    config = mgr.get_draft_config(draft_id)
    if config is None:
        raise ValueError(f"draft_id 不存在: {draft_id}")
    tracks = config.get("tracks", [])
    idx = len(tracks)
    tracks.append({
        "track_type": track_type,
        "track_index": idx,
        "track_name": f"{track_type}_{idx}",
        "segments": [],
    })
    config["tracks"] = tracks
    mgr.update_draft_config(draft_id, config)
    return idx


def _append_segment(draft_id: str, segment_id: str, track_index: int) -> None:
    """将 segment_id 追加到指定轨道。"""
    mgr = get_draft_state_manager()
    config = mgr.get_draft_config(draft_id)
    if config is None:
        raise ValueError(f"draft_id 不存在: {draft_id}")
    config["tracks"][track_index]["segments"].append(segment_id)
    mgr.update_draft_config(draft_id, config)


# ============================================================
# ① add_videos
# ============================================================

def add_videos(
    draft_id: str,
    video_infos_str: str,
    alpha: float = 1.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    transform_x: int = 0,
    transform_y: int = 0,
) -> Tuple[str, List[str], List[str]]:
    """向草稿添加视频，返回 (track_id, video_ids, segment_ids)。"""
    seg_mgr = get_segment_manager()
    project = _get_draft_project(draft_id)
    draft_w = project.get("width", 1920) or 1920
    draft_h = project.get("height", 1080) or 1080

    videos: List[Dict] = _parse_json_list(video_infos_str, "video_infos")
    if not videos:
        raise ValueError("video_infos 为空")

    track_index = _add_track(draft_id, "video")
    segment_ids: List[str] = []

    for v in videos:
        start = int(v["start"])
        end = int(v["end"])
        cfg: Dict[str, Any] = {
            "material_url": v["video_url"],
            "target_timerange": {"start": start, "duration": end - start},
            "volume": float(v.get("volume", 1.0)),
            "clip_settings": {
                "alpha": alpha,
                "scale_x": scale_x,
                "scale_y": scale_y,
                "transform_x": transform_x / draft_w,
                "transform_y": transform_y / draft_h,
            },
        }
        result = seg_mgr.create_segment("video", cfg)
        if not result["success"]:
            raise ValueError(f"创建视频片段失败: {result['message']}")
        seg_id = result["segment_id"]

        if v.get("transition"):
            seg_mgr.add_operation(seg_id, "add_transition", {
                "transition_type": v["transition"],
                "duration": int(v.get("transition_duration", 500_000)),
            })

        _append_segment(draft_id, seg_id, track_index)
        segment_ids.append(seg_id)

    logger.info(f"add_videos 完成: track={track_index}, segments={len(segment_ids)}")
    return str(track_index), segment_ids, segment_ids


# ============================================================
# ② add_audios
# ============================================================

def add_audios(draft_id: str, audio_infos_str: str) -> Tuple[str, List[str]]:
    """向草稿添加音频，返回 (track_id, audio_ids)。"""
    seg_mgr = get_segment_manager()
    _get_draft_project(draft_id)  # 验证存在性

    audios: List[Dict] = _parse_json_list(audio_infos_str, "audio_infos")
    if not audios:
        raise ValueError("audio_infos 为空")

    track_index = _add_track(draft_id, "audio")
    audio_ids: List[str] = []

    for a in audios:
        start = int(a["start"])
        end = int(a["end"])
        cfg: Dict[str, Any] = {
            "material_url": a["audio_url"],
            "target_timerange": {"start": start, "duration": end - start},
            "volume": float(a.get("volume", 1.0)),
        }
        result = seg_mgr.create_segment("audio", cfg)
        if not result["success"]:
            raise ValueError(f"创建音频片段失败: {result['message']}")
        seg_id = result["segment_id"]
        _append_segment(draft_id, seg_id, track_index)
        audio_ids.append(seg_id)

    logger.info(f"add_audios 完成: track={track_index}, audios={len(audio_ids)}")
    return str(track_index), audio_ids


# ============================================================
# ③ add_images
# ============================================================

def add_images(
    draft_id: str,
    image_infos_str: str,
    alpha: float = 1.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    transform_x: int = 0,
    transform_y: int = 0,
) -> Tuple[str, List[str], List[str], List[Dict]]:
    """向草稿添加图片，返回 (track_id, image_ids, segment_ids, segment_infos)。"""
    seg_mgr = get_segment_manager()
    project = _get_draft_project(draft_id)
    draft_w = project.get("width", 1920) or 1920
    draft_h = project.get("height", 1080) or 1080

    images: List[Dict] = _parse_json_list(image_infos_str, "image_infos")
    if not images:
        raise ValueError("image_infos 为空")

    track_index = _add_track(draft_id, "video")  # JY 图片和视频共用 video track
    segment_ids: List[str] = []
    segment_infos: List[Dict] = []

    for img in images:
        start = int(img["start"])
        end = int(img["end"])
        cfg: Dict[str, Any] = {
            "material_url": img["image_url"],
            "target_timerange": {"start": start, "duration": end - start},
            "clip_settings": {
                "alpha": alpha,
                "scale_x": scale_x,
                "scale_y": scale_y,
                "transform_x": transform_x / draft_w,
                "transform_y": transform_y / draft_h,
            },
        }
        result = seg_mgr.create_segment("image", cfg)
        if not result["success"]:
            raise ValueError(f"创建图片片段失败: {result['message']}")
        seg_id = result["segment_id"]

        for anim_key, dur_key in [
            ("in_animation", "in_animation_duration"),
            ("out_animation", "out_animation_duration"),
            ("loop_animation", "loop_animation_duration"),
        ]:
            if img.get(anim_key):
                seg_mgr.add_operation(seg_id, "add_animation", {
                    "animation_type": img[anim_key],
                    "duration": str(img.get(dur_key, 1_000_000)),
                })

        if img.get("transition"):
            seg_mgr.add_operation(seg_id, "add_transition", {
                "transition_type": img["transition"],
            })

        _append_segment(draft_id, seg_id, track_index)
        segment_ids.append(seg_id)
        segment_infos.append({"id": seg_id, "start": start, "end": end})

    logger.info(f"add_images 完成: track={track_index}, images={len(segment_ids)}")
    return str(track_index), segment_ids, segment_ids, segment_infos


# ============================================================
# ④ add_sticker
# ============================================================

def add_sticker(
    draft_id: str,
    sticker_id: str,
    start: int,
    end: int,
    scale: float = 1.0,
    transform_x: int = 0,
    transform_y: int = 0,
) -> Tuple[str, str, str, int]:
    """向草稿添加贴纸，返回 (sticker_id, track_id, segment_id, duration)。"""
    seg_mgr = get_segment_manager()
    project = _get_draft_project(draft_id)
    draft_w = project.get("width", 1920) or 1920
    draft_h = project.get("height", 1080) or 1080

    if end <= start:
        raise ValueError("end 必须大于 start")

    duration = end - start
    track_index = _add_track(draft_id, "sticker")
    cfg: Dict[str, Any] = {
        "resource_id": sticker_id,
        "target_timerange": {"start": start, "duration": duration},
        "scale_x": scale,
        "scale_y": scale,
        # DraftSaver sticker 分支读取 position_x/y 作为 ClipSettings.transform
        "position_x": transform_x / (draft_w / 2),
        "position_y": transform_y / (draft_h / 2),
        "opacity": 1.0,
    }
    result = seg_mgr.create_segment("sticker", cfg)
    if not result["success"]:
        raise ValueError(f"创建贴纸片段失败: {result['message']}")
    seg_id = result["segment_id"]
    _append_segment(draft_id, seg_id, track_index)

    logger.info(f"add_sticker 完成: track={track_index}, segment={seg_id}")
    return sticker_id, str(track_index), seg_id, duration


# ============================================================
# ⑤ add_keyframes
# ============================================================

def add_keyframes(draft_id: str, keyframes_str: str) -> Tuple[int, List[str]]:
    """为已有片段添加关键帧，返回 (added_count, affected_segments)。"""
    seg_mgr = get_segment_manager()
    _get_draft_project(draft_id)  # 验证存在性

    kf_items: List[Dict] = _parse_json_list(keyframes_str, "keyframes")
    if not kf_items:
        raise ValueError("keyframes 为空")

    added = 0
    affected: List[str] = []

    for item in kf_items:
        seg_id = item.get("segment_id", "")
        if not seg_id:
            logger.warning("关键帧条目缺少 segment_id，跳过")
            continue
        ok = seg_mgr.add_operation(seg_id, "add_keyframe", {
            "property": item.get("property", ""),
            "offset": int(item.get("offset", 0)),
            "value": float(item.get("value", 0)),
        })
        if ok:
            added += 1
            if seg_id not in affected:
                affected.append(seg_id)

    logger.info(f"add_keyframes 完成: added={added}, affected={len(affected)}")
    return added, affected


# ============================================================
# ⑥ add_captions
# ============================================================

def add_captions(
    draft_id: str,
    captions_str: str,
    text_color: str = "#ffffff",
    border_color: Optional[str] = None,
    alignment: int = 1,
    alpha: float = 1.0,
    font: Optional[str] = None,
    font_size: int = 15,
    letter_spacing: Optional[float] = None,
    line_spacing: Optional[float] = None,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    transform_x: float = 0.0,
    transform_y: float = 0.0,
    style_text: bool = False,
    underline: bool = False,
    italic: bool = False,
    bold: bool = False,
    has_shadow: bool = False,
    shadow_info=None,
) -> Tuple[str, List[str], List[str], List[Dict]]:
    """向草稿添加字幕，返回 (track_id, text_ids, segment_ids, segment_infos)。"""
    seg_mgr = get_segment_manager()
    project = _get_draft_project(draft_id)
    draft_w = project.get("width", 1920) or 1920
    draft_h = project.get("height", 1080) or 1080

    captions: List[Dict] = _parse_json_list(captions_str, "captions")
    if not captions:
        raise ValueError("captions 为空")

    track_index = _add_track(draft_id, "text")
    text_ids: List[str] = []
    segment_ids: List[str] = []
    segment_infos: List[Dict] = []

    for cap in captions:
        start = int(cap["start"])
        end = int(cap["end"])
        fs = float(cap["font_size"]) if cap.get("font_size") is not None else float(font_size)

        shadow_cfg: Optional[Dict[str, Any]] = None
        if has_shadow:
            if shadow_info:
                shadow_cfg = {
                    "alpha": shadow_info.shadow_alpha,
                    "color": shadow_info.shadow_color,
                    "diffuse": shadow_info.shadow_diffuse,
                    "distance": shadow_info.shadow_distance,
                    "angle": shadow_info.shadow_angle,
                }
            else:
                shadow_cfg = {
                    "alpha": 0.9, "color": "#000000",
                    "diffuse": 15.0, "distance": 5.0, "angle": -45.0,
                }

        cfg: Dict[str, Any] = {
            "text_content": cap.get("text", ""),
            "font_family": font or "文轩体",
            "text_color": text_color,
            "font_size": fs,
            "bold": bold,
            "italic": italic,
            "underline": underline,
            "alignment": alignment,
            "alpha": alpha,
            "letter_spacing": int(letter_spacing) if letter_spacing is not None else 0,
            "line_spacing": int(line_spacing) if line_spacing is not None else 0,
            "border_color": border_color,
            "shadow": shadow_cfg,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "transform_x": transform_x / draft_w,
            "transform_y": transform_y / draft_h,
            "target_timerange": {"start": start, "duration": end - start},
            # 关键词高亮（DraftSaver 暂不支持，存入备用）
            "keyword": cap.get("keyword"),
            "keyword_color": cap.get("keyword_color", "#ff7100"),
            "keyword_font_size": cap.get("keyword_font_size"),
        }
        result = seg_mgr.create_segment("text", cfg)
        if not result["success"]:
            raise ValueError(f"创建字幕片段失败: {result['message']}")
        seg_id = result["segment_id"]

        for anim_key, dur_key in [
            ("in_animation", "in_animation_duration"),
            ("out_animation", "out_animation_duration"),
            ("loop_animation", "loop_animation_duration"),
        ]:
            anim_name = cap.get(anim_key)
            if anim_name:
                seg_mgr.add_operation(seg_id, "add_animation", {
                    "animation_type": anim_name,
                    "duration": str(cap.get(dur_key, 1_000_000)),
                })

        _append_segment(draft_id, seg_id, track_index)
        text_ids.append(seg_id)
        segment_ids.append(seg_id)
        segment_infos.append({"id": seg_id, "start": start, "end": end})

    logger.info(f"add_captions 完成: track={track_index}, captions={len(segment_ids)}")
    return str(track_index), text_ids, segment_ids, segment_infos


# ============================================================
# ⑦ add_effects
# ============================================================

def add_effects(draft_id: str, effect_infos_str: str) -> Tuple[str, List[str], List[str]]:
    """向草稿添加特效，返回 (track_id, effect_ids, segment_ids)。"""
    seg_mgr = get_segment_manager()
    _get_draft_project(draft_id)  # 验证存在性

    effects: List[Dict] = _parse_json_list(effect_infos_str, "effect_infos")
    if not effects:
        raise ValueError("effect_infos 为空")

    track_index = _add_track(draft_id, "effect")
    effect_ids: List[str] = []
    segment_ids: List[str] = []

    for eff in effects:
        start = int(eff["start"])
        end = int(eff["end"])
        cfg: Dict[str, Any] = {
            "effect_type": eff["effect_title"],
            "target_timerange": {"start": start, "duration": end - start},
        }
        result = seg_mgr.create_segment("effect", cfg)
        if not result["success"]:
            raise ValueError(f"创建特效片段失败: {result['message']}")
        seg_id = result["segment_id"]
        _append_segment(draft_id, seg_id, track_index)
        effect_ids.append(seg_id)
        segment_ids.append(seg_id)

    logger.info(f"add_effects 完成: track={track_index}, effects={len(segment_ids)}")
    return str(track_index), effect_ids, segment_ids


# ============================================================
# ⑧ add_masks
# ============================================================

def add_masks(
    draft_id: str,
    segment_ids_list: List[str],
    name: str = "线性",
    X: int = 0,
    Y: int = 0,
    width: int = 512,
    height: int = 512,
    feather: int = 0,
    rotation: int = 0,
    invert: bool = False,
    roundCorner: int = 0,
) -> Tuple[int, List[str], List[str]]:
    """为已有片段添加遮罩，返回 (masks_added, affected_segments, mask_ids)。"""
    seg_mgr = get_segment_manager()
    project = _get_draft_project(draft_id)
    draft_w = project.get("width", 1920) or 1920
    draft_h = project.get("height", 1080) or 1080

    # 将像素值归一化为相对比率（DraftSaver 在 add_mask 时使用）
    size = height / draft_h
    rect_w: Optional[float] = (width / draft_w) if name == "矩形" else None

    masks_added = 0
    affected: List[str] = []
    mask_ids: List[str] = []

    for seg_id in segment_ids_list:
        mask_id = str(uuid.uuid4())
        op_data: Dict[str, Any] = {
            "mask_type_name": name,
            "center_x": float(X),
            "center_y": float(Y),
            "size": size,
            "rotation": float(rotation),
            "feather": float(feather),
            "invert": invert,
            "mask_id": mask_id,
        }
        if rect_w is not None:
            op_data["rect_width"] = rect_w
        if name == "矩形":
            op_data["round_corner"] = float(roundCorner)

        ok = seg_mgr.add_operation(seg_id, "add_mask", op_data)
        if ok:
            masks_added += 1
            affected.append(seg_id)
            mask_ids.append(mask_id)

    logger.info(f"add_masks 完成: masks_added={masks_added}")
    return masks_added, affected, mask_ids
