#!/usr/bin/env python3
"""
生成适配 Coze 平台的 OpenAPI 规范文件

该脚本从 FastAPI 应用生成的 OpenAPI schema 中提取关键端点，
并转换为 Coze 平台所需的格式，包括：
1. 添加完整的 examples 部分（ReqExample 和 RespExample）
2. 简化 operationId
3. 设置适当的服务器 URL（支持 ngrok）
4. 确保 OpenAPI 3.0.1 兼容性
"""

import sys
import os
import json
import yaml
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api_main import app


def get_example_for_schema(schema_ref: str, definitions: Dict[str, Any]) -> Dict[str, Any]:
    """从 schema 定义中提取示例数据"""
    if not schema_ref or not schema_ref.startswith('#/components/schemas/'):
        return {}
    
    schema_name = schema_ref.split('/')[-1]
    schema = definitions.get(schema_name, {})
    
    # 如果有 example，直接返回
    if 'example' in schema:
        return schema['example']
    
    # 如果有 examples，返回第一个
    if 'examples' in schema:
        examples = schema['examples']
        if isinstance(examples, dict) and examples:
            return list(examples.values())[0].get('value', {})
    
    # 从 properties 构建基本示例
    if 'properties' in schema:
        example = {}
        for prop_name, prop_def in schema['properties'].items():
            if 'example' in prop_def:
                example[prop_name] = prop_def['example']
            elif 'default' in prop_def:
                example[prop_name] = prop_def['default']
            elif prop_def.get('type') == 'string':
                example[prop_name] = prop_def.get('description', f'example_{prop_name}')
            elif prop_def.get('type') == 'integer':
                example[prop_name] = 0
            elif prop_def.get('type') == 'number':
                example[prop_name] = 0.0
            elif prop_def.get('type') == 'boolean':
                example[prop_name] = False
            elif prop_def.get('type') == 'array':
                example[prop_name] = []
            elif prop_def.get('type') == 'object':
                example[prop_name] = {}
        return example
    
    return {}


def simplify_operation_id(operation_id: str) -> str:
    """简化 operationId，使其更简洁"""
    # FastAPI 生成的 operationId 格式: create_audio_segment_api_segment_audio_create_post
    # 简化为: create_audio_segment
    parts = operation_id.split('_')
    
    # 查找 'api' 关键字位置
    try:
        api_index = parts.index('api')
        # 返回 'api' 之前的部分
        return '_'.join(parts[:api_index])
    except ValueError:
        # 如果没有 'api'，返回原始值
        return operation_id


