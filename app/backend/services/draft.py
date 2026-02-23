"""
draft.py — 草稿业务逻辑层

每个方法都对应 pyJianYingDraft.ScriptFile / DraftFolder 的一个操作。

ScriptFile 对象由 DRAFT_CACHE 管理（进程级 LRU 缓存）。
Segment 对象和元数据仍由 SessionStore 管理。
保存操作在调用 save() 时调用 script.save() 写出文件。
"""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pyJianYingDraft as draft

from app.backend.exceptions import CustomError, CustomException
from app.backend.store.session_store import SessionStore
from app.backend.utils.cache import DRAFT_CACHE, update_draft_cache
from app.backend.utils.logger import logger


# ---------------------------------------------------------------------------
# track_type 字符串 → pyJianYingDraft TrackType 枚举
# ---------------------------------------------------------------------------

_TRACK_TYPE_MAP: Dict[str, Any] = {
    "audio": draft.TrackType.audio,
    "video": draft.TrackType.video,
    "text": draft.TrackType.text,
    "sticker": draft.TrackType.sticker,
    "effect": draft.TrackType.effect,
    "filter": draft.TrackType.filter,
}


def _resolve_track_type(track_type: str) -> Any:
    jy_type = _TRACK_TYPE_MAP.get(track_type.lower())
    if jy_type is None:
        raise CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            f"不支持的轨道类型: '{track_type}'，合法值: {list(_TRACK_TYPE_MAP.keys())}"
        )
    return jy_type


# ---------------------------------------------------------------------------
# DraftService
# ---------------------------------------------------------------------------

