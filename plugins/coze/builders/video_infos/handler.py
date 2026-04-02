"""
生成视频信息列表 JSON 工具 (video_infos)

纯计算工具——将视频 URL 列表与时间线合并，
生成 add_videos 工具所需的 video_infos JSON 字符串。

同时计算每段视频的 duration = end - start，
可附加遮罩、转场、音量等元数据。

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """video_infos 工具的输入参数"""
    # 视频 URL 数组，JSON 字符串，如 '["url1","url2"]'
    video_urls: str
    # 时间线 JSON 字符串，格式: '[{"start":0,"end":5000000},...]'
    timelines: str
    # 可选：视频高度（像素，用于遮罩/裁切计算）
    height: Optional[int] = None
    # 可选：视频宽度（像素）
    width: Optional[int] = None
    # 可选：遮罩类型（如 "圆形"、"矩形"、"爱心"、"星形"）
    mask: Optional[str] = None
    # 可选：转场类型（统一应用到所有视频）
    transition: Optional[str] = None
    # 可选：转场时长（微秒）
    transition_duration: Optional[int] = None
    # 可选：音量（0.0–10.0，默认 1.0）
    volume: Optional[float] = 1.0


class Output(NamedTuple):
    """video_infos 工具的输出"""
    video_infos: str    # add_videos 所需的 video_infos JSON 字符串
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将视频 URL 列表与时间线逐一对应，计算 duration 并附加元数据，
    生成 add_videos 所需的 JSON 字符串。
    """
    logger = getattr(args, "logger", None)

    try:
        try:
            video_urls = json.loads(args.input.video_urls)
        except json.JSONDecodeError as e:
            raise ValueError(f"video_urls JSON 解析失败: {e}")

        try:
            timelines = json.loads(args.input.timelines)
        except json.JSONDecodeError as e:
            raise ValueError(f"timelines JSON 解析失败: {e}")

        if not isinstance(video_urls, list):
            raise ValueError("video_urls 应为 JSON 数组")
        if not isinstance(timelines, list):
            raise ValueError("timelines 应为 JSON 数组")
        if len(video_urls) != len(timelines):
            raise ValueError(
                f"video_urls 数量 ({len(video_urls)}) 与 timelines 数量 ({len(timelines)}) 不匹配"
            )

        infos = []
        for video_url, tl in zip(video_urls, timelines):
            start = int(tl["start"])
            end = int(tl["end"])
            info: Dict[str, Any] = {
                "video_url": video_url,
                "start": start,
                "end": end,
                "duration": end - start,
            }
            if args.input.width is not None:
                info["width"] = int(args.input.width)
            if args.input.height is not None:
                info["height"] = int(args.input.height)
            if args.input.mask is not None:
                info["mask"] = args.input.mask
            if args.input.transition is not None:
                info["transition"] = args.input.transition
                if args.input.transition_duration is not None:
                    info["transition_duration"] = int(args.input.transition_duration)
            if args.input.volume is not None:
                info["volume"] = float(args.input.volume)
            infos.append(info)

        result = json.dumps(infos, ensure_ascii=False)

        if logger:
            logger.info(f"video_infos: 生成 {len(infos)} 条视频信息")

        return Output(
            video_infos=result,
            success=True,
            message=f"已生成 {len(infos)} 条视频信息",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"video_infos 失败: {exc}")
        return Output(
            video_infos="[]",
            success=False,
            message=str(exc),
        )._asdict()
