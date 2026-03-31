"""
步骤 4：生成 coze2jianying.py 文件写入逻辑
负责生成 API 调用代码，将调用记录写入 /tmp/coze2jianying.py

重构说明：
  生成目标从 "构造 Request 对象" 简化为 "直接 kwargs 调用 service 函数"。
  service 函数为同步函数，不使用 await。
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor
from .shared import BASIC_TYPES, ID_REFERENCE_FIELDS


class APICallCodeGenerator:
    """步骤 4：生成 API 调用记录代码（直接 kwargs 调用 service 函数）"""

    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor

    # ── 类型判断工具 ──────────────────────────────────────────────

    @staticmethod
    def _should_quote_type(field_type: str) -> bool:
        """字段类型是否为字符串族（f-string 中需要引号包裹）。"""
        ft = field_type.strip()
        if ft == "str":
            return True
        return "[str]" in ft or ft.endswith("str")

    @staticmethod
    def _is_optional(field: Dict[str, Any]) -> bool:
        """字段是否可选（有默认值或类型包含 Optional）。"""
        if "Optional" in field["type"]:
            return True
        return field["default"] not in ("...", "Ellipsis")

    @staticmethod
    def _extract_type_name(field_type: str) -> str:
        """从类型字符串中提取最内层 PascalCase 类型名。"""
        matches = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", field_type.strip())
        return matches[-1] if matches else field_type

    def _is_complex_type(self, field_type: str) -> bool:
        """类型是否为自定义复杂类型（如 TimeRange, ClipSettings）。"""
        return self._extract_type_name(field_type) not in BASIC_TYPES

    @staticmethod
    def _is_id_reference(field_name: str, field_type: str) -> bool:
        """字段是否为 ID 引用（draft_id / segment_id）。"""
        if field_name not in ID_REFERENCE_FIELDS:
            return False
        ft = field_type.strip()
        return ft == "str" or "[str]" in ft or ft.endswith("str")

    # ── 值格式化 ──────────────────────────────────────────────────

    def _format_param_value(self, field_name: str, field_type: str) -> str:
        """格式化字段值（用于 handler.py 的 f-string 体内）。"""
        access = "args.input." + field_name

        if self._is_id_reference(field_name, field_type):
            prefix = field_name.replace("_id", "")
            return prefix + "_{" + access + "}"
        if self._should_quote_type(field_type):
            return '"{' + access + '}"'
        if self._is_complex_type(field_type):
            type_name = self._extract_type_name(field_type)
            return "{_to_type_constructor(" + access + ", '" + type_name + "')}"
        return "{" + access + "}"

    def _format_condition(self, field_name: str, field_type: str) -> str:
        """格式化可选字段的存在性检查条件。"""
        access = "args.input." + field_name
        if self._is_complex_type(field_type):
            return "{_is_meaningful_object(" + access + ")}"
        return "{" + access + "} is not None"

    # ── 核心生成方法 ──────────────────────────────────────────────

    def _classify_fields(
        self, endpoint: APIEndpointInfo
    ) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
        """将 request 模型字段分为 required / optional 两组。"""
        if not endpoint.request_model:
            return [], []
        fields = self.schema_extractor.get_schema_fields(endpoint.request_model)
        required, optional = [], []
        for f in fields:
            (optional if self._is_optional(f) else required).append(f)
        return required, optional

    def generate_api_call_code(
        self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]
    ) -> str:
        """生成 API 调用记录代码。

        生成的代码在 handler 运行时被求值为一段 Python 脚本字符串，
        最终通过 exec() 在用户本地执行。

        目标格式示例（单次 API 调用）::

            result_{uuid} = create_video_segment(
                material_url="xxx",
                target_timerange=TimeRange(start=0, duration=5000000),
            )
        """
        required_fields, optional_fields = self._classify_fields(endpoint)

        # ── 构造 f-string body（0 缩进，handler 运行时求值）──
        lines: list[str] = [
            "# API 调用: " + endpoint.func_name,
            "# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        # 收集函数调用参数
        call_args: list[str] = []

        # 路径参数（draft_id / segment_id → 引用之前创建的变量）
        if endpoint.has_draft_id:
            call_args.append("draft_{args.input.draft_id}")
        if endpoint.has_segment_id:
            call_args.append("segment_{args.input.segment_id}")

        # 必需的 request 字段
        for f in required_fields:
            val = self._format_param_value(f["name"], f["type"])
            call_args.append(f["name"] + "=" + val)

        # 可选 request 字段需要条件判断，不能直接放在参数列表中
        # 因此使用 dict + **kwargs 模式来处理
        has_optional = bool(optional_fields)

        if has_optional:
            lines.append("")
            lines.append("_optional_{generated_uuid} = {{}}")
            for f in optional_fields:
                cond = self._format_condition(f["name"], f["type"])
                val = self._format_param_value(f["name"], f["type"])
                lines.append("if " + cond + ":")
                lines.append(
                    "    _optional_{generated_uuid}['"
                    + f["name"]
                    + "'] = "
                    + val
                )

        # 构造函数调用
        lines.append("")

        # 判断返回值：创建型端点返回 ID，其他端点无返回值
        has_output_draft_id = any(f["name"] == "draft_id" for f in output_fields)
        has_output_segment_id = any(f["name"] == "segment_id" for f in output_fields)

        if has_output_draft_id:
            lhs = "draft_{generated_uuid}"
        elif has_output_segment_id:
            lhs = "segment_{generated_uuid}"
        else:
            lhs = None

        # 拼装调用行
        if has_optional:
            call_args.append("**_optional_{generated_uuid}")

        args_str = ", ".join(call_args)

        if lhs:
            lines.append(lhs + " = " + endpoint.func_name + "(" + args_str + ")")
        else:
            lines.append(endpoint.func_name + "(" + args_str + ")")

        # ── 包装为 handler 中的 f-string + 文件写入 ──
        I = "        "  # noqa: E741  8-space indent (inside handler try block)
        outer = [
            I + "# 生成 API 调用代码",
            I + 'api_call = f"""',
            "\n".join(lines),
            '"""',
            "",
            I + "# 写入 API 调用到文件",
            I + "coze_file = ensure_coze2jianying_file()",
            I + "append_api_call_to_file(coze_file, api_call)",
        ]
        return "\n".join(outer) + "\n"
