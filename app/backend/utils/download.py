"""下载工具：capcut-mate 风格统一入口。"""

from __future__ import annotations

import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote

import httpx
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class DownloadValidationError(Exception):
    """下载内容校验失败。"""


def _get_extension_from_content_type(content_type: Optional[str]) -> str:
    if not content_type:
        return ".mp4"
    content_type = content_type.split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(content_type)
    return ext or ".mp4"


def _detect_content_type(url: str, timeout: float = 20.0) -> Optional[str]:
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            response = client.head(url)
            response.raise_for_status()
            return response.headers.get("Content-Type")
    except Exception:
        return None


def _build_filename(url: str, filename: Optional[str], content_type: Optional[str]) -> str:
    if filename:
        return filename

    parsed = urlparse(url)
    path = unquote(parsed.path)
    extracted = os.path.basename(path)
    if extracted and "." in extracted:
        return extracted

    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return f"material_{url_hash}{_get_extension_from_content_type(content_type)}"


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((requests.RequestException, OSError, DownloadValidationError)),
)
def _download_once(url: str, target_path: Path, timeout: float, chunk_size: int, min_size_bytes: int) -> Path:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "image/*,video/*,audio/*,*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }

    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    try:
        with requests.get(
            url,
            stream=True,
            timeout=timeout,
            allow_redirects=True,
            headers=headers,
        ) as response:
            response.raise_for_status()

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "wb") as output:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        output.write(chunk)

        if not temp_path.exists() or temp_path.stat().st_size < min_size_bytes:
            raise DownloadValidationError(
                f"Downloaded file too small: {temp_path.stat().st_size if temp_path.exists() else 0} bytes"
            )

        if target_path.exists():
            target_path.unlink()
        temp_path.rename(target_path)
        return target_path
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def download(
    url: str,
    save_dir: str,
    *,
    filename: Optional[str] = None,
    timeout: float = 60.0,
    chunk_size: int = 8192,
    min_size_bytes: int = 100,
) -> str:
    """下载文件到指定目录并返回本地路径。"""
    content_type = _detect_content_type(url)
    target_filename = _build_filename(url=url, filename=filename, content_type=content_type)
    target_path = Path(save_dir) / target_filename
    downloaded_path = _download_once(
        url=url,
        target_path=target_path,
        timeout=timeout,
        chunk_size=chunk_size,
        min_size_bytes=min_size_bytes,
    )
    return str(downloaded_path)
