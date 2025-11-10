#!/usr/bin/env python3
"""
根据 API 生成 Coze Handler 脚本
基于 A-E 脚本逻辑，从 /app/api 中的 POST API 端点自动生成 Coze 插件 handler.py 文件

脚本功能：
A: 扫描 /app/api 下所有 POST API 函数
B: 在 coze_plugin/raw_tools 下创建对应工具文件夹和文件
C: 生成 Input/Output NamedTuple 类定义
D: 生成 handler 函数
E: 生成 coze2jianying.py 文件写入逻辑
"""

import os
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import importlib.util
import sys


class APIEndpointInfo:
    """存储 API 端点信息"""
    def __init__(self, func_name: str, path: str, has_draft_id: bool, has_segment_id: bool,
                 request_model: Optional[str], response_model: Optional[str],
                 path_params: List[str], source_file: str):
        self.func_name = func_name
        self.path = path
        self.has_draft_id = has_draft_id
        self.has_segment_id = has_segment_id
        self.request_model = request_model
        self.response_model = response_model
        self.path_params = path_params
        self.source_file = source_file


class APIScanner:
    """A脚本：扫描 /app/api 下所有 POST API 函数"""
    
    def __init__(self, api_dir: str):
        self.api_dir = Path(api_dir)
        self.endpoints: List[APIEndpointInfo] = []
    
    def scan_file(self, file_path: Path) -> List[APIEndpointInfo]:
        """扫描单个 Python 文件中的 POST API 端点"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # 遍历 AST 查找函数定义（包括 async 函数）
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 检查是否有 @router.post 装饰器
                    endpoint_info = self._extract_post_endpoint(node, file_path)
                    if endpoint_info:
                        endpoints.append(endpoint_info)
        
        except Exception as e:
            print(f"警告: 解析文件 {file_path} 时出错: {e}")
        
        return endpoints
    
    def _extract_post_endpoint(self, node: ast.FunctionDef, source_file: Path) -> Optional[APIEndpointInfo]:
        """从函数节点提取 POST 端点信息"""
        # 检查装饰器
        has_post_decorator = False
        endpoint_path = ""
        response_model = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # 检查是否是 router.post
                if (isinstance(decorator.func, ast.Attribute) and 
                    decorator.func.attr == 'post'):
                    has_post_decorator = True
                    
                    # 提取路径
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            endpoint_path = decorator.args[0].value
                    
                    # 提取 response_model
                    for keyword in decorator.keywords:
                        if keyword.arg == 'response_model':
                            if isinstance(keyword.value, ast.Name):
                                response_model = keyword.value.id
        
        if not has_post_decorator:
            return None
        
        # 分析函数参数
        func_name = node.name
        has_draft_id = False
        has_segment_id = False
        request_model = None
        path_params = []
        
        for arg in node.args.args:
            arg_name = arg.arg
            
            # 检查路径参数
            if arg_name == 'draft_id':
                has_draft_id = True
                path_params.append('draft_id')
            elif arg_name == 'segment_id':
                has_segment_id = True
                path_params.append('segment_id')
            elif arg_name == 'request':
                # 尝试获取类型注解
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        request_model = arg.annotation.id
        
        return APIEndpointInfo(
            func_name=func_name,
            path=endpoint_path,
            has_draft_id=has_draft_id,
            has_segment_id=has_segment_id,
            request_model=request_model,
            response_model=response_model,
            path_params=path_params,
            source_file=str(source_file)
        )
    
    def scan_all(self) -> List[APIEndpointInfo]:
        """扫描所有 API 文件"""
        api_files = list(self.api_dir.glob('*_routes.py'))
        
        for api_file in api_files:
            print(f"扫描文件: {api_file.name}")
            endpoints = self.scan_file(api_file)
            self.endpoints.extend(endpoints)
            print(f"  找到 {len(endpoints)} 个 POST 端点")
        
        print(f"\n总共找到 {len(self.endpoints)} 个 POST API 端点")
        return self.endpoints


class SchemaExtractor:
    """提取 Pydantic Schema 的字段信息"""
    
    def __init__(self, schema_file: str):
        self.schema_file = Path(schema_file)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载 schema 文件内容"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
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
                field_name = item.target.id if isinstance(item.target, ast.Name) else None
                if field_name:
                    field_type = self._get_type_string(item.annotation)
                    default_value = self._get_default_value(item.value)
                    
                    # 提取 Field 的描述
                    description = ""
                    if isinstance(item.value, ast.Call):
                        if (isinstance(item.value.func, ast.Name) and 
                            item.value.func.id == 'Field'):
                            for keyword in item.value.keywords:
                                if keyword.arg == 'description':
                                    if isinstance(keyword.value, ast.Constant):
                                        description = keyword.value.value
                    
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'default': default_value,
                        'description': description
                    })
        
        return fields
    
    def _get_type_string(self, annotation) -> str:
        """获取类型注解的字符串表示"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # 处理 Optional[T], List[T] 等
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    inner_type = annotation.slice.id
                    return f"{base_type}[{inner_type}]"
                return base_type
        return "Any"
    
    def _get_default_value(self, value_node) -> str:
        """获取默认值"""
        if value_node is None:
            return "..."
        elif isinstance(value_node, ast.Constant):
            if isinstance(value_node.value, str):
                return f'"{value_node.value}"'
            return str(value_node.value)
        elif isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name) and value_node.func.id == 'Field':
                # 从 Field() 提取默认值
                if value_node.args:
                    if isinstance(value_node.args[0], ast.Constant):
                        val = value_node.args[0].value
                        if isinstance(val, str):
                            return f'"{val}"'
                        return str(val)
                return "..."
        return "..."
    
    def get_schema_fields(self, schema_name: str) -> List[Dict[str, Any]]:
        """获取指定 schema 的字段"""
        return self.schemas.get(schema_name, [])


