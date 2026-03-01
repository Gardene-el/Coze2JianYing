#!/usr/bin/env python3
"""
生成适配 Coze 平台的 OpenAPI 规范文件 (重新设计版本)

根据用户要求：
1. 不生成 components/schemas
2. 不生成 components/examples (由 Coze 测试后自动生成)
3. 只生成 paths，schema 内联展开
4. 自动扫描 new_draft_routes.py 和 segment_routes.py 中的所有路由
"""

import sys
import os
import json
import yaml
from typing import Dict, Any, List, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.backend.api_main import app


def convert_schema_to_openapi_3_0(schema: Any) -> Any:
    """
    将 OpenAPI 3.1.0 schema 转换为 OpenAPI 3.0.1 兼容格式
    
    主要变化：
    1. exclusiveMinimum/exclusiveMaximum 从数值改为布尔值
    2. 使用 minimum/maximum + exclusiveMinimum/exclusiveMaximum(boolean)
    3. type: 'null' 转换为 nullable: true
    4. anyOf: [type: X, type: 'null'] 转换为 type: X, nullable: true
    5. 移除所有 title 字段（Coze 平台不支持，会导致解析错误）
    """
    if isinstance(schema, dict):
        converted = {}
        
        # 处理 anyOf 中的 null 类型（OpenAPI 3.1 -> 3.0.1）
        if 'anyOf' in schema:
            any_of_list = schema['anyOf']
            # 检查是否是 [type: X, type: 'null'] 模式
            if isinstance(any_of_list, list) and len(any_of_list) == 2:
                non_null = None
                has_null = False
                
                for item in any_of_list:
                    if isinstance(item, dict):
                        if item.get('type') == 'null':
                            has_null = True
                        else:
                            non_null = item
                
                # 如果是 [type: X, type: 'null'] 模式，转换为 type: X, nullable: true
                if has_null and non_null:
                    # 递归转换非 null 部分
                    converted = convert_schema_to_openapi_3_0(non_null)
                    if isinstance(converted, dict):
                        converted['nullable'] = True
                    # 保留其他字段（如 description），但跳过 title
                    for key, value in schema.items():
                        if key not in ['anyOf', 'title'] and key not in converted:
                            converted[key] = convert_schema_to_openapi_3_0(value)
                    return converted
        
        # 处理单独的 type: 'null'（罕见情况）
        if schema.get('type') == 'null':
            return {'nullable': True}
        
        for key, value in schema.items():
            # 跳过 title 字段（Coze 平台不支持，会导致解析错误）
            if key == 'title':
                continue
            
            # 处理 exclusiveMinimum (OpenAPI 3.1: number, OpenAPI 3.0: boolean)
            if key == 'exclusiveMinimum' and isinstance(value, (int, float)):
                converted['minimum'] = value
                converted['exclusiveMinimum'] = True
                continue
            
            # 处理 exclusiveMaximum (OpenAPI 3.1: number, OpenAPI 3.0: boolean)
            if key == 'exclusiveMaximum' and isinstance(value, (int, float)):
                converted['maximum'] = value
                converted['exclusiveMaximum'] = True
                continue
            
            # 递归处理嵌套的对象和数组
            converted[key] = convert_schema_to_openapi_3_0(value)
        
        return converted
    elif isinstance(schema, list):
        return [convert_schema_to_openapi_3_0(item) for item in schema]
    else:
        return schema


