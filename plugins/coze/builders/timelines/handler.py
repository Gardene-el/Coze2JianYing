"""
生成时间线工具处理器 (make_timelines)

纯计算工具——将总时长分割为 N 段时间线，返回 JSON 字符串。
用于替代原 capcut-mate 的 /timelines 路由。

无网络请求，无文件 I/O。
"""

import json
import random
from typing import Dict, Any, List, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """make_timelines 工具的输入参数"""
    duration: int           # 总时长（微秒）
    num: int                # 分割段数
    start: int = 0          # 起始偏移（微秒，默认 0）
    split_type: int = 0     # 0=平均分割，1=随机分割


class Output(NamedTuple):
    """make_timelines 工具的输出"""
    timelines: str          # 时间线 JSON 字符串，格式: [{"start":…,"end":…},…]
    all_timelines: str      # 同 timelines（合并后的完整列表，与 timelines 相同）
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将总时长分割为 N 段时间线。

    Args:
        args.input.duration:   总时长（微秒）
        args.input.num:        分割段数
        args.input.start:      起始偏移（微秒，默认 0）
        args.input.split_type: 0=平均分，1=随机

    Returns:
        Output._asdict()
    """
    logger = getattr(args, "logger", None)

    try:
        duration = int(args.input.duration)
        num = int(args.input.num)
        start = int(args.input.start)
        split_type = int(args.input.split_type)

        if duration <= 0:
            raise ValueError("duration 必须大于 0")
        if num <= 0:
            raise ValueError("num 必须大于 0")

        segments: List[Dict[str, int]] = []

        if split_type == 1:
            # 随机分割：先生成 num-1 个随机分界点，再排序
            breakpoints = sorted(random.randint(1, duration - 1) for _ in range(num - 1))
            breakpoints = [0] + breakpoints + [duration]
            for i in range(num):
                seg_start = start + breakpoints[i]
                seg_end = start + breakpoints[i + 1]
                segments.append({"start": seg_start, "end": seg_end})
        else:
            # 平均分割（默认）
            seg_dur = duration // num
            for i in range(num):
                seg_start = start + i * seg_dur
                # 最后一段取到 duration 末尾，避免舍入误差
                seg_end = start + duration if i == num - 1 else seg_start + seg_dur
                segments.append({"start": seg_start, "end": seg_end})

        timelines_str = json.dumps(segments, ensure_ascii=False)

        if logger:
            logger.info(f"make_timelines: duration={duration}, num={num}, split_type={split_type}")

        return Output(
            timelines=timelines_str,
            all_timelines=timelines_str,
            success=True,
            message=f"已生成 {len(segments)} 段时间线",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"make_timelines 失败: {exc}")
        return Output(
            timelines="[]",
            all_timelines="[]",
            success=False,
            message=str(exc),
        )._asdict()
