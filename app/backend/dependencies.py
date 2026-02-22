"""
FastAPI 依赖注入工厂（Dependencies）

移除了 Repository 层和 ExportService，改为使用进程级 SessionStore。
DraftService 通过模块级全局 DRAFT_CACHE 持有草稿对象。
"""
from __future__ import annotations

from app.backend.config import AppConfig, get_config
from app.backend.core.settings_manager import SettingsManager, get_settings_manager
from app.backend.store.session_store import SessionStore, get_session_store
from app.backend.services.draft import DraftService


# ---------------------------------------------------------------------------
# 基础设施
# ---------------------------------------------------------------------------

def get_app_config() -> AppConfig:
    """注入应用配置（不可变，单例安全）。"""
    return get_config()


def get_settings() -> SettingsManager:
    """注入用户设置管理器（单例）。"""
    return get_settings_manager()


def get_session() -> SessionStore:
    """注入进程级 SessionStore 单例（管理 segment 对象和元数据）。"""
    return get_session_store()


# ---------------------------------------------------------------------------
# 服务层
# ---------------------------------------------------------------------------

def get_draft_service() -> DraftService:
    """
    构造 DraftService 实例。

    - SessionStore：管理 segment 对象和 draft/segment 元数据。
    - DRAFT_CACHE：模块级全局字典，直接由 DraftService 内部使用。
    - SettingsManager：读取剪映输出路径等用户设置。
    """
    return DraftService(
        session=get_session_store(),
        settings=get_settings_manager(),
    )

