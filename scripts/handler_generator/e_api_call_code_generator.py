"""
E 脚本：生成 coze2jianying.py 文件写入逻辑
负责生成 API 调用代码，将调用记录写入 /tmp/coze2jianying.py
"""

from typing import List, Dict, Any

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class APICallCodeGenerator:
    """E脚本：生成 API 调用记录代码"""
    
    def __init__(self, schema_extractor: SchemaExtractor):
        self.schema_extractor = schema_extractor
    
    def generate_api_call_code(self, endpoint: APIEndpointInfo, output_fields: List[Dict[str, Any]]) -> str:
        """生成 API 调用代码"""
        
        # 确定目标 ID 类型
        target_id_name = None
        if endpoint.has_draft_id:
            target_id_name = 'draft_id'
        elif endpoint.has_segment_id:
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
        
        api_call_code = f"""        # 生成 API 调用代码
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
        
        return api_call_code
