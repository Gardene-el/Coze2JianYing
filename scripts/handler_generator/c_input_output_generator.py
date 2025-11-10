"""
C 脚本：定义 Input/Output NamedTuple 类型
负责生成 Input 类（包含路径参数和 Request 模型字段）
"""

from typing import List, Dict, Any

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class InputOutputGenerator:
    """C脚本：生成 Input/Output 类定义"""
    
    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor
    
    def generate_input_class(self, endpoint: APIEndpointInfo) -> str:
        """生成 Input 类"""
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
    
    def get_output_fields(self, endpoint: APIEndpointInfo) -> List[Dict[str, Any]]:
        """获取 Output 字段"""
        if endpoint.response_model:
            return self.schema_extractor.get_schema_fields(endpoint.response_model)
        return []
