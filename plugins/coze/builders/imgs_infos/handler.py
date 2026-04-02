"""
生成图片信息列表 JSON 工具 (imgs_infos)

纯计算工具——将图片 URL 列表与时间线合并，
生成 add_images 工具所需的 image_infos JSON 字符串。

动画参数支持两种格式：
- 单值（所有图片相同）：如 "渐入"
- 管道分隔多值（每张图片不同）：如 "渐入|浮入|旋转入"
  数量不足时首图动画补齐，多于图片数时截取。

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, List, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """imgs_infos 工具的输入参数"""
    # 图片 URL 数组，JSON 字符串，如 '["url1","url2"]'
    imgs: str
    # 时间线 JSON 字符串，格式: '[{"start":0,"end":5000000},...]'
    timelines: str
    # 可选：图片高度（像素）
    height: Optional[int] = None
    # 可选：图片宽度（像素）
    width: Optional[int] = None
    # 可选：入场动画（单值或 | 分隔多值）
    in_animation: Optional[str] = None
    # 可选：入场动画时长（微秒）
    in_animation_duration: Optional[int] = None
    # 可选：循环动画（单值或 | 分隔多值）
    loop_animation: Optional[str] = None
    # 可选：循环动画时长（微秒）
    loop_animation_duration: Optional[int] = None
    # 可选：出场动画（单值或 | 分隔多值）
    out_animation: Optional[str] = None
    # 可选：出场动画时长（微秒）
    out_animation_duration: Optional[int] = None
    # 可选：转场类型（单值或 | 分隔多值）
    transition: Optional[str] = None
    # 可选：转场时长（微秒）
    transition_duration: Optional[int] = None


class Output(NamedTuple):
    """imgs_infos 工具的输出"""
    image_infos: str    # add_images 所需的 image_infos JSON 字符串
    success: bool
    message: str


def _parse_anim(param: Optional[str]) -> List[str]:
    """将 | 分隔的动画参数解析为列表；空值返回空列表。"""
    if not param:
        return []
    return [s.strip() for s in param.split("|") if s.strip()]


def _get_anim_val(values: List[str], idx: int) -> Optional[str]:
    """
    按索引取动画值：
    - 单值列表 → 对所有索引都返回该值
    - 多值列表 → 索引越界时返回 None（不添加该动画）
    """
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    return values[idx] if idx < len(values) else None


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将图片 URL 列表与时间线逐一对应，附加动画/转场参数，
    生成 add_images 所需的 JSON 字符串。
    """
    logger = getattr(args, "logger", None)

    try:
        try:
            imgs = json.loads(args.input.imgs)
        except json.JSONDecodeError as e:
            raise ValueError(f"imgs JSON 解析失败: {e}")

        try:
            timelines = json.loads(args.input.timelines)
        except json.JSONDecodeError as e:
            raise ValueError(f"timelines JSON 解析失败: {e}")

        if not isinstance(imgs, list):
            raise ValueError("imgs 应为 JSON 数组")
        if not isinstance(timelines, list):
            raise ValueError("timelines 应为 JSON 数组")
        if len(imgs) != len(timelines):
            raise ValueError(
                f"imgs 数量 ({len(imgs)}) 与 timelines 数量 ({len(timelines)}) 不匹配"
            )

        in_anims = _parse_anim(args.input.in_animation)
        out_anims = _parse_anim(args.input.out_animation)
        loop_anims = _parse_anim(args.input.loop_animation)
        trans_anims = _parse_anim(args.input.transition)

        infos = []
        for i, (img_url, tl) in enumerate(zip(imgs, timelines)):
            info: Dict[str, Any] = {
                "image_url": img_url,
                "start": int(tl["start"]),
                "end": int(tl["end"]),
            }
            if args.input.height is not None:
                info["height"] = int(args.input.height)
            if args.input.width is not None:
                info["width"] = int(args.input.width)

            # 动画：有值则写入
            v = _get_anim_val(in_anims, i)
            if v:
                info["in_animation"] = v
                if args.input.in_animation_duration is not None:
                    info["in_animation_duration"] = int(args.input.in_animation_duration)

            v = _get_anim_val(out_anims, i)
            if v:
                info["out_animation"] = v
                if args.input.out_animation_duration is not None:
                    info["out_animation_duration"] = int(args.input.out_animation_duration)

            v = _get_anim_val(loop_anims, i)
            if v:
                info["loop_animation"] = v
                if args.input.loop_animation_duration is not None:
                    info["loop_animation_duration"] = int(args.input.loop_animation_duration)

            v = _get_anim_val(trans_anims, i)
            if v:
                info["transition"] = v
                if args.input.transition_duration is not None:
                    info["transition_duration"] = int(args.input.transition_duration)

            infos.append(info)

        result = json.dumps(infos, ensure_ascii=False)

        if logger:
            logger.info(f"imgs_infos: 生成 {len(infos)} 条图片信息")

        return Output(
            image_infos=result,
            success=True,
            message=f"已生成 {len(infos)} 条图片信息",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"imgs_infos 失败: {exc}")
        return Output(
            image_infos="[]",
            success=False,
            message=str(exc),
        )._asdict()
