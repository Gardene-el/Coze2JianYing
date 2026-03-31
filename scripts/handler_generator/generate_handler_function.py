"""
步骤 5：生成 handler 函数
负责生成主 handler 函数的框架代码，包括 UUID 生成和错误处理
"""

from pathlib import Path
from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo
from .shared import ID_REFERENCE_FIELDS, infer_default_for_type

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


class HandlerFunctionGenerator:
    """步骤 5：生成 handler 函数"""

    def generate_handler_function(
        self,
        endpoint: APIEndpointInfo,
        output_fields: List[Dict[str, Any]],
        api_call_code: str,
    ) -> str:
        """生成 handler 函数"""

        # 生成返回值
        return_values = []
        for field in output_fields:
            field_name = field["name"]
            # 对于 draft_id 和 segment_id，返回纯 UUID
            if field_name in ID_REFERENCE_FIELDS:
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == "success":
                return_values.append(f'        "{field_name}": True')
            elif field_name == "message":
                return_values.append(f'        "{field_name}": "操作成功"')
            elif field_name == "api_call":
                # 对于 api_call 字段，返回生成的 API 调用代码字符串
                return_values.append(f'        "{field_name}": api_call')
            else:
                # 其他字段使用默认值
                default = field.get("default", "None")
                if default == "..." or default == "Ellipsis":
                    default = infer_default_for_type(field.get("type", "Any"))
                return_values.append(f'        "{field_name}": {default}')

        if not return_values:
            return_values.append("success=True")
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

        # 从模板文件读取辅助函数定义（用于处理 CustomNamespace）
        helper_functions = (_TEMPLATES_DIR / "runtime_helpers.py").read_text(encoding="utf-8") + "\n\n"

        handler_function = (
            helper_functions
            + f'''def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    {endpoint.func_name} 的主处理函数

    Args:
        args: Input arguments

    Returns:
        Dict containing response data (converted from Output NamedTuple for Coze compatibility)
    """
    logger = getattr(args, 'logger', None)

    if logger:
        logger.info(f"调用 {endpoint.func_name}，参数: {{args.input}}")

    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4()).replace("-", "_")

        if logger:
            logger.info(f"生成 UUID: {{generated_uuid}}")

{api_call_code}

        if logger:
            logger.info(f"{endpoint.func_name} 调用成功")

        return Output({output_construction})._asdict()

    except Exception as e:
        error_msg = f"调用 {endpoint.func_name} 时发生错误: {{str(e)}}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {{traceback.format_exc()}}")

        return Output(success=False, message=error_msg)._asdict()
'''
        )

        return handler_function