class DraftService:
    """
    草稿业务逻辑服务。

    - 草稿对象（ScriptFile）由 DRAFT_CACHE（进程级 LRU 全局字典）管理。
    - Segment 对象和元数据仍由 SessionStore 管理。
    """

    def __init__(self, session: SessionStore, settings):
        self._session = session
        self._settings = settings

    # ------------------------------------------------------------------
    # 对应 DraftFolder.create_draft
    # ------------------------------------------------------------------

    def create_draft(
        self,
        draft_name: str,
        width: int,
        height: int,
        fps: int,
    ) -> str:
        """创建草稿，将 ScriptFile 存入 DraftCache，并向 SessionStore 注册元数据。返回 draft_id。"""
        draft_id = str(uuid.uuid4())
        self._settings.reload()
        output_dir = self._settings.get_effective_output_path()

        draft_folder = draft.DraftFolder(output_dir)
        script = draft_folder.create_draft(draft_name, width, height, fps, allow_replace=True)

        # ScriptFile 存入 DRAFT_CACHE（对标 capcut-mate 的 update_cache）
        update_draft_cache(draft_id, script)

        # 元数据仍存入 SessionStore
        meta: Dict[str, Any] = {
            "name": draft_name,
            "width": width,
            "height": height,
            "fps": fps,
            "status": "created",
            "output_path": None,
            "created_timestamp": datetime.now().timestamp(),
        }
        self._session.store_draft(draft_id, script, meta)
        logger.info("草稿已创建: %s (%s %dx%d@%dfps)", draft_id, draft_name, width, height, fps)
        return draft_id

    # ------------------------------------------------------------------
    # 对应 ScriptFile.add_track
    # ------------------------------------------------------------------

    def add_track(
        self,
        draft_id: str,
        track_type: str,
        track_name: Optional[str] = None,
    ) -> int:
        """向草稿追加一条新轨道，返回轨道在当前草稿中的顺序索引。"""
        meta = self._session.get_draft_meta(draft_id)
        tracks: List[Dict] = meta.setdefault("tracks", [])

        if track_name is None:
            n = sum(1 for t in tracks if t["track_type"] == track_type)
            track_name = f"{track_type}_{n}"

        # 通过 DRAFT_CACHE 直接取 ScriptFile
        if draft_id not in DRAFT_CACHE:
            raise CustomException(CustomError.DRAFT_NOT_FOUND, f"draft_id={draft_id}")
        script = DRAFT_CACHE[draft_id]
        jy_type = _resolve_track_type(track_type)
        script.add_track(jy_type, track_name)

        track_index = len(tracks)
        tracks.append({"track_type": track_type, "track_name": track_name})
        self._session.update_draft_meta(draft_id, {"tracks": tracks})

        logger.info("轨道已添加: draft=%s type=%s name=%s index=%d", draft_id, track_type, track_name, track_index)
        return track_index

    # ------------------------------------------------------------------
    # 对应 ScriptFile.add_segment
    # ------------------------------------------------------------------

    def add_segment(
        self,
        draft_id: str,
        segment_id: str,
        track_name: Optional[str] = None,
        track_index: Optional[int] = None,
    ) -> None:
        """将片段关联到草稿轨道。"""
        script = DRAFT_CACHE.get(draft_id)
        if script is None:
            raise CustomException(CustomError.DRAFT_NOT_FOUND, f"draft_id={draft_id}")
        seg = self._session.get_segment(segment_id)

        if track_name is None and track_index is not None:
            meta = self._session.get_draft_meta(draft_id)
            tracks: List[Dict] = meta.get("tracks", [])
            if 0 <= track_index < len(tracks):
                track_name = tracks[track_index]["track_name"]

        script.add_segment(seg, track_name)
        logger.info("片段已关联: draft=%s segment=%s track=%s", draft_id, segment_id, track_name)

    # ------------------------------------------------------------------
    # 全局特效 / 滤镜
    # ------------------------------------------------------------------

    def add_global_effect(
        self,
        draft_id: str,
        effect_type: str,
        target_timerange: Dict[str, int],
        params: Optional[List[Optional[float]]] = None,
    ) -> None:
        """添加全局特效。"""
        from app.backend.adapters.jianying_adapter import resolve_video_effect_enum
        from pyJianYingDraft import trange as jy_trange

        script = self._draft_cache.get(draft_id)
        t_range = jy_trange(
            f"{target_timerange.get('start', 0) / 1_000_000}s",
            f"{target_timerange.get('duration', 1_000_000) / 1_000_000}s",
        )
        effect_enum = resolve_video_effect_enum(effect_type)
        if params is not None:
            script.add_effect(effect_enum, t_range, params=params)
        else:
            script.add_effect(effect_enum, t_range)
        logger.info("全局特效已添加: draft=%s type=%s", draft_id, effect_type)

    def add_global_filter(
        self,
        draft_id: str,
        filter_type: str,
        target_timerange: Dict[str, int],
        intensity: float = 1.0,
    ) -> None:
        """添加全局滤镜。"""
        from pyJianYingDraft import FilterType, trange as jy_trange

        script = self._draft_cache.get(draft_id)
        t_range = jy_trange(
            f"{target_timerange.get('start', 0) / 1_000_000}s",
            f"{target_timerange.get('duration', 1_000_000) / 1_000_000}s",
        )
        filter_name = filter_type.split(".")[-1] if "." in filter_type else filter_type
        try:
            filter_enum = FilterType[filter_name]
        except KeyError:
            valid = [m.name for m in FilterType][:50]
            raise CustomException(
                CustomError.PARAM_VALIDATION_FAILED,
                f"未知的滤镜类型: '{filter_name}'，合法値（前50个）: {valid}",
            )
        script.add_filter(filter_enum, t_range, intensity=intensity)
        logger.info("全局滤镜已添加: draft=%s type=%s", draft_id, filter_type)

    # ------------------------------------------------------------------
    # 保存
    # ------------------------------------------------------------------

    def save(self, draft_id: str) -> str:
        """保存草稿到磁盘，对应 ScriptFile.save()。"""
        script = self._draft_cache.get(draft_id)
        script.save()

        meta = self._session.get_draft_meta(draft_id)
        self._settings.reload()
        output_dir = self._settings.get_effective_output_path()
        draft_name = meta.get("name", "Untitled")
        output_path = str(Path(output_dir) / draft_name)

        self._session.update_draft_meta(draft_id, {
            "status": "saved",
            "output_path": output_path,
        })
        logger.info("草稿已保存: %s → %s", draft_id, output_path)
        return output_path

    # ------------------------------------------------------------------
    # 查询 / 删除
    # ------------------------------------------------------------------

    def get_status(self, draft_id: str) -> Dict[str, Any]:
        """返回草稿元数据。"""
        return self._session.get_draft_meta(draft_id)

    def delete_draft(self, draft_id: str) -> None:
        """从 Session 中删除草稿（不影响磁盘文件）。"""
        self._session.delete_draft(draft_id)
        logger.info("草稿已从 Session 删除: %s", draft_id)

    def mark_saved(self, draft_id: str, draft_path: str) -> None:
        """向后兼容：更新草稿保存状态。"""
        self._session.update_draft_meta(draft_id, {
            "status": "saved",
            "output_path": draft_path,
        })