def convert_schema_to_openapi_3_0(schema: Any) -> Any:
    """
    将 OpenAPI 3.1.0 schema 转换为 OpenAPI 3.0.1 兼容格式
    
    主要变化：
    1. exclusiveMinimum/exclusiveMaximum 从数值改为布尔值
    2. 使用 minimum/maximum + exclusiveMinimum/exclusiveMaximum(boolean)
    3. type: 'null' 转换为 nullable: true
    4. anyOf: [type: X, type: 'null'] 转换为 type: X, nullable: true
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
                    # 保留其他字段（如 title, description）
                    for key, value in schema.items():
                        if key not in ['anyOf'] and key not in converted:
                            converted[key] = convert_schema_to_openapi_3_0(value)
                    return converted
        
        # 处理单独的 type: 'null'（罕见情况）
        if schema.get('type') == 'null':
            # 在 OpenAPI 3.0.1 中，使用 nullable: true 而不是 type: 'null'
            # 但单独的 type: 'null' 比较特殊，通常不应该出现
            # 我们将其转换为一个空的 schema 并标记为 nullable
            return {'nullable': True}
        
        for key, value in schema.items():
            # 处理 exclusiveMinimum (OpenAPI 3.1: number, OpenAPI 3.0: boolean)
            if key == 'exclusiveMinimum' and isinstance(value, (int, float)):
                # 在 3.0.1 中，exclusiveMinimum 是布尔值，最小值用 minimum 表示
                converted['minimum'] = value
                converted['exclusiveMinimum'] = True
                continue
            
            # 处理 exclusiveMaximum (OpenAPI 3.1: number, OpenAPI 3.0: boolean)
            if key == 'exclusiveMaximum' and isinstance(value, (int, float)):
                # 在 3.0.1 中，exclusiveMaximum 是布尔值，最大值用 maximum 表示
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


def create_coze_openapi_spec(server_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    创建适配 Coze 平台的 OpenAPI 规范
    
    Args:
        server_url: 服务器 URL，默认为本地地址
    
    Returns:
        Coze 兼容的 OpenAPI 规范字典
    """
    # 获取原始 OpenAPI schema
    original_schema = app.openapi()
    
    # 转换所有 schemas 为 OpenAPI 3.0.1 格式
    original_schemas = original_schema.get('components', {}).get('schemas', {})
    converted_schemas = convert_schema_to_openapi_3_0(original_schemas)
    
    # 创建 Coze 格式的 schema
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
        'paths': {},
        'components': {
            'examples': {},
            'schemas': converted_schemas
        }
    }
    
    # 选择关键端点添加到 Coze schema
    key_endpoints = [
        '/api/draft/create',
        '/api/segment/audio/create',
        '/api/segment/video/create',
        '/api/segment/audio/{segment_id}/add_effect',
    ]
    
    definitions = original_schema.get('components', {}).get('schemas', {})
    
    for path, path_item in original_schema.get('paths', {}).items():
        # 只处理关键端点
        if path not in key_endpoints:
            continue
        
        coze_path_item = {}
        
        for method, operation in path_item.items():
            if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            # 简化 operationId
            original_op_id = operation.get('operationId', '')
            simplified_op_id = simplify_operation_id(original_op_id)
            
            # 获取请求和响应示例
            req_example = {}
            resp_example = {}
            
            # 从 requestBody 提取示例
            if 'requestBody' in operation:
                content = operation['requestBody'].get('content', {})
                json_content = content.get('application/json', {})
                if 'schema' in json_content:
                    schema_ref = json_content['schema'].get('$ref', '')
                    req_example = get_example_for_schema(schema_ref, definitions)
            
            # 从 responses 提取示例
            if 'responses' in operation:
                success_responses = [code for code in operation['responses'].keys() 
                                   if code.startswith('2')]
                if success_responses:
                    success_response = operation['responses'][success_responses[0]]
                    content = success_response.get('content', {})
                    json_content = content.get('application/json', {})
                    if 'schema' in json_content:
                        schema_ref = json_content['schema'].get('$ref', '')
                        resp_example = get_example_for_schema(schema_ref, definitions)
            
            # 添加到 components/examples
            if simplified_op_id:
                coze_schema['components']['examples'][simplified_op_id] = {
                    'value': {
                        'ReqExample': req_example,
                        'RespExample': resp_example
                    }
                }
            
            # 创建简化的 operation
            coze_operation = {
                'operationId': simplified_op_id,
                'summary': operation.get('summary', ''),
                'description': operation.get('description', ''),
                'requestBody': operation.get('requestBody'),
                'responses': operation.get('responses', {
                    'default': {'description': ''}
                }),
                'parameters': operation.get('parameters', [])
            }
            
            # 移除 422 验证错误响应（Coze 不需要）
            if '422' in coze_operation['responses']:
                del coze_operation['responses']['422']
            
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
        default='http://localhost:8000',
        help='API 服务器 URL（默认: http://localhost:8000）'
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
        # Coze 平台可能无法正确解析带锚点的 YAML
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
    print(f"  - 示例数量: {len(coze_schema['components']['examples'])}")
    print(f"  - Schema 数量: {len(coze_schema['components']['schemas'])}")
    
    print(f"\n💡 使用提示:")
    print(f"  1. 如需使用 ngrok，请先启动 API 服务: python start_api.py")
    print(f"  2. 获取 ngrok URL 后重新运行: python scripts/generate_coze_openapi.py --server-url https://your-ngrok-url.ngrok-free.app")
    print(f"  3. 将生成的 {output_path} 文件导入到 Coze 平台")


if __name__ == '__main__':
    main()
