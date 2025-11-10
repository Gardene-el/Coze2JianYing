"""
A 脚本：扫描 /app/api 下所有 POST API 函数
负责扫描 FastAPI 路由文件，提取所有 POST 端点的信息
"""

import ast
from pathlib import Path
from typing import List, Optional

from .api_endpoint_info import APIEndpointInfo


class APIScanner:
    """A脚本：扫描 /app/api 下所有 POST API 函数"""
    
    def __init__(self, api_dir: str):
        self.api_dir = Path(api_dir)
        self.endpoints: List[APIEndpointInfo] = []
    
    def scan_file(self, file_path: Path) -> List[APIEndpointInfo]:
        """扫描单个 Python 文件中的 POST API 端点"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # 遍历 AST 查找函数定义（包括 async 函数）
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 检查是否有 @router.post 装饰器
                    endpoint_info = self._extract_post_endpoint(node, file_path)
                    if endpoint_info:
                        endpoints.append(endpoint_info)
        
        except Exception as e:
            print(f"警告: 解析文件 {file_path} 时出错: {e}")
        
        return endpoints
    
    def _extract_post_endpoint(self, node: ast.FunctionDef, source_file: Path) -> Optional[APIEndpointInfo]:
        """从函数节点提取 POST 端点信息"""
        # 检查装饰器
        has_post_decorator = False
        endpoint_path = ""
        response_model = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # 检查是否是 router.post
                if (isinstance(decorator.func, ast.Attribute) and 
                    decorator.func.attr == 'post'):
                    has_post_decorator = True
                    
                    # 提取路径
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            endpoint_path = decorator.args[0].value
                    
                    # 提取 response_model
                    for keyword in decorator.keywords:
                        if keyword.arg == 'response_model':
                            if isinstance(keyword.value, ast.Name):
                                response_model = keyword.value.id
        
        if not has_post_decorator:
            return None
        
        # 分析函数参数
        func_name = node.name
        has_draft_id = False
        has_segment_id = False
        request_model = None
        path_params = []
        
        for arg in node.args.args:
            arg_name = arg.arg
            
            # 检查路径参数
            if arg_name == 'draft_id':
                has_draft_id = True
                path_params.append('draft_id')
            elif arg_name == 'segment_id':
                has_segment_id = True
                path_params.append('segment_id')
            elif arg_name == 'request':
                # 尝试获取类型注解
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        request_model = arg.annotation.id
        
        return APIEndpointInfo(
            func_name=func_name,
            path=endpoint_path,
            has_draft_id=has_draft_id,
            has_segment_id=has_segment_id,
            request_model=request_model,
            response_model=response_model,
            path_params=path_params,
            source_file=str(source_file)
        )
    
    def scan_all(self) -> List[APIEndpointInfo]:
        """扫描所有 API 文件"""
        api_files = list(self.api_dir.glob('*_routes.py'))
        
        for api_file in api_files:
            print(f"扫描文件: {api_file.name}")
            endpoints = self.scan_file(api_file)
            self.endpoints.extend(endpoints)
            print(f"  找到 {len(endpoints)} 个 POST 端点")
        
        print(f"\n总共找到 {len(self.endpoints)} 个 POST API 端点")
        return self.endpoints
