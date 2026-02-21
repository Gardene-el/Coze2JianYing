"""
生成字幕信息列表 JSON 工具 (caption_infos)

纯计算工具——将文本列表与时间线合并，
生成 add_captions 工具所需的 captions JSON 字符串。

关键词支持：texts 中可使用语法 "正文||关键词" 内联指定关键词；
也可通过 keywords 参数按索引为每条字幕指定关键词（优先级高于内联语法）。

动画参数支持单值（所有字幕相同）。

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, List, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """caption_infos 工具的输入参数"""
    # 文本数组，JSON 字符串，如 '["大家好","欢迎观看"]'
    # 也可以在每条文本中使用 "正文||关键词" 格式内联指定关键词
    texts: str
    # 时间线 JSON 字符串，格式: '[{"start":0,"end":3000000},...]'
    timelines: str
    # 可选：统一字体大小（对所有字幕生效）
    font_size: Optional[int] = None
    # 可选：关键词颜色（十六进制，如 "#ff7100"）
    keyword_color: Optional[str] = None
    # 可选：关键词字体大小
    keyword_font_size: Optional[int] = None
    # 可选：关键词数组，JSON 字符串，如 '["关键词1","关键词2"]'
    # 按索引对应 texts，优先级高于文本内联语法
    keywords: Optional[str] = None
    # 可选：入场动画名称（所有字幕相同）
    in_animation: Optional[str] = None
    # 可选：入场动画时长（微秒）
    in_animation_duration: Optional[int] = None
    # 可选：循环动画名称
    loop_animation: Optional[str] = None
    # 可选：循环动画时长（微秒）
    loop_animation_duration: Optional[int] = None
    # 可选：出场动画名称
    out_animation: Optional[str] = None
    # 可选：出场动画时长（微秒）
    out_animation_duration: Optional[int] = None
    # 可选：转场名称
    transition: Optional[str] = None
    # 可选：转场时长（微秒）
    transition_duration: Optional[int] = None


class Output(NamedTuple):
    """caption_infos 工具的输出"""
    captions: str       # add_captions 所需的 captions JSON 字符串
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将文本列表与时间线逐一对应，附加字体、关键词、动画参数，
    生成 add_captions 所需的 JSON 字符串。
    """
    logger = getattr(args, "logger", None)

    try:
        try:
            texts: List[str] = json.loads(args.input.texts)
        except json.JSONDecodeError as e:
            raise ValueError(f"texts JSON 解析失败: {e}")

        try:
            timelines = json.loads(args.input.timelines)
        except json.JSONDecodeError as e:
            raise ValueError(f"timelines JSON 解析失败: {e}")

        if not isinstance(texts, list):
            raise ValueError("texts 应为 JSON 数组")
        if not isinstance(timelines, list):
            raise ValueError("timelines 应为 JSON 数组")
        if len(texts) != len(timelines):
            raise ValueError(
                f"texts 数量 ({len(texts)}) 与 timelines 数量 ({len(timelines)}) 不匹配"
            )

        # 解析可选关键词列表
        keywords_list: Optional[List[str]] = None
        if args.input.keywords:
            try:
                keywords_list = json.loads(args.input.keywords)
                if not isinstance(keywords_list, list):
                    keywords_list = None
            except json.JSONDecodeError:
                keywords_list = None

        infos = []
        for i, (text, tl) in enumerate(zip(texts, timelines)):
            # 支持内联关键词语法：文本||关键词
            keyword: Optional[str] = None
            actual_text = text
            if "||" in text:
                parts = text.split("||", 1)
                actual_text = parts[0].strip()
                keyword = parts[1].strip()

            # keywords 参数优先级高于内联语法
            if keywords_list is not None:
                keyword = keywords_list[i] if i < len(keywords_list) else ""

            info: Dict[str, Any] = {
                "start": int(tl["start"]),
                "end": int(tl["end"]),
                "text": actual_text,
            }

            # 关键词相关
            if keyword is not None:
                info["keyword"] = keyword
            if args.input.keyword_color is not None:
                info["keyword_color"] = args.input.keyword_color
            if args.input.keyword_font_size is not None:
                info["keyword_font_size"] = int(args.input.keyword_font_size)

            # 字体
            if args.input.font_size is not None:
                info["font_size"] = int(args.input.font_size)

            # 动画
            if args.input.in_animation:
                info["in_animation"] = args.input.in_animation
                if args.input.in_animation_duration is not None:
                    info["in_animation_duration"] = int(args.input.in_animation_duration)
            if args.input.loop_animation:
                info["loop_animation"] = args.input.loop_animation
                if args.input.loop_animation_duration is not None:
                    info["loop_animation_duration"] = int(args.input.loop_animation_duration)
            if args.input.out_animation:
                info["out_animation"] = args.input.out_animation
                if args.input.out_animation_duration is not None:
                    info["out_animation_duration"] = int(args.input.out_animation_duration)
            if args.input.transition:
                info["transition"] = args.input.transition
                if args.input.transition_duration is not None:
                    info["transition_duration"] = int(args.input.transition_duration)

            infos.append(info)

        result = json.dumps(infos, ensure_ascii=False)

        if logger:
            logger.info(f"caption_infos: 生成 {len(infos)} 条字幕信息")

        return Output(
            captions=result,
            success=True,
            message=f"已生成 {len(infos)} 条字幕信息",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"caption_infos 失败: {exc}")
        return Output(
            captions="[]",
            success=False,
            message=str(exc),
        )._asdict()
