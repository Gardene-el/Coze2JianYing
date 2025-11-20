"""
E 脚本：生成 coze2jianying.py 文件写入逻辑
负责生成 API 调用代码，将调用记录写入 /tmp/coze2jianying.py
"""

from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class APICallCodeGenerator:
    """E脚本：生成 API 调用记录代码"""

    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor

    def _should_quote_type(self, field_type: str) -> bool:
        """
        判断字段类型是否需要在 f-string 中用引号包裹

        Args:
            field_type: 字段的类型字符串，如 "str", "int", "Optional[str]" 等

        Returns:
            True 如果需要引号（字符串类型），False 否则
        """
        # 去除空格
        field_type = field_type.strip()

        # 字符串类型需要引号
        if field_type == "str":
            return True

        # Optional[str], List[str] 等包含 str 的复杂类型也需要引号
        # 但要排除 "string" 等其他包含 str 的词
        if "str" in field_type and (
            "[str]" in field_type or field_type.endswith("str")
        ):
            return True

        # 其他类型（int, float, bool, List[int], Dict 等）不需要引号
        return False

    def _is_optional_field(self, field: Dict[str, Any]) -> bool:
        """
        判断字段是否为可选字段（可以不传递）

        Args:
            field: 字段信息字典，包含 name, type, default, description

        Returns:
            True 如果字段是可选的（有默认值或类型包含 Optional）
        """
        field_type = field["type"]
        field_default = field["default"]

        # 如果类型中包含 Optional，说明可以为 None
        if "Optional" in field_type:
            return True

        # 如果有默认值且不是 "..." 或 "Ellipsis"（Pydantic 的必需字段标记），说明是可选的
        # SchemaExtractor 会将 ... 转换为字符串 "..." 或 Ellipsis 对象的字符串表示
        if field_default not in ("...", "Ellipsis"):
            return True

        return False

    def _extract_type_name(self, field_type: str) -> str:
        """
        从类型字符串中提取核心类型名

        例如：
        - "TimeRange" -> "TimeRange"
        - "Optional[TimeRange]" -> "TimeRange"
        - "Optional[List[ClipSettings]]" -> "ClipSettings"
        - "List[str]" -> "str"

        Args:
            field_type: 字段类型字符串

        Returns:
            核心类型名
        """
        import re

        # 去除空格
        field_type = field_type.strip()

        # 使用正则表达式提取最内层的类型名
        # 匹配大写字母开头的类型名（自定义类型通常是 PascalCase）
        matches = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", field_type)

        if matches:
            # 返回最后一个匹配（最内层类型）
            # 例如 Optional[List[ClipSettings]] 会匹配 [Optional, List, ClipSettings]
            # 我们要返回 ClipSettings
            return matches[-1]

        return field_type

    def _is_complex_type(self, field_type: str) -> bool:
        """
        判断字段类型是否为复杂类型（需要类型构造）

        Args:
            field_type: 字段类型字符串

        Returns:
            True 如果是复杂类型（如 TimeRange, ClipSettings 等自定义类型）
        """
        # 提取核心类型名
        type_name = self._extract_type_name(field_type)

        # 基本类型不是复杂类型
        basic_types = {
            "str",
            "int",
            "float",
            "bool",
            "None",
            "Any",
            "List",
            "Dict",
            "Tuple",
            "Set",
            "Optional",
            "Union",
        }

        if type_name in basic_types:
            return False

        # 其他类型（如 TimeRange, ClipSettings 等）视为复杂类型
        # 在 Coze 中这些会是 CustomNamespace，需要转换为类型构造调用
        return True

    def _is_id_field(self, field_name: str, field_type: str) -> bool:
        """
        判断字段是否为 ID 引用字段（需要引用之前创建的对象）
        
        ID 字段的特征：
        1. 字段名是 draft_id 或 segment_id（这些是引用之前创建的对象）
        2. 字段类型是 str
        3. 这些字段在 handler 中应该引用之前创建的对象变量
        
        注意：其他以 _id 结尾的字段（如 effect_id, filter_id 等）通常是
        配置字符串或资源标识符，不是对象引用，因此不应被视为 ID 引用字段
        
        Args:
            field_name: 字段名称
            field_type: 字段类型
            
        Returns:
            True 如果是 ID 引用字段
        """
        # 字段必须是字符串类型
        if not self._should_quote_type(field_type):
            return False
        
        # 只有 draft_id 和 segment_id 是对象引用
        # 其他 *_id 字段（effect_id, filter_id, resource_id 等）是配置字符串
        if field_name in ("draft_id", "segment_id"):
            return True
        
        return False

    def _format_param_value(self, field_name: str, field_type: str) -> str:
        """
        根据字段类型格式化参数值

        Args:
            field_name: 字段名称
            field_type: 字段类型

        Returns:
            格式化后的参数值字符串（用于写入 handler.py 的 f-string 中）
        """
        # 构造访问表达式：args.input.field_name
        access_expr = "args.input." + field_name

        # 检查是否为 ID 引用字段
        if self._is_id_field(field_name, field_type):
            # ID 字段：引用之前创建的对象变量
            # 例如：segment_id -> segment_{args.input.segment_id}
            #      draft_id -> draft_{args.input.draft_id}
            object_type = field_name.replace("_id", "")  # segment_id -> segment
            return object_type + "_{" + access_expr + "}"
        elif self._should_quote_type(field_type):
            # 普通字符串类型：需要在 handler.py 的 f-string 中是 "{args.input.xxx}"
            # 使用单层大括号，这样在 handler 运行时会插值
            return '"{' + access_expr + '}"'
        elif self._is_complex_type(field_type):
            # 复杂类型（如 TimeRange, ClipSettings）：调用 _to_type_constructor 生成类型构造表达式
            # 例如：CustomNamespace(start=0, duration=5000000) -> TimeRange(start=0, duration=5000000)
            type_name = self._extract_type_name(field_type)
            return "{_to_type_constructor(" + access_expr + ", '" + type_name + "')}"
        else:
            # 非字符串的基本类型：需要在 handler.py 的 f-string 中是 {args.input.xxx}
            return "{" + access_expr + "}"

    def _format_condition_value(self, field_name: str, field_type: str) -> str:
        """
        根据字段类型格式化条件检查中的值
        用于生成 'if <value> is not None:' 中的 <value> 部分

        Args:
            field_name: 字段名称
            field_type: 字段类型

        Returns:
            格式化后的条件值字符串（用于 if 条件中）
        """
        # 构造访问表达式：args.input.field_name
        access_expr = "args.input." + field_name

        # 检查是否为 ID 引用字段
        if self._is_id_field(field_name, field_type):
            # ID 字段：在条件中检查原始 ID 值是否为 None
            # 不需要加引号，因为我们要检查的是输入的 ID 值本身
            return "{" + access_expr + "}"
        elif self._should_quote_type(field_type):
            # 普通字符串类型：在条件中也需要加引号，避免被解释为变量名
            # 例如：if "demo_coze" is not None（而不是 if demo_coze is not None）
            return '"{' + access_expr + '}"'
        elif self._is_complex_type(field_type):
            # 复杂类型（如 TimeRange, ClipSettings）：需要检查是否为空对象
            # 使用 _is_meaningful_object 辅助函数，避免 CustomNamespace() 空对象被视为有效值
            return "{_is_meaningful_object(" + access_expr + ")}"
        else:
            # 非字符串类型：直接使用插值表达式
            # 例如：if 1080 is not None, if True is not None
            return "{" + access_expr + "}"

    def generate_api_call_code(
        self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]
    ) -> str:
        """生成 API 调用代码"""

        # 确定目标 ID 类型
        target_id_name = None
        if endpoint.has_draft_id:
            target_id_name = "draft_id"
        elif endpoint.has_segment_id:
            target_id_name = "segment_id"

        # 生成 request 对象构造代码
        request_construction = ""
        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(
                endpoint.request_model
            )

            # 分离必需字段和可选字段
            required_fields = []
            optional_fields = []
            for field in request_fields:
                if self._is_optional_field(field):
                    optional_fields.append(field)
                else:
                    required_fields.append(field)

            # 构造 request 对象的代码
            request_construction = "\n# 构造 request 对象\n"
            request_construction += "req_params_{generated_uuid} = {{}}\n"

            # 必需字段直接添加到字典
            for field in required_fields:
                field_name = field["name"]
                field_type = field["type"]
                formatted_value = self._format_param_value(field_name, field_type)
                request_construction += (
                    "req_params_{generated_uuid}['"
                    + field_name
                    + "'] = "
                    + formatted_value
                    + "\n"
                )

            # 可选字段：仅在非 None 时添加
            for field in optional_fields:
                field_name = field["name"]
                field_type = field["type"]
                formatted_value = self._format_param_value(field_name, field_type)
                condition_value = self._format_condition_value(field_name, field_type)
                
                # 对于复杂类型，condition_value 已经是完整的布尔表达式
                # 对于其他类型，需要添加 'is not None' 检查
                if self._is_complex_type(field_type):
                    # 复杂类型：使用 _is_meaningful_object() 直接返回 bool
                    request_construction += "if " + condition_value + ":\n"
                else:
                    # 简单类型：需要 'is not None' 检查
                    request_construction += "if " + condition_value + " is not None:\n"
                
                request_construction += (
                    "    req_params_{generated_uuid}['"
                    + field_name
                    + "'] = "
                    + formatted_value
                    + "\n"
                )

            # 使用字典解包创建 request 对象
            request_construction += (
                "req_{generated_uuid} = "
                + endpoint.request_model
                + "(**req_params_{generated_uuid})\n"
            )

        # 生成 API 调用代码
        api_call_params = []
        if target_id_name:
            # 使用变量引用：对于使用已有 ID 的函数，通过变量名引用之前创建的对象
            # 例如：segment_{args.input.segment_id} 引用之前创建的 segment
            object_type = target_id_name.replace(
                "_id", ""
            )  # draft_id -> draft, segment_id -> segment
            api_call_params.append(object_type + "_{args.input." + target_id_name + "}")
        if endpoint.request_model:
            api_call_params.append("req_{generated_uuid}")

        # 构造完整的 API 调用代码
        # 使用字符串拼接，完全避免 f-string 和 .format() 的转义问题
        api_call_code = "        # 生成 API 调用代码\n"
        api_call_code += '        api_call = f"""\n'
        api_call_code += "# API 调用: " + endpoint.func_name + "\n"
        api_call_code += "# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"

        if request_construction:
            api_call_code += request_construction

        api_call_code += "\n"
        api_call_code += "resp_{generated_uuid} = await " + endpoint.func_name + "("
        api_call_code += ", ".join(api_call_params)
        api_call_code += ")\n"

        # 检查 output 中所有的 ID 字段并保存
        # 这些 ID 可以在后续的 API 调用中被引用
        # 支持的 ID 类型：draft_id, segment_id, effect_id, keyframe_id, animation_id, 
        # filter_id, mask_id, transition_id, bubble_id 等
        id_fields_to_extract = [
            "draft_id",
            "segment_id", 
            "effect_id",
            "keyframe_id",
            "animation_id",
            "filter_id",
            "mask_id",
            "transition_id",
            "bubble_id",
            "track_id",
        ]
        
        for id_field in id_fields_to_extract:
            has_output_id = any(f["name"] == id_field for f in output_fields)
            if has_output_id:
                # 保存为 {type}_{uuid} 格式
                # 例如：effect_{uuid}, keyframe_{uuid} 等
                # 这样后续函数可以通过这个变量名引用创建的对象
                id_type = id_field.replace("_id", "")  # draft_id -> draft, effect_id -> effect
                api_call_code += "\n"
                api_call_code += f"{id_type}_{{generated_uuid}} = resp_{{generated_uuid}}.{id_field}\n"

        api_call_code += '"""\n'
        api_call_code += "\n"
        api_call_code += "        # 写入 API 调用到文件\n"
        api_call_code += "        coze_file = ensure_coze2jianying_file()\n"
        api_call_code += "        append_api_call_to_file(coze_file, api_call)\n"

        return api_call_code
