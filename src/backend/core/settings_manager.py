"""
全局设置管理器

归属：core/ — 纯内存状态，持久化完全由 Electron store 负责。
Python 进程只需在内存中维护由前端通过 PUT /gui/settings 推送过来的值：
  draft_folder, transfer_enabled, effective_output_path, effective_assets_base_path

路径决策逻辑已迁移到 Electron 主进程的 PathResolverService（TypeScript）。
Python 服务直接读取预计算好的 effective_* 路径，不再执行任何 fs 判断。
"""
from typing import Any, Dict, Optional
from src.backend.utils.logger import logger


class SettingsManager:
    """全局设置管理器（纯内存 KV 容器，无文件 I/O，无路径决策逻辑）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logger
        self._settings: Dict[str, Any] = {
            "draft_folder": "",
            # Pre-computed by Electron main process PathResolverService.
            # Empty string means Python should fall back to config.drafts_dir / config.assets_dir.
            "effective_output_path": "",
            "effective_assets_base_path": "",
        }
        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        return self._settings.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """获取所有设置"""
        return self._settings.copy()

    def update(self, data: Dict[str, Any]) -> None:
        """批量更新内存设置（仅保留已知键，忽略其他字段）"""
        allowed = {
            "draft_folder",
            "effective_assets_base_path",
            "effective_output_path",
        }
        for key, value in data.items():
            if key in allowed:
                self._settings[key] = value


def get_settings_manager() -> SettingsManager:
    """获取设置管理器实例（单例）"""
    return SettingsManager()
