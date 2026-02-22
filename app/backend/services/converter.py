"""
转换器兼容层（Converter Compatibility Shim）

此模块为 draft_generator.py 等旧调用方提供向后兼容的 DraftInterfaceConverter 类。
内部委托给 adapters/jianying_adapter.py 中的纯函数。

注意：新代码应直接使用 app.backend.adapters.jianying_adapter 中的函数。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.backend.adapters.jianying_adapter import (
    build_audio_segment,
    build_video_segment,
    build_text_segment,
)
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


class DraftInterfaceConverter:
    """
    草稿接口转换器（兼容包装类）

    将 CozeOutputParser 输出的 segment_config 字典映射为
    pyJianYingDraft 片段对象。内部委托给 jianying_adapter.py 纯函数。
    """

    def convert_video_segment_config(
        self,
        segment_config: Dict[str, Any],
        video_material=None,
    ):
        """
        将视频片段配置转换为 pyJianYingDraft VideoSegment。

        Args:
            segment_config: 片段配置字典(来自 CozeOutputParser / draft_generator)
            video_material: 已下载的素材对象（含 .path 属性）
        """
        local_path = video_material.path if hasattr(video_material, "path") else None
        return build_video_segment(segment_config, local_path)

    def convert_audio_segment_config(
        self,
        segment_config: Dict[str, Any],
        audio_material=None,
    ):
        """
        将音频片段配置转换为 pyJianYingDraft AudioSegment。

        Args:
            segment_config: 片段配置字典
            audio_material: 已下载的素材对象（含 .path 属性）
        """
        local_path = audio_material.path if hasattr(audio_material, "path") else None
        return build_audio_segment(segment_config, local_path)

    def convert_image_segment_config(
        self,
        segment_config: Dict[str, Any],
        image_file_path: Optional[str] = None,
    ):
        """
        将图片片段配置转换为 pyJianYingDraft VideoSegment。
        图片在 pyJianYingDraft 中复用 VideoSegment，路径指向本地图片文件。

        Args:
            segment_config: 片段配置字典
            image_file_path: 本地图片文件路径
        """
        return build_video_segment(segment_config, image_file_path)

    def convert_text_segment_config(
        self,
        segment_config: Dict[str, Any],
    ):
        """
        将文本片段配置转换为 pyJianYingDraft TextSegment。

        Args:
            segment_config: 片段配置字典
        """
        return build_text_segment(segment_config)
