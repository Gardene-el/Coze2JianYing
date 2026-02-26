"""
FastAPI 依赖注入工厂（Dependencies）

移除了 Repository 层和 ExportService，改为使用进程级 SessionStore。
DraftService 通过模块级全局 DRAFT_CACHE 持有草稿对象。
"""
from __future__ import annotations

from app.backend.config import AppConfig, get_config
from app.backend.core.settings_manager import SettingsManager, get_settings_manager


# ---------------------------------------------------------------------------
# 基础设施
# ---------------------------------------------------------------------------

def get_app_config() -> AppConfig:
    """注入应用配置（不可变，单例安全）。"""
    return get_config()


def get_settings() -> SettingsManager:
    """注入用户设置管理器（单例）。"""
    return get_settings_manager()
