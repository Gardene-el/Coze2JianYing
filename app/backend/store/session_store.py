"""
session_store.py — 进程内内存 Session Store

持有所有运行中草稿（ScriptFile）和片段（AudioSegment / VideoSegment / ...）的
原生 pyJianYingDraft 对象，替代原来的 JSON 文件 Repository。

设计原则：
- 进程级单例：`get_session_store()` 返回唯一实例
- 草稿和片段在进程生命周期内有效（重启后清空，符合脚本执行场景）
- 无 I/O 依赖：纯内存操作，速度快且无文件系统副作用

使用方式::

    from app.backend.store.session_store import get_session_store, SessionStore

    session = get_session_store()
    session.store_draft(draft_id, script_file_obj, meta_dict)
    script = session.get_draft(draft_id)
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# SessionStore
# ---------------------------------------------------------------------------

class SessionStore:
    """
    进程内内存 Session Store。

    持有两个主要字典：
    - `_drafts`：draft_id → pyJianYingDraft.ScriptFile
    - `_segments`：segment_id → AudioSegment / VideoSegment / TextSegment / ...

    以及对应的元数据字典（供状态查询端点使用）：
    - `_draft_meta`：draft_id → {name, width, height, fps, status, output_path}
    - `_segment_meta`：segment_id → {type, material_url}
    """

    def __init__(self) -> None:
        self._drafts: Dict[str, Any] = {}        # draft_id → ScriptFile
        self._draft_meta: Dict[str, Dict[str, Any]] = {}
        self._segments: Dict[str, Any] = {}      # segment_id → *Segment
        self._segment_meta: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # 草稿
    # ------------------------------------------------------------------

    def store_draft(self, draft_id: str, script, meta: Dict[str, Any], allow_replace: bool = True) -> None:
        """存入草稿对象及元数据。allow_replace=False 时，若 draft_id 已存在则抛 CustomException。"""
        with self._lock:
            if not allow_replace and draft_id in self._drafts:
                raise CustomException(CustomError.DRAFT_ALREADY_EXISTS, f"draft_id={draft_id}")
            self._drafts[draft_id] = script
            self._draft_meta[draft_id] = {**meta, "draft_id": draft_id}
        logger.debug("SessionStore: 草稿已存入 %s", draft_id)

    def get_draft(self, draft_id: str):
        """获取草稿 ScriptFile 对象；不存在则抛 CustomException。"""
        script = self._drafts.get(draft_id)
        if script is None:
            raise CustomException(CustomError.DRAFT_NOT_FOUND, f"draft_id={draft_id}")
        return script

    def get_draft_meta(self, draft_id: str) -> Dict[str, Any]:
        """获取草稿元数据的**浅拷贝**；不存在则抛 CustomException。

        返回拷贝而非原始 dict，防止外部直接修改时绕过锁。
        """
        meta = self._draft_meta.get(draft_id)
        if meta is None:
            raise CustomException(CustomError.DRAFT_NOT_FOUND, f"draft_id={draft_id}")
        return dict(meta)

    def update_draft_meta(self, draft_id: str, updates: Dict[str, Any]) -> None:
        """更新草稿元数据字段。"""
        with self._lock:
            meta = self._draft_meta.get(draft_id)
            if meta is None:
                raise CustomException(CustomError.DRAFT_NOT_FOUND, f"draft_id={draft_id}")
            meta.update(updates)

    def delete_draft(self, draft_id: str) -> None:
        """从 Session 中删除草稿（不影响磁盘上已保存的文件）。"""
        with self._lock:
            self._drafts.pop(draft_id, None)
            self._draft_meta.pop(draft_id, None)
        logger.debug("SessionStore: 草稿已删除 %s", draft_id)

    def list_draft_ids(self):
        """返回当前所有草稿 ID 列表。"""
        return list(self._draft_meta.keys())

    def list_segment_ids(self):
        """返回当前所有片段 ID 列表。"""
        return list(self._segment_meta.keys())

    # ------------------------------------------------------------------
    # 片段
    # ------------------------------------------------------------------

    def store_segment(self, segment_id: str, segment, meta: Dict[str, Any]) -> None:
        """存入片段对象及元数据。"""
        with self._lock:
            self._segments[segment_id] = segment
            self._segment_meta[segment_id] = {**meta, "segment_id": segment_id}
        logger.debug("SessionStore: 片段已存入 %s (%s)", segment_id, meta.get("type"))

    def get_segment(self, segment_id: str):
        """获取片段原生对象；不存在则抛 CustomException。"""
        seg = self._segments.get(segment_id)
        if seg is None:
            raise CustomException(CustomError.SEGMENT_NOT_FOUND, f"segment_id={segment_id}")
        return seg

    def get_segment_meta(self, segment_id: str) -> Dict[str, Any]:
        """获取片段元数据；不存在则抛 CustomException。"""
        meta = self._segment_meta.get(segment_id)
        if meta is None:
            raise CustomException(CustomError.SEGMENT_NOT_FOUND, f"segment_id={segment_id}")
        return meta

    def get_segment_or_none(self, segment_id: str) -> Optional[Any]:
        """获取片段原生对象；不存在则返回 None。"""
        return self._segments.get(segment_id)

    def delete_segment(self, segment_id: str) -> None:
        """从 Session 中删除片段。"""
        with self._lock:
            self._segments.pop(segment_id, None)
            self._segment_meta.pop(segment_id, None)


# ---------------------------------------------------------------------------
# 进程级单例
# ---------------------------------------------------------------------------

_store = SessionStore()


def get_session_store() -> SessionStore:
    """返回进程级唯一 SessionStore 实例（用于 FastAPI Depends 注入）。"""
    return _store

