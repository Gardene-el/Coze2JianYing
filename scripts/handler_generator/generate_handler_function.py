"""
步骤 5：生成 handler 函数
负责生成主 handler 函数的框架代码，包括 UUID 生成和错误处理
"""

from typing import Any, Dict, List

from .api_endpoint_info import APIEndpointInfo


class HandlerFunctionGenerator:
    """步骤 5：生成 handler 函数"""

    def generate_handler_function(
        self,
        endpoint: APIEndpointInfo,
        output_fields: List[Dict[str, Any]],
        api_call_code: str,
    ) -> str:
        """生成 handler 函数"""

        # 确定目标 ID 类型
        target_id_type = None
        if endpoint.has_draft_id:
            target_id_type = "draft_id"
        elif endpoint.has_segment_id:
            target_id_type = "segment_id"

        # 生成返回值
        return_values = []
        for field in output_fields:
            field_name = field["name"]
            # 对于 draft_id 和 segment_id，返回纯 UUID
            # 这样在后续调用中可以通过 draft_{uuid} 或 segment_{uuid} 引用
            if field_name == "draft_id" and target_id_type == "draft_id":
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == "segment_id" and target_id_type == "segment_id":
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == "draft_id":
                return_values.append(f'        "{field_name}": f"{{generated_uuid}}"')
            elif field_name == "segment_id":
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
                    # 根据字段类型设置合理的默认值
                    field_type = field.get("type", "Any")
                    if "int" in field_type.lower():
                        default = "0"
                    elif "str" in field_type.lower():
                        default = '""'
                    elif "bool" in field_type.lower():
                        default = "False"
                    elif "list" in field_type.lower():
                        default = "[]"
                    elif "dict" in field_type.lower():
                        default = "{}"
                    else:
                        default = "None"
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

        # 生成辅助函数的定义（用于处理 CustomNamespace）
        helper_functions = '''def _is_meaningful_object(obj) -> bool:
    """
    检查对象是否包含有意义的数据

    用于区分空的 CustomNamespace() 对象和包含有效数据的对象
    避免将空对象视为有效值，导致 Pydantic 验证失败

    Args:
        obj: 任意对象

    Returns:
        True 如果对象包含有意义的数据，False 如果对象为 None 或为空
    """
    # None 值不是有意义的对象
    if obj is None:
        return False

    # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        # 空字典意味着空对象
        if not obj_dict:
            return False
        # 检查是否所有值都是 None（也视为空对象）
        if all(v is None for v in obj_dict.values()):
            return False
        # 至少有一个非 None 值，视为有意义的对象
        return True

    # 对于基本类型（字符串、数字、布尔值等），非 None 即为有意义
    return True


def _to_type_constructor(obj, type_name: str) -> str:
    """
    将 CustomNamespace/SimpleNamespace 对象转换为类型构造表达式字符串

    用于处理 Coze 的 CustomNamespace/SimpleNamespace 对象
    这些对象在 Coze 云端使用，在应用端执行时需要转换为对应类型的构造调用

    例如：
        CustomNamespace(start=0, duration=5000000)
        -> "TimeRange(start=0, duration=5000000)"

    Args:
        obj: CustomNamespace/SimpleNamespace 对象
        type_name: 目标类型名，如 "TimeRange", "ClipSettings", "CropSettings", "TextStyle"

    Returns:
        类型构造表达式字符串，如 "TimeRange(start=0, duration=5000000)"
    """
    if obj is None:
        return 'None'

    # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        # 构造类型构造调用的参数列表
        params = []
        for key, value in obj_dict.items():
            # 递归处理嵌套对象
            if hasattr(value, '__dict__'):
                # 嵌套对象：尝试推断其类型名（使用首字母大写的 key）
                nested_type_name = key.capitalize() if key else 'Object'
                # 如果 key 本身就是类型相关的，使用更智能的命名
                # 根据最新 schema 重构：ClipSettings, CropSettings, TextStyle, TimeRange
                if 'clip_settings' in key.lower() or key.lower() == 'clipsettings':
                    nested_type_name = 'ClipSettings'
                elif 'crop_settings' in key.lower() or key.lower() == 'cropsettings':
                    nested_type_name = 'CropSettings'
                elif 'timerange' in key.lower():
                    nested_type_name = 'TimeRange'
                elif 'text_style' in key.lower() or key.lower() == 'textstyle':
                    nested_type_name = 'TextStyle'
                # Note: Position class was removed in schema refactoring
                value_repr = _to_type_constructor(value, nested_type_name)
            elif isinstance(value, str):
                # 字符串值：加引号
                value_repr = f'"{value}"'
            else:
                # 其他类型：直接使用 repr
                value_repr = repr(value)
            params.append(f'{key}={value_repr}')

        # 构造类型构造表达式：TypeName(param1=value1, param2=value2)
        return f'{type_name}(' + ', '.join(params) + ')'

    # 如果不是复杂对象，返回其 repr
    if isinstance(obj, str):
        return f'"{obj}"'
    else:
        return repr(obj)


'''

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
