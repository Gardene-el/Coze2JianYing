"""
B 脚本：在 coze_plugin/raw_tools 下创建对应工具文件夹和文件
负责创建工具目录结构，并生成 handler.py 和 README.md 文件
"""

from pathlib import Path

from .api_endpoint_info import APIEndpointInfo


class FolderCreator:
    """B脚本：创建工具文件夹和文件"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
    
    def create_tool_folder(self, endpoint: APIEndpointInfo, handler_content: str, readme_content: str):
        """创建工具文件夹并生成文件"""
        tool_dir = self.output_dir / endpoint.func_name
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成 handler.py
        handler_file = tool_dir / 'handler.py'
        with open(handler_file, 'w', encoding='utf-8') as f:
            f.write(handler_content)
        
        print(f"  生成: {handler_file}")
        
        # 生成 README.md
        readme_file = tool_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  生成: {readme_file}")
        
        return tool_dir
    
    def generate_readme(self, endpoint: APIEndpointInfo) -> str:
        """生成 README.md 内容"""
        return f"""# {endpoint.func_name}

## 功能描述
此工具对应 FastAPI 端点: `{endpoint.path}`

源文件: `{endpoint.source_file}`

## API 信息
- **函数名**: {endpoint.func_name}
- **路径**: {endpoint.path}
- **方法**: POST
- **Request Model**: {endpoint.request_model or '无'}
- **Response Model**: {endpoint.response_model or '无'}

## 路径参数
{self._format_path_params(endpoint)}

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
    
    def _format_path_params(self, endpoint: APIEndpointInfo) -> str:
        """格式化路径参数说明"""
        if not endpoint.path_params:
            return "无"
        
        params = []
        for param in endpoint.path_params:
            params.append(f"- `{param}`: {'草稿ID' if param == 'draft_id' else '片段ID'}")
        
        return '\n'.join(params)
