"""
F 脚本：扫描 segment_schemas.py 中的自定义类，为每个类生成 handler
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
    """F脚本：为自定义类生成 handler"""
    
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
并返回一个 {custom_class.class_name} 对象。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


{class_definition}


{input_class}


# Output 类型定义
class Output(NamedTuple):
    """{custom_class.tool_name} 工具的输出"""
    result: Optional[{custom_class.class_name}]  # {custom_class.class_name} 对象（错误时为 None）
    success: bool           # 操作成功状态
    message: str            # 状态消息


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
        
        # 生成字段处理代码 - 构建参数列表
        field_assignments = []
        for field in custom_class.fields:
            field_name = field['name']
            default = field.get('default', '...')
            
            # 如果输入为 None，使用默认值；否则使用输入值
            if default == '...' or default == 'Ellipsis':
                # 必需参数，如果 None 则抛出错误
                field_assignments.append(
                    f"        if args.input.{field_name} is None:\n"
                    f"            raise ValueError('{field_name} 是必需参数，必须提供')\n"
                    f"        {field_name} = args.input.{field_name}"
                )
            else:
                # 可选参数，如果 None 则使用默认值
                field_assignments.append(
                    f"        {field_name} = args.input.{field_name} if args.input.{field_name} is not None else {default}"
                )
        
        field_assignments_code = '\n'.join(field_assignments)
        
        # 生成构造函数参数列表
        constructor_params = ', '.join([f"{field['name']}={field['name']}" for field in custom_class.fields])
        
        handler = f'''def handler(args: Args[Input]) -> Output:
    """
    创建 {custom_class.class_name} 对象的主处理函数
    
    Args:
        args: 包含所有 {custom_class.class_name} 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 {custom_class.class_name} 对象的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating {custom_class.class_name} object")
    
    try:
        # 准备参数，使用提供的值或默认值
{field_assignments_code}
        
        # 创建 {custom_class.class_name} 对象
        result = {custom_class.class_name}({constructor_params})
        
        if logger:
            logger.info(f"Successfully created {custom_class.class_name} object")
        
        return Output(
            result=result,
            success=True,
            message="{custom_class.class_name} 对象创建成功"
        )
        
    except ValueError as e:
        # 参数验证错误
        error_msg = f"参数错误: {{str(e)}}"
        if logger:
            logger.error(error_msg)
        
        # 返回 None 作为错误情况（Output 中 result 改为 Optional）
        return Output(
            result=None,
            success=False,
            message=error_msg
        )
    except Exception as e:
        error_msg = f"创建 {custom_class.class_name} 对象时发生错误: {{str(e)}}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result=None,
            success=False,
            message=error_msg
        )
'''
        return handler
    
    def generate_readme_content(self, custom_class: CustomClass) -> str:
        """生成 README.md 内容"""
        
        # 生成参数表格
        param_rows = []
        for field in custom_class.fields:
            field_name = field['name']
            field_type = field['type']
            description = field.get('description', '')
            default = field.get('default', 'None')
            
            param_rows.append(f"| `{field_name}` | `{field_type}` | {description} | `{default}` |")
        
        param_table = '\n'.join(param_rows)
        
        # 生成使用示例
        example_params = []
        for i, field in enumerate(custom_class.fields[:3]):  # 只展示前3个参数作为示例
            field_name = field['name']
            field_type = field['type']
            
            # 根据类型生成示例值
            if 'int' in field_type.lower():
                example_value = "1000000"
            elif 'float' in field_type.lower():
                example_value = "0.5"
            elif 'bool' in field_type.lower():
                example_value = "true"
            elif 'List' in field_type:
                example_value = "[1.0, 0.5, 0.3]"
            else:
                example_value = '"value"'
            
            example_params.append(f'  "{field_name}": {example_value}')
        
        example_json = ',\n'.join(example_params)
        
        readme = f'''# {custom_class.tool_name}

## 功能描述

为 `{custom_class.class_name}` 类生成 Object 对象的辅助工具。

{custom_class.docstring}

此工具接收 {custom_class.class_name} 的所有参数（全部为可选），并返回一个 Object（字典）表示。
该对象可以在 Coze 工作流中传递给需要 {custom_class.class_name} 参数的其他工具。

## 输入参数

所有参数均为可选，仅在提供时才会包含在返回的对象中。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
{param_table}

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    result: Dict[str, Any]  # {custom_class.class_name} 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息
```

## 使用示例

### 在 Coze 工作流中使用

```json
{{
{example_json}
}}
```

### 返回示例

```json
{{
  "result": {{
{example_json}
  }},
  "success": true,
  "message": "{custom_class.class_name} 对象创建成功"
}}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 {custom_class.class_name} 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 {custom_class.class_name} 对象，使工作流更清晰
3. **参数复用**: 创建一个 {custom_class.class_name} 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数不会出现在返回的对象中
- 返回的 `result` 字段是一个标准的 JSON 对象（字典）
- 可以在 Coze 工作流的后续步骤中直接使用此对象
'''
        return readme
    
    def create_tool_folder(self, custom_class: CustomClass, output_dir: Path):
        """创建工具文件夹和文件"""
        tool_dir = output_dir / custom_class.tool_name
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成并写入 handler.py
        handler_content = self.generate_handler_content(custom_class)
        handler_file = tool_dir / "handler.py"
        with open(handler_file, 'w', encoding='utf-8') as f:
            f.write(handler_content)
        print(f"    生成 handler.py: {handler_file}")
        
        # 生成并写入 README.md
        readme_content = self.generate_readme_content(custom_class)
        readme_file = tool_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"    生成 README.md: {readme_file}")
