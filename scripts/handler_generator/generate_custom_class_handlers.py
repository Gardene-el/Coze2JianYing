"""
附加流程：扫描 segment_schemas.py 中的自定义类，为每个类生成 handler
负责识别自定义类（TimeRange, ClipSettings, TextStyle, CropSettings）
并生成对应的 make_<class_name> handler 工具
"""

import ast
from pathlib import Path
from typing import List, Dict, Any
from .schema_extractor import SchemaExtractor


class CustomClass:
    """自定义类信息"""

    def __init__(self, class_name: str, fields: List[Dict[str, Any]], docstring: str = ""):
        self.class_name = class_name
        self.fields = fields
        self.docstring = docstring
        self.tool_name = f"make_{self._to_snake_case(class_name)}"

    def _to_snake_case(self, name: str) -> str:
        """将类名转换为 snake_case"""
        import re
        # 在大写字母前插入下划线（除了首字母）
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # 在小写字母和大写字母之间插入下划线
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()


class CustomClassHandlerGenerator:
    """附加流程：为自定义类生成 handler"""

    # 需要生成 handler 的自定义类列表
    TARGET_CLASSES = ['TimeRange', 'ClipSettings', 'TextStyle', 'CropSettings']

    def __init__(self, schema_file: str, schema_extractor: SchemaExtractor):
        self.schema_file = Path(schema_file)
        self.schema_extractor = schema_extractor
        self.custom_classes: List[CustomClass] = []

    def scan_custom_classes(self) -> List[CustomClass]:
        """扫描 segment_schemas.py 中的自定义类"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            # 遍历 AST 查找目标类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name in self.TARGET_CLASSES:
                        # 提取类的字段信息
                        fields = self.schema_extractor.get_schema_fields(node.name)
                        docstring = ast.get_docstring(node) or ""

                        custom_class = CustomClass(
                            class_name=node.name,
                            fields=fields,
                            docstring=docstring
                        )
                        self.custom_classes.append(custom_class)
                        print(f"  找到自定义类: {node.name} ({len(fields)} 个字段)")

        except Exception as e:
            print(f"警告: 扫描自定义类时出错: {e}")

        return self.custom_classes

    def generate_handler_content(self, custom_class: CustomClass) -> str:
        """生成 handler.py 的完整内容"""

        # 生成 Input 类
        input_class = self._generate_input_class(custom_class)

        # 生成自定义类的定义
        class_definition = self._generate_class_definition(custom_class)

        # 生成 handler 函数
        handler_func = self._generate_handler_function(custom_class)

        content = f'''"""
{custom_class.tool_name} 工具处理器

为 {custom_class.class_name} 类生成对象
{custom_class.docstring}

此工具接收 {custom_class.class_name} 的所有参数（可选，使用原始默认值），
并返回一个包含 {custom_class.class_name} 数据的字典。

注意：handler 直接返回 Dict[str, Any]，而不是 NamedTuple，
以确保在 Coze 平台中正确的 JSON 对象序列化。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


{class_definition}


{input_class}


