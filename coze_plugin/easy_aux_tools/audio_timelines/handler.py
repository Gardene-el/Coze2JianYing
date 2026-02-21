"""
根据音频时长列表生成时间线 (make_audio_timelines)

纯计算工具——接收各段音频的时长（微秒）列表，
按顺序累加生成时间线 JSON 字符串。

配合 get_media_duration 工具使用：
  1. 对每个音频 URL 调用 get_media_duration → 得到 duration_us
  2. 将所有 duration_us 用逗号拼接传入本工具

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, List, NamedTuple

from runtime import Args


class Input(NamedTuple):
    """make_audio_timelines 工具的输入参数"""
    # 各段音频时长（微秒），用英文逗号分隔，如 "5000000,4000000,6000000"
    durations_us: str
    # 起始偏移（微秒，默认 0）
    start: int = 0


class Output(NamedTuple):
    """make_audio_timelines 工具的输出"""
    timelines: str      # JSON 字符串：[{"start":…,"end":…},…]
    all_timelines: str  # 同 timelines
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    根据各音频时长依次累加，生成连续衔接的时间线段。

    Args:
        args.input.durations_us: 逗号分隔的时长列表（微秒）
        args.input.start:        起始偏移（微秒，默认 0）

    Returns:
        Output._asdict()
    """
    logger = getattr(args, "logger", None)

    try:
        raw = args.input.durations_us.strip()
        if not raw:
            raise ValueError("durations_us 不能为空")

        parts = [p.strip() for p in raw.split(",") if p.strip()]
        durations: List[int] = [int(p) for p in parts]

        if not durations:
            raise ValueError("解析后时长列表为空")

        start = int(args.input.start)
        segments: List[Dict[str, int]] = []
        cursor = start

        for dur in durations:
            if dur <= 0:
                raise ValueError(f"时长必须大于 0，当前值: {dur}")
            segments.append({"start": cursor, "end": cursor + dur})
            cursor += dur

        timelines_str = json.dumps(segments, ensure_ascii=False)

        if logger:
            logger.info(f"make_audio_timelines: {len(segments)} 段，总时长 {cursor - start} μs")

        return Output(
            timelines=timelines_str,
            all_timelines=timelines_str,
            success=True,
            message=f"已生成 {len(segments)} 段音频时间线",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"make_audio_timelines 失败: {exc}")
        return Output(
            timelines="[]",
            all_timelines="[]",
            success=False,
            message=str(exc),
        )._asdict()
