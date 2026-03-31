"""
步骤 5：生成 handler 函数
负责生成主 handler 函数的框架代码，包括 UUID 生成和错误处理

重构说明：
  简化返回值构造，移除冗余 Output 字段的手动映射。
  运行时辅助函数（_to_type_constructor 等）不再在此嵌入，
  改由 main.py 通过 Jinja2 模板按需注入。
"""

from __future__ import annotations

from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo
from .shared import ID_REFERENCE_FIELDS, infer_default_for_type


class HandlerFunctionGenerator:
    """步骤 5：生成 handler 函数"""

    def generate_handler_function(
        self,
        endpoint: APIEndpointInfo,
        output_fields: List[Dict[str, Any]],
        api_call_code: str,
    ) -> str:
        """生成 handler 函数"""

        # 构造 Output(...) 关键字参数列表
        output_params: list[str] = []
        for field in output_fields:
            name = field["name"]
            if name in ID_REFERENCE_FIELDS:
                output_params.append(f'{name}=f"{{generated_uuid}}"')
            elif name == "success":
                output_params.append(f"{name}=True")
            elif name == "message":
                output_params.append(f'{name}="操作成功"')
            elif name == "api_call":
                output_params.append(f"{name}=api_call")
            else:
                default = field.get("default", "None")
                if default in ("...", "Ellipsis"):
                    default = infer_default_for_type(field.get("type", "Any"))
                output_params.append(f"{name}={default}")

        if not output_params:
            output_params = ["success=True", 'message="操作成功"']

        output_construction = ", ".join(output_params)

        handler_function = f'''def handler(args: Args[Input]) -> Dict[str, Any]:
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

        return handler_function