class HandlerGenerator:
    """B/C/D/E脚本：生成 handler.py 文件"""
    
    def __init__(self, output_dir: str, schema_extractor: SchemaExtractor):
        self.output_dir = Path(output_dir)
        self.schema_extractor = schema_extractor
    
    def generate_handler(self, endpoint: APIEndpointInfo) -> str:
        """为单个 API 端点生成 handler.py 内容"""
        
        # 生成 Input 类
        input_class = self._generate_input_class(endpoint)
        
        # 生成 Output 类（使用 Dict 返回类型）
        output_fields = self._get_output_fields(endpoint)
        
        # 生成 handler 函数
        handler_func = self._generate_handler_function(endpoint, output_fields)
        
        # 组合完整内容
        content = f'''"""
{endpoint.func_name} 工具处理器

自动从 API 端点生成: {endpoint.path}
源文件: {endpoint.source_file}
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args


# Input 类型定义
{input_class}


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def ensure_coze2jianying_file() -> str:
    """
    确保 /tmp 目录下存在 coze2jianying.py 文件
    
    Returns:
        coze2jianying.py 文件的完整路径
    """
    file_path = "/tmp/coze2jianying.py"
    
    if not os.path.exists(file_path):
        # 创建初始文件内容
        initial_content = """# Coze2JianYing API 调用记录
# 此文件由 Coze 工具自动生成和更新
# 记录所有通过 Coze 工具调用的 API 操作

import asyncio
from app.schemas.segment_schemas import *

# API 调用记录将追加在下方
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    
    return file_path


def append_api_call_to_file(file_path: str, api_call_code: str):
    """
    将 API 调用代码追加到 coze2jianying.py 文件
    
    Args:
        file_path: coze2jianying.py 文件路径
        api_call_code: 要追加的 API 调用代码
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\\n" + api_call_code + "\\n")


{handler_func}
'''
        return content
    
    def _generate_input_class(self, endpoint: APIEndpointInfo) -> str:
        """C脚本：生成 Input 类"""
        fields = []
        
        # 添加路径参数
        if endpoint.has_draft_id:
            fields.append('    draft_id: str')
        if endpoint.has_segment_id:
            fields.append('    segment_id: str')
        
        # 添加 request model 的字段
        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(endpoint.request_model)
            for field in request_fields:
                # 跳过复杂的嵌套类型，使用简化的类型
                field_type = field['type']
                if '[' in field_type:
                    # 简化泛型类型
                    if 'Optional' in field_type:
                        field_type = 'Optional[Any]'
                    elif 'List' in field_type:
                        field_type = 'List[Any]'
                    else:
                        field_type = 'Any'
                
                default = field['default']
                if default == '...':
                    # 必需字段
                    fields.append(f"    {field['name']}: {field_type}")
                else:
                    # 可选字段
                    if 'Optional' not in field_type:
                        field_type = f'Optional[{field_type}]'
                    fields.append(f"    {field['name']}: {field_type} = {default}")
        
        # 如果没有字段，添加一个占位符
        if not fields:
            fields.append('    pass  # 无输入参数')
        
        class_def = f"class Input(NamedTuple):\n"
        class_def += f'    """{endpoint.func_name} 工具的输入参数"""\n'
        class_def += '\n'.join(fields)
        
        return class_def
    
    def _get_output_fields(self, endpoint: APIEndpointInfo) -> List[Dict[str, Any]]:
        """获取 Output 字段"""
        if endpoint.response_model:
            return self.schema_extractor.get_schema_fields(endpoint.response_model)
        return []
    
    def _generate_handler_function(self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]) -> str:
        """D/E脚本：生成 handler 函数"""
        
        # 确定目标 ID 类型
        target_id_type = None
        target_id_name = None
        if endpoint.has_draft_id:
            target_id_type = 'draft_id'
            target_id_name = 'draft_id'
        elif endpoint.has_segment_id:
            target_id_type = 'segment_id'
            target_id_name = 'segment_id'
        
        # 生成 request 对象构造代码
        request_construction = ""
        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(endpoint.request_model)
            params = []
            for field in request_fields:
                params.append(f"{field['name']}=args.input.{field['name']}")
            
            request_construction = f"""
    # 构造 request 对象
    req_{{generated_uuid}} = {endpoint.request_model}({', '.join(params)})
"""
        
        # 生成 API 调用代码
        api_call_params = []
        if target_id_name:
            api_call_params.append(f"{target_id_name}_{{generated_uuid}}")
        if endpoint.request_model:
            api_call_params.append(f"req_{{generated_uuid}}")
        
        api_call_code = f"""
    # 生成 API 调用代码
    api_call = f\"\"\"
# API 调用: {endpoint.func_name}
# 时间: {{time.strftime('%Y-%m-%d %H:%M:%S')}}
"""
        
        if target_id_name:
            api_call_code += f"""
{target_id_name}_{{generated_uuid}} = "{{generated_uuid}}"
"""
        
        if request_construction:
            api_call_code += request_construction
        
        if api_call_params:
            api_call_code += f"""
resp_{{generated_uuid}} = await {endpoint.func_name}({', '.join(api_call_params)})
"""
        else:
            api_call_code += f"""
resp_{{generated_uuid}} = await {endpoint.func_name}()
"""
        
        # 检查 output 是否包含 draft_id 或 segment_id
        has_output_draft_id = any(f['name'] == 'draft_id' for f in output_fields)
        has_output_segment_id = any(f['name'] == 'segment_id' for f in output_fields)
        
        if has_output_draft_id:
            api_call_code += f"""
draft_id_{{generated_uuid}} = resp_{{generated_uuid}}.draft_id
"""
        if has_output_segment_id:
            api_call_code += f"""
segment_id_{{generated_uuid}} = resp_{{generated_uuid}}.segment_id
"""
        
        api_call_code += '''\"\"\"
    
    # 写入 API 调用到文件
    coze_file = ensure_coze2jianying_file()
    append_api_call_to_file(coze_file, api_call)
'''
        
        # 生成返回值
        return_values = []
        for field in output_fields:
            field_name = field['name']
            if field_name == 'draft_id' and target_id_type == 'draft_id':
                return_values.append(f'        "{field_name}": f"draft_{{generated_uuid}}"')
            elif field_name == 'segment_id' and target_id_type == 'segment_id':
                return_values.append(f'        "{field_name}": f"segment_{{generated_uuid}}"')
            elif field_name == 'draft_id':
                return_values.append(f'        "{field_name}": f"draft_{{generated_uuid}}"')
            elif field_name == 'segment_id':
                return_values.append(f'        "{field_name}": f"segment_{{generated_uuid}}"')
            elif field_name == 'success':
                return_values.append(f'        "{field_name}": True')
            elif field_name == 'message':
                return_values.append(f'        "{field_name}": "操作成功"')
            else:
                # 其他字段使用默认值
                default = field.get('default', 'None')
                if default == '...' or default == 'Ellipsis':
                    # 根据字段类型设置合理的默认值
                    field_type = field.get('type', 'Any')
                    if 'int' in field_type.lower():
                        default = '0'
                    elif 'str' in field_type.lower():
                        default = '""'
                    elif 'bool' in field_type.lower():
                        default = 'False'
                    elif 'list' in field_type.lower():
                        default = '[]'
                    elif 'dict' in field_type.lower():
                        default = '{}'
                    else:
                        default = 'None'
                return_values.append(f'        "{field_name}": {default}')
        
        if not return_values:
            return_values.append('        "success": True')
        
        return_dict = ",\n".join(return_values)
        
        handler_function = f'''def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    {endpoint.func_name} 的主处理函数
    
    Args:
        args: Input arguments
        
    Returns:
        Dict containing response data
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"调用 {endpoint.func_name}，参数: {{args.input}}")
    
    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4())
        
        if logger:
            logger.info(f"生成 UUID: {{generated_uuid}}")
{api_call_code}
        
        if logger:
            logger.info(f"{endpoint.func_name} 调用成功")
        
        return {{
{return_dict}
        }}
        
    except Exception as e:
        error_msg = f"调用 {endpoint.func_name} 时发生错误: {{str(e)}}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {{traceback.format_exc()}}")
        
        return {{
            "success": False,
            "message": error_msg
        }}
'''
        
        return handler_function
    
    def generate_readme(self, endpoint: APIEndpointInfo) -> str:
        """B脚本：生成 README.md"""
        return f"""# {endpoint.func_name}

## 功能描述
此工具对应 FastAPI 端点: `{endpoint.path}`

源文件: `{endpoint.source_file}`

## API 信息
- **函数名**: {endpoint.func_name}
- **路径**: {endpoint.path}
- **方法**: POST
- **Request Model**: {endpoint.request_model or '无'}
- **Response Model**: {endpoint.response_model or '无'}

## 路径参数
{self._format_path_params(endpoint)}

## 使用说明
此工具由脚本自动生成，用于在 Coze 平台中调用对应的 API 端点。

工具会：
1. 生成唯一的 UUID
2. 记录 API 调用到 `/tmp/coze2jianying.py` 文件
3. 返回包含 UUID 的响应

## 注意事项
- 此工具在 Coze 平台的沙盒环境中运行
- API 调用记录保存在 `/tmp/coze2jianying.py`
- UUID 用于关联和追踪不同的对象实例
"""
    
    def _format_path_params(self, endpoint: APIEndpointInfo) -> str:
        """格式化路径参数说明"""
        if not endpoint.path_params:
            return "无"
        
        params = []
        for param in endpoint.path_params:
            params.append(f"- `{param}`: {'草稿ID' if param == 'draft_id' else '片段ID'}")
        
        return '\n'.join(params)
    
    def create_tool_folder(self, endpoint: APIEndpointInfo):
        """B脚本：创建工具文件夹和文件"""
        tool_dir = self.output_dir / endpoint.func_name
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成 handler.py
        handler_content = self.generate_handler(endpoint)
        handler_file = tool_dir / 'handler.py'
        with open(handler_file, 'w', encoding='utf-8') as f:
            f.write(handler_content)
        
        print(f"  生成: {handler_file}")
        
        # 生成 README.md
        readme_content = self.generate_readme(endpoint)
        readme_file = tool_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  生成: {readme_file}")
        
        return tool_dir


