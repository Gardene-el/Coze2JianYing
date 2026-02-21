"""
生成关键帧信息 JSON 工具 (make_keyframes_infos)

纯计算工具——根据关键帧类型、百分比偏移量和值，
结合片段信息，生成 add_keyframes 所需的 JSON 字符串。

无网络请求，无文件 I/O。

关键帧类型（ctype）对照：
  - KFTypePositionX     水平位移（像素 → 归一化 /draft_w）
  - KFTypePositionY     垂直位移（像素 → 归一化 /draft_h）
  - KFTypeRotation      旋转（度，直接使用）
  - UNIFORM_SCALE       等比缩放（1.0 = 原始大小）
  - KFTypeAlpha         透明度（0.0–1.0）
  - KFTypeScaleX        X 轴缩放
  - KFTypeScaleY        Y 轴缩放

offsets 和 values 使用 "|" 分隔；segment_infos 为 JSON 数组字符串，
格式：[{"id": "...", "start": 微秒, "end": 微秒}, ...]
"""

import json
from typing import Dict, Any, List, NamedTuple, Optional

from runtime import Args


class Input(NamedTuple):
    """make_keyframes_infos 工具的输入参数"""
    # 关键帧类型
    ctype: str
    # 偏移量（0-100 百分比），用 "|" 分隔，如 "0|50|100"
    offsets: str
    # 对应 offsets 的值，用 "|" 分隔，如 "0|1|0"
    values: str
    # 片段信息 JSON 字符串：[{"id": "...", "start": int, "end": int}, ...]
    segment_infos: str
    # 草稿高度（像素），KFTypePositionY 归一化用，可选
    height: Optional[int] = None
    # 草稿宽度（像素），KFTypePositionX 归一化用，可选
    width: Optional[int] = None


class Output(NamedTuple):
    """make_keyframes_infos 工具的输出"""
    keyframes_infos: str    # add_keyframes 所需的 JSON 字符串
    success: bool
    message: str


# 需要按草稿尺寸归一化的类型
_NORMALIZE_X = {"KFTypePositionX"}
_NORMALIZE_Y = {"KFTypePositionY"}


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    为每个片段生成关键帧配置列表。

    每个 offset 百分比映射到片段时长内的绝对时间偏移（微秒），
    value 按类型做归一化处理。

    Returns:
        Output._asdict()  其中 keyframes_infos 是 JSON 字符串
    """
    logger = getattr(args, "logger", None)

    try:
        ctype = args.input.ctype.strip()
        if not ctype:
            raise ValueError("ctype 不能为空")

        # 解析偏移量百分比
        offsets_parts = [p.strip() for p in args.input.offsets.split("|") if p.strip()]
        values_parts = [p.strip() for p in args.input.values.split("|") if p.strip()]

        if len(offsets_parts) != len(values_parts):
            raise ValueError(
                f"offsets 数量 ({len(offsets_parts)}) 与 values 数量 ({len(values_parts)}) 不匹配"
            )
        if not offsets_parts:
            raise ValueError("offsets 不能为空")

        offset_pcts = [float(o) for o in offsets_parts]
        raw_values = [float(v) for v in values_parts]

        # 解析片段信息
        try:
            segs: List[Dict] = json.loads(args.input.segment_infos)
        except json.JSONDecodeError as e:
            raise ValueError(f"segment_infos JSON 解析失败: {e}")

        if not isinstance(segs, list) or not segs:
            raise ValueError("segment_infos 应为非空 JSON 数组")

        # 确定归一化基数
        draft_w = int(args.input.width) if args.input.width else 1920
        draft_h = int(args.input.height) if args.input.height else 1080

        all_kf: List[Dict[str, Any]] = []

        for seg in segs:
            seg_id = seg.get("id", "")
            seg_start = int(seg.get("start", 0))
            seg_end = int(seg.get("end", 0))
            seg_dur = max(seg_end - seg_start, 1)

            for pct, raw_val in zip(offset_pcts, raw_values):
                # 百分比 → 微秒偏移（相对片段起点）
                offset_us = int(seg_dur * pct / 100)

                # 按类型归一化
                if ctype in _NORMALIZE_X:
                    final_val = raw_val / draft_w
                elif ctype in _NORMALIZE_Y:
                    final_val = raw_val / draft_h
                else:
                    final_val = raw_val

                all_kf.append({
                    "segment_id": seg_id,
                    "property": ctype,
                    "offset": offset_us,
                    "value": final_val,
                })

        result_str = json.dumps(all_kf, ensure_ascii=False)

        if logger:
            logger.info(f"make_keyframes_infos: ctype={ctype}, {len(all_kf)} 个关键帧")

        return Output(
            keyframes_infos=result_str,
            success=True,
            message=f"已生成 {len(all_kf)} 个关键帧配置",
        )._asdict()

    except Exception as exc:
        if logger:
            logger.error(f"make_keyframes_infos 失败: {exc}")
        return Output(
            keyframes_infos="[]",
            success=False,
            message=str(exc),
        )._asdict()