def resolve_schema_ref(schema: Dict[str, Any], definitions: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析并展开 schema 引用，将 $ref 替换为实际的 schema 定义
    """
    if not isinstance(schema, dict):
        return schema
    
    # 如果有 $ref，解析它
    if '$ref' in schema:
        ref_path = schema['$ref']
        if ref_path.startswith('#/components/schemas/'):
            schema_name = ref_path.split('/')[-1]
            if schema_name in definitions:
                # 递归解析引用的 schema
                resolved = resolve_schema_ref(definitions[schema_name].copy(), definitions)
                return resolved
        return schema
    
    # 递归处理所有嵌套的对象
    resolved = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            resolved[key] = resolve_schema_ref(value, definitions)
        elif isinstance(value, list):
            resolved[key] = [resolve_schema_ref(item, definitions) if isinstance(item, dict) else item for item in value]
        else:
            resolved[key] = value
    
    return resolved


def simplify_operation_id(operation_id: str) -> str:
    """简化 operationId"""
    parts = operation_id.split('_')
    try:
        api_index = parts.index('api')
        return '_'.join(parts[:api_index])
    except ValueError:
        return operation_id


def create_coze_openapi_spec(server_url: str = "http://localhost:20211") -> Dict[str, Any]:
    """
    创建适配 Coze 平台的 OpenAPI 规范
    
    根据用户要求：
    - 不包含 components/schemas
    - 不包含 components/examples  
    - 只包含 paths，schema 内联
    """
    # 获取原始 OpenAPI schema
    original_schema = app.openapi()
    
    # 创建 Coze 格式的 schema (只有基本信息和 paths)
    coze_schema = {
        'openapi': '3.0.1',  # Coze 要求 3.0.1
        'info': {
            'title': 'Coze2JianYing - 基于已有服务创建',
            'description': '提供云端服务，生成对应视频',
            'version': 'v1'
        },
        'servers': [
            {'url': server_url}
        ],
        'paths': {}
    }
    
    definitions = original_schema.get('components', {}).get('schemas', {})
    
    # 处理所有路径
    for path, path_item in original_schema.get('paths', {}).items():
        # 只处理 /api/draft/ 和 /api/segment/ 开头的路径
        if not (path.startswith('/api/draft/') or path.startswith('/api/segment/')):
            continue
        
        coze_path_item = {}
        
        for method, operation in path_item.items():
            if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            # 简化 operationId
            original_op_id = operation.get('operationId', '')
            simplified_op_id = simplify_operation_id(original_op_id)
            
            # 创建 operation
            coze_operation = {
                'operationId': simplified_op_id,
                'summary': operation.get('summary', ''),
                'description': operation.get('description', ''),
            }
            
            # 处理 parameters (路径参数等)
            if 'parameters' in operation:
                params = []
                for param in operation['parameters']:
                    param_copy = param.copy()
                    # 解析 schema 中的引用
                    if 'schema' in param_copy:
                        param_copy['schema'] = resolve_schema_ref(param_copy['schema'], definitions)
                        # 转换为 OpenAPI 3.0.1
                        param_copy['schema'] = convert_schema_to_openapi_3_0(param_copy['schema'])
                    params.append(param_copy)
                coze_operation['parameters'] = params
            
            # 处理 requestBody
            if 'requestBody' in operation:
                request_body = operation['requestBody'].copy()
                if 'content' in request_body:
                    content_copy = {}
                    for content_type, content_data in request_body['content'].items():
                        content_data_copy = content_data.copy()
                        if 'schema' in content_data_copy:
                            # 解析并内联 schema
                            schema_resolved = resolve_schema_ref(content_data_copy['schema'], definitions)
                            # 转换为 OpenAPI 3.0.1
                            schema_converted = convert_schema_to_openapi_3_0(schema_resolved)
                            content_data_copy['schema'] = schema_converted
                        content_copy[content_type] = content_data_copy
                    request_body['content'] = content_copy
                coze_operation['requestBody'] = request_body
            
            # 处理 responses
            responses = {}
            for status_code, response in operation.get('responses', {}).items():
                # 跳过 422 验证错误
                if status_code == '422':
                    continue
                
                response_copy = response.copy()
                if 'content' in response_copy:
                    content_copy = {}
                    for content_type, content_data in response_copy['content'].items():
                        content_data_copy = content_data.copy()
                        if 'schema' in content_data_copy:
                            # 解析并内联 schema
                            schema_resolved = resolve_schema_ref(content_data_copy['schema'], definitions)
                            # 转换为 OpenAPI 3.0.1
                            schema_converted = convert_schema_to_openapi_3_0(schema_resolved)
                            content_data_copy['schema'] = schema_converted
                        content_copy[content_type] = content_data_copy
                    response_copy['content'] = content_copy
                responses[status_code] = response_copy
            
            # 如果没有响应，添加默认响应
            if not responses:
                responses['default'] = {'description': ''}
            
            coze_operation['responses'] = responses
            coze_path_item[method] = coze_operation
        
        if coze_path_item:
            coze_schema['paths'][path] = coze_path_item
    
    return coze_schema


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='生成适配 Coze 平台的 OpenAPI 规范文件'
    )
    parser.add_argument(
        '--server-url',
        default='http://localhost:20211',
        help='API 服务器 URL（默认: http://localhost:20211）'
    )
    parser.add_argument(
        '--output',
        default='coze_openapi.yaml',
        help='输出文件路径（默认: coze_openapi.yaml）'
    )
    parser.add_argument(
        '--format',
        choices=['yaml', 'json'],
        default='yaml',
        help='输出格式（默认: yaml）'
    )
    
    args = parser.parse_args()
    
    print(f"正在生成 Coze OpenAPI 规范...")
    print(f"服务器 URL: {args.server_url}")
    
    # 生成 Coze OpenAPI schema
    coze_schema = create_coze_openapi_spec(args.server_url)
    
    # 保存文件
    output_path = args.output
    if args.format == 'yaml':
        # 使用自定义 Dumper 禁用 YAML 锚点和别名
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(coze_schema, f, Dumper=NoAliasDumper,
                     allow_unicode=True, sort_keys=False, 
                     default_flow_style=False, indent=4)
        print(f"✅ YAML 文件已生成: {output_path}")
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(coze_schema, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON 文件已生成: {output_path}")
    
    # 统计信息
    print(f"\n📊 生成统计:")
    print(f"  - 端点数量: {len(coze_schema['paths'])}")
    print(f"  - 注意：components/examples 将由 Coze 测试后自动生成")
    
    print(f"\n💡 使用提示:")
    print(f"  1. 将生成的 {output_path} 文件导入到 Coze 平台")
    print(f"  2. 在 Coze 中测试各个端点")
    print(f"  3. Coze 会自动生成 examples")


if __name__ == '__main__':
    main()
