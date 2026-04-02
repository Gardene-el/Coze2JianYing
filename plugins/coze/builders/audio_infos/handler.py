"""
生成音频信息列表 JSON 工具 (audio_infos)

纯计算工具——将音频 URL 列表与时间线合并，
生成 add_audios 工具所需的 audio_infos JSON 字符串。

timelines 通常来自 audio_timelines/ 或 timelines/ 工具的输出字段。

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """audio_infos 工具的输入参数"""
    # 音频 URL 数组，JSON 字符串，如 '["url1","url2"]'
    mp3_urls: str
    # 时间线 JSON 字符串，格式: '[{"start":0,"end":5000000},...]'
    # 通常来自 audio_timelines/ 或 timelines/ 工具的 timelines 输出
    timelines: str
    # 可选：音频效果名称（统一应用到所有音频）
    audio_effect: Optional[str] = None
    # 可选：音量（0.0–2.0，默认 1.0）
    volume: Optional[float] = None


class Output(NamedTuple):
    """audio_infos 工具的输出"""
    audio_infos: str    # add_audios 所需的 audio_infos JSON 字符串
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将音频 URL 列表与时间线逐一对应，生成 add_audios 所需的 JSON 字符串。

    Args:
        args.input.mp3_urls:     JSON 数组字符串，如 '["url1","url2"]'
        args.input.timelines:    JSON 数组字符串，如 '[{"start":0,"end":5000000}]'
        args.input.audio_effect: 可选音频效果名称
        args.input.volume:       可选音量

    Returns:
        Output._asdict()
    """
    logger = getattr(args, "logger", None)

    try:
        try:
            mp3_urls = json.loads(args.input.mp3_urls)
        except json.JSONDecodeError as e:
            raise ValueError(f"mp3_urls JSON 解析失败: {e}")

        try:
            timelines = json.loads(args.input.timelines)
        except json.JSONDecodeError as e:
            raise ValueError(f"timelines JSON 解析失败: {e}")

        if not isinstance(mp3_urls, list):
            raise ValueError("mp3_urls 应为 JSON 数组")
        if not isinstance(timelines, list):
            raise ValueError("timelines 应为 JSON 数组")
        if len(mp3_urls) != len(timelines):
            raise ValueError(
                f"mp3_urls 数量 ({len(mp3_urls)}) 与 timelines 数量 ({len(timelines)}) 不匹配"
            )

        infos = []
        for audio_url, tl in zip(mp3_urls, timelines):
            info: Dict[str, Any] = {
                "audio_url": audio_url,
                "start": int(tl["start"]),
                "end": int(tl["end"]),
            }
            if args.input.audio_effect is not None:
                info["audio_effect"] = args.input.audio_effect
            if args.input.volume is not None:
                info["volume"] = float(args.input.volume)
            infos.append(info)

        result = json.dumps(infos, ensure_ascii=False)

        if logger:
            logger.info(f"audio_infos: 生成 {len(infos)} 条音频信息")

        return Output(
            audio_infos=result,
            success=True,
            message=f"已生成 {len(infos)} 条音频信息",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"audio_infos 失败: {exc}")
        return Output(
            audio_infos="[]",
            success=False,
            message=str(exc),
        )._asdict()
