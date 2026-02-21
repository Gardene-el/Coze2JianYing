"""
生成特效信息列表 JSON 工具 (effect_infos)

纯计算工具——将特效名称列表与时间线合并，
生成 add_effects 工具所需的 effect_infos JSON 字符串。

无网络请求，无文件 I/O。
"""

import json
from typing import Dict, Any, NamedTuple

from runtime import Args


class Input(NamedTuple):
    """effect_infos 工具的输入参数"""
    # 特效名称数组，JSON 字符串，如 '["幻影","闪白"]'
    # 特效名称对应 pyJianYingDraft 中 VideoSceneEffectType 的成员名或显示名
    effects: str
    # 时间线 JSON 字符串，格式: '[{"start":0,"end":3000000},...]'
    timelines: str


class Output(NamedTuple):
    """effect_infos 工具的输出"""
    effect_infos: str   # add_effects 所需的 effect_infos JSON 字符串
    success: bool
    message: str


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    将特效名称列表与时间线逐一对应，
    生成 add_effects 所需的 JSON 字符串。
    """
    logger = getattr(args, "logger", None)

    try:
        try:
            effects = json.loads(args.input.effects)
        except json.JSONDecodeError as e:
            raise ValueError(f"effects JSON 解析失败: {e}")

        try:
            timelines = json.loads(args.input.timelines)
        except json.JSONDecodeError as e:
            raise ValueError(f"timelines JSON 解析失败: {e}")

        if not isinstance(effects, list):
            raise ValueError("effects 应为 JSON 数组")
        if not isinstance(timelines, list):
            raise ValueError("timelines 应为 JSON 数组")
        if len(effects) != len(timelines):
            raise ValueError(
                f"effects 数量 ({len(effects)}) 与 timelines 数量 ({len(timelines)}) 不匹配"
            )

        infos = []
        for effect_name, tl in zip(effects, timelines):
            infos.append({
                "effect_title": effect_name,
                "start": int(tl["start"]),
                "end": int(tl["end"]),
            })

        result = json.dumps(infos, ensure_ascii=False)

        if logger:
            logger.info(f"effect_infos: 生成 {len(infos)} 条特效信息")

        return Output(
            effect_infos=result,
            success=True,
            message=f"已生成 {len(infos)} 条特效信息",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"effect_infos 失败: {exc}")
        return Output(
            effect_infos="[]",
            success=False,
            message=str(exc),
        )._asdict()
