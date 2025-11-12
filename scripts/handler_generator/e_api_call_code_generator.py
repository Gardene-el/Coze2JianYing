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
            params = []
            for field in request_fields:
                field_name = field['name']
                field_type = field.get('type', '')
                default = field.get('default', '...')
                
                # 判断字段是否必需（没有默认值）
                is_required = default in ('...', 'Ellipsis')
                
                # 对于有默认值的字段，只在值不是None时才传递
                if is_required:
                    # 必需字段：始终传递
                    # 对于TimeRange等自定义类型，需要特殊处理
                    if 'TimeRange' in field_type:
                        # TimeRange类型：生成构造器代码
                        params.append(
                            f"{field_name}={{TimeRange(**{{k: v for k, v in args.input.{field_name}._asdict().items()}}) if hasattr(args.input.{field_name}, '_asdict') else args.input.{field_name}}}"
                        )
                    else:
                        # 使用repr()函数调用来格式化值
                        # 在运行时f-string中，这会正确地将值转换为repr形式
                        params.append(f"{field_name}={{repr(args.input.{field_name})}}")
                else:
                    # 可选字段：只在值不为None时传递，避免覆盖默认值
                    # 使用条件表达式动态构建参数
                    params.append(
                        f"**({{{repr(field_name)}: repr(args.input.{field_name})}} if args.input.{field_name} is not None else {{}})"
                    )

            request_construction = f"""
# 构造 request 对象
req_{{generated_uuid}} = {endpoint.request_model}({", ".join(params)})
"""

        # 生成 API 调用代码
        api_call_params = []
        if target_id_name:
            # 使用变量引用：对于使用已有 ID 的函数，通过变量名引用之前创建的对象
            # 例如：segment_{args.input.segment_id} 引用之前创建的 segment
            object_type = target_id_name.replace(
                "_id", ""
            )  # draft_id -> draft, segment_id -> segment
            api_call_params.append(f"{object_type}_{{args.input.{target_id_name}}}")
        if endpoint.request_model:
            api_call_params.append(f"req_{{generated_uuid}}")

        api_call_code = f"""        # 生成 API 调用代码
        api_call = f\"\"\"
# API 调用: {endpoint.func_name}
# 时间: {{time.strftime('%Y-%m-%d %H:%M:%S')}}
"""

        if request_construction:
            api_call_code += request_construction

        if api_call_params:
            api_call_code += f"""
resp_{{generated_uuid}} = await {endpoint.func_name}({", ".join(api_call_params)})
"""
        else:
            api_call_code += f"""
resp_{{generated_uuid}} = await {endpoint.func_name}()
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
