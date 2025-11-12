"""
E 脚本：生成 coze2jianying.py 文件写入逻辑
负责生成 API 调用代码，将调用记录写入 /tmp/coze2jianying.py
"""

from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class APICallCodeGenerator:
    """E脚本：生成 API 调用记录代码"""

    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor

    def generate_api_call_code(
        self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]
    ) -> str:
        """生成 API 调用代码"""

        # 确定目标 ID 类型
        target_id_name = None
        if endpoint.has_draft_id:
            target_id_name = "draft_id"
        elif endpoint.has_segment_id:
            target_id_name = "segment_id"

        # 生成 request 对象构造代码
        request_construction = ""
        if endpoint.request_model:
            request_fields = self.schema_extractor.get_schema_fields(
                endpoint.request_model
            )
            
            # 生成动态参数构建逻辑
            params_building_code = []
            for field in request_fields:
                field_name = field['name']
                field_type = field.get('type', 'Any')
                default_value = field.get('default', '...')
                
                # 判断字段类型
                needs_quotes = self._field_needs_quotes(field_type)
                is_optional = 'Optional' in field_type
                is_complex_object = self._is_complex_object_type(field_type)
                
                # 为每个字段生成条件添加逻辑
                if needs_quotes:
                    # 字符串类型：使用 json.dumps 获得双引号，并处理None
                    if is_optional or default_value != '...':
                        params_building_code.append(f"""
        if args.input.{field_name} is not None:
            param_str = f'{field_name}={{{{json.dumps(args.input.{field_name})}}}}'
            params.append(param_str)""")
                    else:
                        # 必需字符串字段
                        params_building_code.append(f"""
        param_str = f'{field_name}={{{{json.dumps(args.input.{field_name})}}}}'
        params.append(param_str)""")
                        
                elif is_complex_object:
                    # 复杂对象（如TimeRange）：转换CustomNamespace并生成构造调用
                    base_type = self._extract_base_type(field_type)
                    if is_optional or default_value != '...':
                        params_building_code.append(f"""
        if args.input.{field_name} is not None:
            # 转换 CustomNamespace 为 {base_type}
            obj = args.input.{field_name}
            if hasattr(obj, '__dict__'):
                obj_params = ', '.join(f'{{{{k}}}}={{{{v}}}}' for k, v in vars(obj).items())
                param_str = f'{field_name}={base_type}({{{{obj_params}}}})' 
            else:
                param_str = f'{field_name}={{{{str(obj)}}}}'
            params.append(param_str)""")
                    else:
                        # 必需复杂对象
                        params_building_code.append(f"""
        obj = args.input.{field_name}
        if hasattr(obj, '__dict__'):
            obj_params = ', '.join(f'{{{{k}}}}={{{{v}}}}' for k, v in vars(obj).items())
            param_str = f'{field_name}={base_type}({{{{obj_params}}}})' 
        else:
            param_str = f'{field_name}={{{{str(obj)}}}}'
        params.append(param_str)""")
                        
                else:
                    # 基本类型（int, float, bool）
                    if is_optional or default_value != '...':
                        params_building_code.append(f"""
        if args.input.{field_name} is not None:
            param_str = f'{field_name}={{{{args.input.{field_name}}}}}'
            params.append(param_str)""")
                    else:
                        # 必需基本类型
                        params_building_code.append(f"""
        param_str = f'{field_name}={{{{args.input.{field_name}}}}}'
        params.append(param_str)""")

            request_construction = f"""
        # 构造 request 对象参数列表
        params = []{"".join(params_building_code)}
        
        # 生成 request 构造代码
        params_str = ', '.join(params)
"""

        # 生成 API 调用代码
        api_call_params = []
        if target_id_name:
            # 使用变量引用：对于使用已有 ID 的函数，通过变量名引用之前创建的对象
            # 例如：segment_{args.input.segment_id} 引用之前创建的 segment
            object_type = target_id_name.replace(
                "_id", ""
            )  # draft_id -> draft, segment_id -> segment
            api_call_params.append(f"{object_type}_{{{{args.input.{target_id_name}}}}}")
        if endpoint.request_model:
            api_call_params.append(f"req_{{{{generated_uuid}}}}")

        api_call_code = f"""        # 生成 API 调用代码
        api_call = f\"\"\"
# API 调用: {endpoint.func_name}
# 时间: {{{{time.strftime('%Y-%m-%d %H:%M:%S')}}}}
"""

        if request_construction:
            api_call_code += request_construction
            api_call_code += f"""
# 构造 request 对象
req_{{{{generated_uuid}}}} = {endpoint.request_model}({{{{params_str}}}})
"""

        if api_call_params:
            api_call_code += f"""
resp_{{{{generated_uuid}}}} = await {endpoint.func_name}({", ".join(api_call_params)})
"""
        else:
            api_call_code += f"""
resp_{{{{generated_uuid}}}} = await {endpoint.func_name}()
"""

        # 检查 output 是否包含 draft_id 或 segment_id
        # 如果是 create 类型的函数，需要保存创建的对象ID以便后续引用
        has_output_draft_id = any(f["name"] == "draft_id" for f in output_fields)
        has_output_segment_id = any(f["name"] == "segment_id" for f in output_fields)

        if has_output_draft_id:
            # 保存为 draft_{uuid} 而不是 draft_id_{uuid}
            # 这样后续函数可以通过 draft_{uuid} 引用这个草稿
            api_call_code += f"""
draft_{{generated_uuid}} = resp_{{generated_uuid}}.draft_id
"""
        if has_output_segment_id:
            # 保存为 segment_{uuid} 而不是 segment_id_{uuid}
            # 这样后续函数可以通过 segment_{uuid} 引用这个片段
            api_call_code += f"""
segment_{{generated_uuid}} = resp_{{generated_uuid}}.segment_id
"""

        api_call_code += """\"\"\"

        # 写入 API 调用到文件
        coze_file = ensure_coze2jianying_file()
        append_api_call_to_file(coze_file, api_call)
"""

        return api_call_code
    
    def _field_needs_quotes(self, field_type: str) -> bool:
        """
        判断字段类型是否需要在生成的代码中使用引号
        
        Args:
            field_type: 字段类型字符串，如 "str", "int", "Optional[str]", "TimeRange" 等
            
        Returns:
            True 如果需要引号，False 否则
        """
        # 基本类型中只有 str 需要引号
        # 数字类型 (int, float) 和布尔类型 (bool) 不需要引号
        # None 不需要引号
        # 自定义类型（如 TimeRange, ClipSettings）也不需要引号，因为它们是对象构造
        
        # 如果类型包含 "str"，则需要引号
        # 这包括 "str", "Optional[str]", "List[str]" 等
        if 'str' in field_type:
            return True
        
        # 其他类型不需要引号
        return False
    
    def _is_complex_object_type(self, field_type: str) -> bool:
        """
        判断字段类型是否是复杂对象类型（需要从CustomNamespace转换）
        
        Args:
            field_type: 字段类型字符串
            
        Returns:
            True 如果是复杂对象类型，False 否则
        """
        # 基本类型和常见泛型
        basic_types = {'str', 'int', 'float', 'bool', 'Any', 'None', 'Dict', 'List'}
        
        # 提取类型名称（去除Optional等包装）
        import re
        type_names = re.findall(r'\b([A-Z][a-zA-Z0-9_]*)\b', field_type)
        
        # 如果有非基本类型的大写开头类型，则认为是复杂对象
        for type_name in type_names:
            if type_name not in basic_types and type_name != 'Optional':
                return True
        
        return False
    
    def _extract_base_type(self, field_type: str) -> str:
        """
        从类型字符串中提取基础类型名
        
        Args:
            field_type: 类型字符串，如 "TimeRange", "Optional[TimeRange]"
            
        Returns:
            基础类型名，如 "TimeRange"
        """
        import re
        # 提取所有大写开头的类型名
        type_names = re.findall(r'\b([A-Z][a-zA-Z0-9_]*)\b', field_type)
        
        # 过滤掉 Optional 等泛型包装器
        basic_wrappers = {'Optional', 'List', 'Dict', 'Union', 'Tuple'}
        for type_name in type_names:
            if type_name not in basic_wrappers:
                return type_name
        
        return 'Any'
