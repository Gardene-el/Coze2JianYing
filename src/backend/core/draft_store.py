"""
草稿文件夹路径存储

全局单例：Python 模块本身即单例。
初始值为空；由 Electron 主进程启动后通过 PUT /gui/settings 写入。
"""

_draft_folder: str = ""


def get_draft_folder() -> str:
    """返回当前草稿文件夹路径（可能为空）。"""
    return _draft_folder


def require_draft_folder() -> str:
    """返回草稿文件夹路径；若未配置则抛出 ValueError。"""
    if not _draft_folder:
        raise ValueError(
            "设置项 'draft_folder' 未配置：请先在前端设置中选择剪映草稿文件夹，"
            "或通过 PUT /gui/settings 传入对应的路径。"
        )
    return _draft_folder


def set_draft_folder(path: str) -> None:
    """设置草稿文件夹路径。"""
    global _draft_folder
    _draft_folder = path
