"""
Schema Extractor - 辅助模块
用于从 Pydantic schema 文件中提取类字段信息
供 C/D/E 脚本使用
"""

import ast
from pathlib import Path
from typing import Any, Dict, List


class SchemaExtractor:
    """提取 Pydantic Schema 的字段信息"""

    def __init__(self, schema_file: str):
        self.schema_file = Path(schema_file)
        self.schemas = {}
        self._load_schemas()

    def _load_schemas(self):
        """加载 schema 文件内容"""
        try:
            with open(self.schema_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            # 查找所有类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    fields = self._extract_class_fields(node)
                    self.schemas[node.name] = fields

        except Exception as e:
            print(f"警告: 加载 schema 文件时出错: {e}")

    def _extract_class_fields(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """提取类的字段信息"""
        fields = []

        for item in class_node.body:
            if isinstance(item, ast.AnnAssign):
                # 这是一个带类型注解的赋值
                field_name = (
                    item.target.id if isinstance(item.target, ast.Name) else None
                )
                if field_name:
                    field_type = self._get_type_string(item.annotation)
                    default_value = self._get_default_value(item.value)

                    # 提取 Field 的描述
                    description = ""
                    if isinstance(item.value, ast.Call):
                        if (
                            isinstance(item.value.func, ast.Name)
                            and item.value.func.id == "Field"
                        ):
                            for keyword in item.value.keywords:
                                if keyword.arg == "description":
                                    if isinstance(keyword.value, ast.Constant):
                                        description = keyword.value.value

                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "default": default_value,
                            "description": description,
                        }
                    )

        return fields

    def _get_type_string(self, annotation) -> str:
        """获取类型注解的字符串表示"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # 处理 Optional[T], List[T], Optional[List[T]] 等泛型类型
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                # 递归处理内层类型
                if isinstance(annotation.slice, ast.Name):
                    # 简单类型: Optional[str], List[int]
                    inner_type = annotation.slice.id
                    return f"{base_type}[{inner_type}]"
                elif isinstance(annotation.slice, ast.Subscript):
                    # 嵌套泛型: Optional[List[float]], Dict[str, int]
                    inner_type = self._get_type_string(annotation.slice)
                    return f"{base_type}[{inner_type}]"
                else:
                    # 其他情况，尝试递归处理
                    inner_type = self._get_type_string(annotation.slice)
                    if inner_type and inner_type != "Any":
                        return f"{base_type}[{inner_type}]"
                return base_type
        return "Any"

    def get_class_source_code(self, class_name: str) -> str:
        """
        获取指定类的完整源代码定义（简化为NamedTuple形式）

        Args:
            class_name: 类名

        Returns:
            类的NamedTuple形式定义字符串，如果找不到返回空字符串
        """
        # 对于Coze插件，我们将Pydantic模型转换为简化的NamedTuple定义
        # 这样避免了对pydantic的依赖

        if class_name not in self.schemas:
            return ""

        fields = self.schemas[class_name]
        if not fields:
            return ""

        # 构建NamedTuple类定义
        field_lines = []
        for field in fields:
            field_name = field["name"]
            field_type = field["type"]
            default = field["default"]
            description = field.get("description", "")

            # 添加注释
            if description:
                field_lines.append(f"    {field_name}: {field_type}  # {description}")
            else:
                field_lines.append(f"    {field_name}: {field_type}")

        class_def = f"class {class_name}(NamedTuple):\n"
        class_def += f'    """{class_name}"""\n'
        class_def += "\n".join(field_lines)

        return class_def

    def get_multiple_class_sources(self, class_names: List[str]) -> str:
        """
        获取多个类的完整源代码定义

        Args:
            class_names: 类名列表

        Returns:
            所有类的源代码，用空行分隔
        """
        sources = []
        processed = set()  # 避免重复

        for class_name in class_names:
            if class_name in processed:
                continue
            processed.add(class_name)

            source = self.get_class_source_code(class_name)
            if source:
                sources.append(source)

        return "\n\n".join(sources) if sources else ""

    def _get_default_value(self, value_node) -> str:
        """获取默认值"""
        if value_node is None:
            return "..."
        elif isinstance(value_node, ast.Constant):
            if isinstance(value_node.value, str):
                return f'"{value_node.value}"'
            return str(value_node.value)
        elif isinstance(value_node, ast.List):
            # 处理列表默认值，如 [1.0, 1.0, 1.0]
            elements = []
            for elt in value_node.elts:
                if isinstance(elt, ast.Constant):
                    elements.append(str(elt.value))
            return f"[{', '.join(elements)}]"
        elif isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name) and value_node.func.id == "Field":
                # 从 Field() 提取默认值
                if value_node.args:
                    first_arg = value_node.args[0]
                    if isinstance(first_arg, ast.Constant):
                        val = first_arg.value
                        if isinstance(val, str):
                            return f'"{val}"'
                        return str(val)
                    elif isinstance(first_arg, ast.List):
                        # 处理 Field([1.0, 2.0, 3.0]) 这样的情况
                        elements = []
                        for elt in first_arg.elts:
                            if isinstance(elt, ast.Constant):
                                elements.append(str(elt.value))
                        return f"[{', '.join(elements)}]"
                return "..."
        return "..."

    def get_schema_fields(self, schema_name: str) -> List[Dict[str, Any]]:
        """获取指定 schema 的字段"""
        return self.schemas.get(schema_name, [])

    def extract_custom_types(self, type_string: str) -> List[str]:
        """
        从类型字符串中提取自定义类型（非基本类型）

        Args:
            type_string: 类型字符串，如 "Optional[TimeRange]", "List[ClipSettings]"

        Returns:
            自定义类型列表，如 ["TimeRange"], ["ClipSettings"]
        """
        basic_types = {
            "str",
            "int",
            "float",
            "bool",
            "Any",
            "None",
            "Dict",
            "List",
            "Optional",
            "Tuple",
            "Union",
        }
        custom_types = []

        # 移除泛型括号，提取所有类型名
        import re

        # 匹配所有标识符
        type_names = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", type_string)

        for type_name in type_names:
            if type_name not in basic_types and type_name not in custom_types:
                custom_types.append(type_name)

        return custom_types

    def get_all_custom_types_from_fields(
        self, fields: List[Dict[str, Any]]
    ) -> List[str]:
        """
        从字段列表中提取所有自定义类型

        Args:
            fields: 字段列表

        Returns:
            去重后的自定义类型列表
        """
        all_custom_types = []
        for field in fields:
            type_string = field.get("type", "")
            custom_types = self.extract_custom_types(type_string)
            for ct in custom_types:
                if ct not in all_custom_types:
                    all_custom_types.append(ct)

        return all_custom_types