def main():
    """主函数：执行完整的生成流程"""
    print("=" * 60)
    print("Coze Handler 生成器")
    print("根据 API 端点自动生成 Coze 工具 handler.py")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 定义路径
    api_dir = project_root / 'app' / 'api'
    schema_file = project_root / 'app' / 'schemas' / 'segment_schemas.py'
    output_dir = project_root / 'coze_plugin' / 'raw_tools'
    
    print(f"项目根目录: {project_root}")
    print(f"API 目录: {api_dir}")
    print(f"Schema 文件: {schema_file}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # A脚本：扫描 API 端点
    print("步骤 1: 扫描 API 端点...")
    scanner = APIScanner(str(api_dir))
    endpoints = scanner.scan_all()
    print()
    
    if not endpoints:
        print("未找到任何 POST API 端点")
        return
    
    # 加载 schema 信息
    print("步骤 2: 加载 Schema 信息...")
    schema_extractor = SchemaExtractor(str(schema_file))
    print(f"加载了 {len(schema_extractor.schemas)} 个 schema 定义")
    print()
    
    # 生成 handler 文件
    print("步骤 3: 生成 handler.py 文件...")
    generator = HandlerGenerator(str(output_dir), schema_extractor)
    
    generated_count = 0
    for endpoint in endpoints:
        print(f"\n处理端点: {endpoint.func_name}")
        try:
            generator.create_tool_folder(endpoint)
            generated_count += 1
        except Exception as e:
            print(f"  错误: 生成失败 - {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    print(f"生成完成！")
    print(f"成功生成 {generated_count}/{len(endpoints)} 个工具")
    print(f"输出目录: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