{handler_func}
'''
        return content

    def _generate_class_definition(self, custom_class: CustomClass) -> str:
        """生成自定义类的定义（NamedTuple形式）"""
        lines = [
            f"# {custom_class.class_name} 类型定义",
            f"class {custom_class.class_name}(NamedTuple):",
            f'    """{custom_class.docstring}"""'
        ]

        for field in custom_class.fields:
            field_name = field['name']
            field_type = field['type']
            description = field.get('description', '')

            # 构建字段定义行（不设置默认值，让类使用原始定义）
            if description:
                lines.append(f"    {field_name}: {field_type}  # {description}")
            else:
                lines.append(f"    {field_name}: {field_type}")

        return '\n'.join(lines)

    def _generate_input_class(self, custom_class: CustomClass) -> str:
        """生成 Input 类定义"""
        lines = [
            "# Input 类型定义",
            "class Input(NamedTuple):",
            f'    """{custom_class.tool_name} 工具的输入参数（可选，有默认值的参数使用原始默认值）"""'
        ]

        for field in custom_class.fields:
            field_name = field['name']
            field_type = field['type']
            description = field.get('description', '')
            default = field.get('default', '...')

            # 处理类型，确保所有参数都是可选的
            if not field_type.startswith('Optional'):
                # 如果不是 Optional，则包装为 Optional
                field_type = f"Optional[{field_type}]"

            # 使用原始默认值，如果是 ... 则表示无默认值（必需参数），在Input中设为None
            if default == '...' or default == 'Ellipsis':
                # 对于必需参数，在Input中设为 None 使其可选
                default_value = "None"
            else:
                # 保留原始默认值
                default_value = default

            # 构建字段定义行
            if description:
                lines.append(f"    {field_name}: {field_type} = {default_value}  # {description}")
            else:
                lines.append(f"    {field_name}: {field_type} = {default_value}")

        return '\n'.join(lines)

    def _generate_handler_function(self, custom_class: CustomClass) -> str:
        """生成 handler 函数"""

        # 生成字段处理代码 - 准备参数
        field_assignments = []
        constructor_params = []

        for field in custom_class.fields:
            field_name = field['name']
            default = field.get('default', '...')

            # 为每个字段准备参数值
            if default == '...' or default == 'Ellipsis':
                # 无默认值的参数：检查是否为 None，如果是则返回 None 结果
                field_assignments.append(
                    f"        if args.input.{field_name} is None:\n"
                    f"            # {field_name} 是必需参数但未提供，返回 None\n"
                    f"            if logger:\n"
                    f"                logger.warning(f'{field_name} 未提供，返回 None')\n"
                    f"            return {{\n"
                    f"                'result': None,\n"
                    f"                'success': True,\n"
                    f"                'message': '{custom_class.class_name} 对象创建成功（参数不完整）'\n"
                    f"            }}\n"
                    f"        {field_name} = args.input.{field_name}"
                )
            else:
                # 有默认值的参数：如果 None 则使用默认值
                field_assignments.append(
                    f"        {field_name} = args.input.{field_name} if args.input.{field_name} is not None else {default}"
                )

            constructor_params.append(f"{field_name}={field_name}")

        field_assignments_str = "\n".join(field_assignments)
        constructor_params_str = ", ".join(constructor_params)

        handler_func = f'''def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    {custom_class.tool_name} 的主处理函数

    Args:
        args: Input arguments

    Returns:
        Output data
    """
    try:
        logger = getattr(args, 'logger', None)

{field_assignments_str}

        result = {custom_class.class_name}({constructor_params_str})

        return {{
            'result': result._asdict(),
            'success': True,
            'message': '{custom_class.class_name} 对象创建成功'
        }}

    except Exception as e:
        if logger:
            logger.error(f"{custom_class.class_name} 创建失败: {{e}}")
        return {{
            'result': None,
            'success': False,
            'message': str(e)
        }}
'''

        return handler_func

    def _generate_readme_content(self, custom_class: CustomClass) -> str:
        """生成工具 README 内容"""
        fields = "\n".join(
            [f"- `{field['name']}`: `{field['type']}`" for field in custom_class.fields]
        )
        return f"""# {custom_class.tool_name}

## 功能

构造 `{custom_class.class_name}` 对象并返回字典结果。

## 输入参数

{fields}

## 输出

- `result`: `{custom_class.class_name}` 对象的字典表示
- `success`: 是否成功
- `message`: 处理消息
"""

    def create_tool_folder(self, custom_class: CustomClass, output_dir: Path) -> None:
        """创建工具目录并写入 handler.py / README.md"""
        tool_dir = output_dir / custom_class.tool_name
        tool_dir.mkdir(parents=True, exist_ok=True)

        handler_content = self.generate_handler_content(custom_class)
        readme_content = self._generate_readme_content(custom_class)

        with open(tool_dir / "handler.py", "w", encoding="utf-8") as f:
            f.write(handler_content)

        with open(tool_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
