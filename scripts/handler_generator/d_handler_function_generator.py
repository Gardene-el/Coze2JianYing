"""
D 脚本：生成 handler 函数
负责生成主 handler 函数的框架代码，包括 UUID 生成和错误处理
"""

from typing import List, Dict, Any

from .api_endpoint_info import APIEndpointInfo


class HandlerFunctionGenerator:
    """D脚本：生成 handler 函数"""
    
    def generate_handler_function(self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]], 
                                   api_call_code: str) -> str:
        """生成 handler 函数"""
        
        # 确定目标 ID 类型
        target_id_type = None
        if endpoint.has_draft_id:
            target_id_type = 'draft_id'
        elif endpoint.has_segment_id:
            target_id_type = 'segment_id'
        
        # 生成返回值
        return_values = []
        for field in output_fields:
            field_name = field['name']
            # 对于 draft_id 和 segment_id，返回纯 UUID
            # 这样在后续调用中可以通过 draft_{uuid} 或 segment_{uuid} 引用
            if field_name == 'draft_id' and target_id_type == 'draft_id':
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == 'segment_id' and target_id_type == 'segment_id':
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == 'draft_id':
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == 'segment_id':
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
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
            return_values.append('success=True')
            return_values.append('message="操作成功"')
        
        # 生成 Output() 构造调用，使用关键字参数
        output_params = []
        for val in return_values:
            # 将 "field": value 格式转换为 field=value 格式
            if '": ' in val:
                # 移除前导空格和引号
                val = val.strip()
                if val.startswith('"'):
                    # 格式: "field": value
                    parts = val.split('": ', 1)
                    field_name = parts[0].strip('"')
                    field_value = parts[1]
                    output_params.append(f"{field_name}={field_value}")
                else:
                    output_params.append(val)
            else:
                output_params.append(val)
        
        output_construction = ", ".join(output_params)
        
        handler_function = f'''def handler(args: Args[Input]) -> Output:
    """
    {endpoint.func_name} 的主处理函数
    
    Args:
        args: Input arguments
        
    Returns:
        Output NamedTuple containing response data
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
        
        return Output({output_construction})
        
    except Exception as e:
        error_msg = f"调用 {endpoint.func_name} 时发生错误: {{str(e)}}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {{traceback.format_exc()}}")
        
        return Output(success=False, message=error_msg)
'''
        
        return handler_function
