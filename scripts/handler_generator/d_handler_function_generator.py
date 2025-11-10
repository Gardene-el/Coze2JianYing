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
