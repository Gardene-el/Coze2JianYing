"""
segments/_base.py — 片段模块共用的下载工具函数。

替代原来的 SegmentRepository 持久化工具；无状态，仅负责将 URL 下载为本地文件。
"""
import os
from typing import Optional

from app.backend.utils.logger import logger


def download_material(url: str, assets_dir: str) -> str:
    """
    将素材 URL 下载到 assets_dir，返回本地文件路径。

    若文件已存在（同名缓存）则直接返回，不重复下载。

    Raises:
        RuntimeError: 下载失败
    """
    import requests

    os.makedirs(assets_dir, exist_ok=True)

    # 提取文件名（去掉 query string）
    filename = url.split("/")[-1].split("?")[0] or "material"
    save_path = os.path.join(assets_dir, filename)

    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
        logger.debug("素材已缓存，跳过下载: %s", save_path)
        return save_path

    logger.info("下载素材: %s → %s", url, save_path)
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()

        # 若服务器返回了 Content-Disposition 推断更合适的扩展名
        content_type = resp.headers.get("Content-Type", "")
        if "." not in filename:
            ext = _ext_from_content_type(content_type)
            save_path = save_path + ext

        with open(save_path, "wb") as f:
            f.write(resp.content)
        logger.info("素材下载完成: %s (%d bytes)", save_path, len(resp.content))
        return save_path
    except Exception as exc:
        raise RuntimeError(f"素材下载失败 [{url}]: {exc}") from exc


def _ext_from_content_type(content_type: str) -> str:
    _MAP = {
        "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
        "image/gif": ".gif", "image/webp": ".webp",
        "video/mp4": ".mp4", "video/quicktime": ".mov", "video/x-msvideo": ".avi",
        "audio/mpeg": ".mp3", "audio/mp4": ".m4a", "audio/wav": ".wav",
        "audio/aac": ".aac", "audio/ogg": ".ogg",
    }
    base = content_type.split(";")[0].strip().lower()
    return _MAP.get(base, "")
