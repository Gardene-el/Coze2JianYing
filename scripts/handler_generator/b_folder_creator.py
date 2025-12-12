"""
B 脚本：在 coze_plugin/raw_tools 下创建对应工具文件夹和文件
负责创建工具目录结构，并生成 handler.py 和 README.md 文件
"""

from pathlib import Path
from typing import Dict, Any, List
import re

from .api_endpoint_info import APIEndpointInfo
from .schema_extractor import SchemaExtractor


class FolderCreator:
    """B脚本：创建工具文件夹和文件"""

    def __init__(self, output_dir: str, schema_extractor: SchemaExtractor = None):
        self.output_dir = Path(output_dir)
        self.schema_extractor = schema_extractor
    
    def _parse_pyjianying_docstring(self, docstring: str) -> Dict[str, Any]:
        """
        解析 pyJianYingDraft 风格的 docstring
        
        Returns:
            包含 description, args, raises 三部分的字典
        """
        if not docstring:
            return {
                "description": "没有提供详细文档注释",
                "args": [],
                "raises": []
            }
        
        # 寻找 "对应 pyJianYingDraft 注释：" 标记
        match = re.search(r'对应 pyJianYingDraft 注释[：:][\s\S]*?```([\s\S]*?)```', docstring, re.MULTILINE)
        
        if not match:
            # 如果没有找到 pyJianYingDraft 注释标记，返回空值
            return {
                "description": "没有提供详细文档注释",
                "args": [],
                "raises": []
            }
        
        pyjianying_doc = match.group(1).strip()
        
        result = {
            "description": "",
            "args": [],
            "raises": []
        }
        
        # 分离 Description, Args 和 Raises 部分
        lines = pyjianying_doc.split('\n')
        current_section = "description"
        current_arg = None
        description_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 检测 Args: 开始
            if line.startswith('Args:'):
                current_section = "args"
                continue
            
            # 检测 Raises: 开始
            if line.startswith('Raises:'):
                current_section = "raises"
                continue
            
            # 处理 description 部分
            if current_section == "description" and line:
                description_lines.append(line)
            
            # 处理 Args 部分
            elif current_section == "args":
                # 匹配参数行: param_name (`type` or `type2`): description
                # 或: param_name (`type`, optional): description
                arg_match = re.match(r'(\w+)\s*\((.+?)(?:,\s*optional)?\):\s*(.*)', line)
                if arg_match:
                    if current_arg:
                        result["args"].append(current_arg)
                    
                    param_name = arg_match.group(1)
                    param_type_raw = arg_match.group(2)
                    param_desc = arg_match.group(3)
                    is_optional = 'optional' in line
                    
                    # 清理类型字符串，移除多余的反引号
                    param_type = param_type_raw.strip('`').strip()
                    
                    current_arg = {
                        "name": param_name,
                        "type": param_type,
                        "description": param_desc,
                        "required": not is_optional
                    }
                elif current_arg and line:
                    # 继续上一个参数的描述
                    current_arg["description"] += " " + line
            
            # 处理 Raises 部分
            elif current_section == "raises":
                # 匹配异常行: `ExceptionType`: description
                raise_match = re.match(r'`([^`]+)`:\s*(.*)', line)
                if raise_match:
                    exception_type = raise_match.group(1)
                    exception_desc = raise_match.group(2)
                    result["raises"].append({
                        "type": exception_type,
                        "description": exception_desc
                    })
        
        # 添加最后一个参数
        if current_arg:
            result["args"].append(current_arg)
        
        # 合并 description
        result["description"] = " ".join(description_lines) if description_lines else "没有提供详细文档注释"
        
        return result

    def create_tool_folder(
        self, endpoint: APIEndpointInfo, handler_content: str, readme_content: str
    ):
        """创建工具文件夹并生成文件"""
        tool_dir = self.output_dir / endpoint.func_name
        tool_dir.mkdir(parents=True, exist_ok=True)

        # 生成 handler.py
        handler_file = tool_dir / "handler.py"
        with open(handler_file, "w", encoding="utf-8") as f:
            f.write(handler_content)

        print(f"  生成: {handler_file}")

        # 生成 README.md
        readme_file = tool_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"  生成: {readme_file}")

        return tool_dir

    def generate_readme(self, endpoint: APIEndpointInfo) -> str:
        """生成 README.md 内容"""
        # 解析 pyJianYingDraft docstring
        doc_info = self._parse_pyjianying_docstring(endpoint.docstring)
        
        # 获取输入参数信息
        input_params_section = self._format_input_parameters(endpoint, doc_info)
        
        # 获取输出参数信息
        output_params_section = self._format_output_parameters(endpoint)
        
        # 检查是否应该有 api_call 字段，如果有则添加使用说明
        should_have_api_call = self._should_have_api_call_field(endpoint.func_name)
        api_call_note = ""
        if should_have_api_call:
            api_call_note = '\n\n受限于Coze本身的运行状态，使用此函数后需使用插件名为"Coze2剪映 - 在Coze IDE 中创建 基础工具"的插件中的write_script工具，将当前工具函数的返回值api_call作为write_script工具的输入值，此函数才起效。'

        return f"""# {endpoint.func_name}

## 工具名称
`{endpoint.func_name}`

## 工具介绍
此工具对应 FastAPI 端点: `{endpoint.path}`

{doc_info['description']}{api_call_note}

## 输入参数

{input_params_section}

## 输出参数

{output_params_section}

## 使用说明
此工具由脚本自动生成，用于在 Coze 平台中调用对应的 API 端点。

工具会：
1. 生成唯一的 UUID
2. 记录 API 调用到 `/tmp/coze2jianying.py` 文件
3. 返回包含 UUID 的响应

## 注意事项
- 此工具在 Coze 平台的沙盒环境中运行
- API 调用记录保存在 `/tmp/coze2jianying.py`
- UUID 用于关联和追踪不同的对象实例
"""
    
    def _format_input_parameters(self, endpoint: APIEndpointInfo, doc_info: Dict[str, Any]) -> str:
        """格式化输入参数表格"""
        if not self.schema_extractor or not endpoint.request_model:
            # 如果没有 request model，只显示路径参数
            if not endpoint.path_params:
                return "无输入参数"
            
            lines = ["| 参数名称 | 参数描述 | 参数类型 | 是否必填 |",
                    "|---------|---------|---------|---------|"]
            
            for param in endpoint.path_params:
                param_desc = "草稿ID" if param == "draft_id" else "片段ID"
                lines.append(f"| {param} | {param_desc} | str | 是 |")
            
            return "\n".join(lines)
        
        # 获取 request model 的字段
        request_fields = self.schema_extractor.get_schema_fields(endpoint.request_model)
        
        if not request_fields and not endpoint.path_params:
            return "无输入参数"
        
        lines = ["| 参数名称 | 参数描述 | 参数类型 | 是否必填 |",
                "|---------|---------|---------|---------|"]
        
        # 先添加路径参数
        for param in endpoint.path_params:
            param_desc = "草稿ID" if param == "draft_id" else "片段ID"
            lines.append(f"| {param} | {param_desc} | str | 是 |")
        
        # 添加 request body 参数
        for field in request_fields:
            field_name = field["name"]
            field_type = field["type"]
            default = field.get("default", "...")
            description = field.get("description", "")
            
            # 判断是否必填
            is_required = default == "..." or default == "Ellipsis"
            required_text = "是" if is_required else "否"
            
            lines.append(f"| {field_name} | {description} | {field_type} | {required_text} |")
        
        return "\n".join(lines)
    
    def _should_have_api_call_field(self, func_name: str) -> bool:
        """
        判断函数是否应该有 api_call 字段
        
        排除以下函数：
        - add_track
        - add_segment
        """
        excluded_add_functions = {
            "add_track",
            "add_segment",
        }
        
        return func_name.startswith("add_") and func_name not in excluded_add_functions

    def _format_output_parameters(self, endpoint: APIEndpointInfo) -> str:
        """格式化输出参数表格"""
        # 判断是否是 create 函数
        is_create_function = "create" in endpoint.func_name.lower()
        # 判断是否应该有 api_call 字段（特定的 add_ 函数）
        should_have_api_call = self._should_have_api_call_field(endpoint.func_name)
        
        if not is_create_function and not should_have_api_call:
            # 非 create 函数且不应该有 api_call 的函数，不显示输出参数
            return "无输出参数"
        
        lines = ["| 参数名称 | 参数描述 | 参数类型 | 是否必填 |",
                "|---------|---------|---------|---------|"]
        
        if is_create_function:
            # create 函数，只返回对应的 ID
            # 判断返回的是 draft_id 还是 segment_id
            if "draft" in endpoint.func_name.lower():
                lines.append("| draft_id | 返回创建的草稿ID | str | 是 |")
            else:
                lines.append("| segment_id | 返回创建的片段ID | str | 是 |")
        
        if should_have_api_call:
            # 特定的 add_ 函数，返回 api_call 字段
            lines.append("| api_call | 生成的 API 调用代码 | str | 是 |")
        
        return "\n".join(lines)
