"""
C 脚本：定义 Input/Output NamedTuple 类型
负责生成 Input 类（包含路径参数和 Request 模型字段）
"""

from typing import Any, Dict, List, Set

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class InputOutputGenerator:
    """C脚本：生成 Input/Output 类定义"""

    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor

    def generate_input_class(self, endpoint: APIEndpointInfo) -> str:
        """生成 Input 类（保持原始类型，不额外包装Optional）"""
        fields = []

        # 添加路径参数
        if endpoint.has_draft_id:
            fields.append("    draft_id: str")
        if endpoint.has_segment_id:
            fields.append("    segment_id: str")

        # 添加 request model 的字段
        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(
                endpoint.request_model
            )
            for field in request_fields:
                # 保持原始类型，不进行简化
                field_type = field["type"]
                default = field["default"]

                # 判断是否为必需字段（默认值为 Ellipsis）
                if default == "Ellipsis" or default == "...":
                    # 必需字段，不添加默认值
                    fields.append(f"    {field['name']}: {field_type}")
                else:
                    # 可选字段，保持原类型和默认值
                    fields.append(f"    {field['name']}: {field_type} = {default}")

        # 如果没有字段，添加一个占位符
        if not fields:
            fields.append("    pass  # 无输入参数")

        class_def = f"class Input(NamedTuple):\n"
        class_def += f'    """{endpoint.func_name} 工具的输入参数"""\n'
        class_def += "\n".join(fields)

        return class_def

    def get_output_fields(self, endpoint: APIEndpointInfo) -> List[Dict[str, Any]]:
        """获取 Output 字段"""
        if endpoint.response_model:
            # 获取所有字段
            all_fields = self.schema_extractor.get_schema_fields(
                endpoint.response_model
            )

            # 过滤掉不需要的字段
            # timestamp 字段对 Coze 工具没有实际用途，因为工具只需要知道操作是否成功
            excluded_fields = {"timestamp"}

            filtered_fields = [
                field for field in all_fields if field["name"] not in excluded_fields
            ]

            return filtered_fields
        return []

    def generate_output_class(
        self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]
    ) -> str:
        """生成 Output 类（保持原始类型）"""
        if not output_fields:
            # 如果没有输出字段，使用基本的 success 和 message
            output_fields = [
                {"name": "success", "type": "bool", "default": "False"},
                {"name": "message", "type": "str", "default": '""'},
            ]

        fields = []
        for field in output_fields:
            field_name = field["name"]
            field_type = field["type"]
            default = field.get("default", "None")

            # 处理默认值
            if default == "Ellipsis" or default == "...":
                # 必需字段需要设置合理的默认值（Output通常都有默认值）
                if "int" in field_type.lower():
                    default = "0"
                elif "str" in field_type.lower():
                    default = '""'
                elif "bool" in field_type.lower():
                    default = "False"
                elif "list" in field_type.lower():
                    default = "[]"
                else:
                    default = "None"

            # 保持原始类型，只为Output添加合理默认值
            if "Optional" not in field_type and default == "None":
                # 如果原本不是Optional且默认值是None，包装为Optional
                field_type = f"Optional[{field_type}]"

            fields.append(f"    {field_name}: {field_type} = {default}")

        class_def = f"class Output(NamedTuple):\n"
        class_def += f'    """{endpoint.func_name} 工具的输出参数"""\n'
        class_def += "\n".join(fields)

        return class_def

    def get_custom_types_from_input(self, endpoint: APIEndpointInfo) -> Set[str]:
        """获取Input类中使用的所有自定义类型"""
        custom_types = set()

        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(
                endpoint.request_model
            )
            custom_types.update(
                self.schema_extractor.get_all_custom_types_from_fields(request_fields)
            )

        return custom_types

    def get_custom_types_from_output(self, endpoint: APIEndpointInfo) -> Set[str]:
        """获取Output类中使用的所有自定义类型"""
        custom_types = set()

        if endpoint.response_model:
            response_fields = self.schema_extractor.get_schema_fields(
                endpoint.response_model
            )
            custom_types.update(
                self.schema_extractor.get_all_custom_types_from_fields(response_fields)
            )

        return custom_types

    def get_custom_types_from_input(self, endpoint: APIEndpointInfo) -> Set[str]:
        """获取Input类中使用的所有自定义类型"""
        custom_types = set()

        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(
                endpoint.request_model
            )
            custom_types.update(
                self.schema_extractor.get_all_custom_types_from_fields(request_fields)
            )

        return custom_types

    def get_custom_types_from_output(self, endpoint: APIEndpointInfo) -> Set[str]:
        """获取Output类中使用的所有自定义类型"""
        custom_types = set()

        if endpoint.response_model:
            response_fields = self.schema_extractor.get_schema_fields(
                endpoint.response_model
            )
            custom_types.update(
                self.schema_extractor.get_all_custom_types_from_fields(response_fields)
            )

        return custom_types
