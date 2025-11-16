"""
API 端点信息数据类
用于在各脚本模块间传递 API 端点的元数据
"""

from typing import List, Optional


class APIEndpointInfo:
    """存储 API 端点信息"""
    def __init__(self, func_name: str, path: str, has_draft_id: bool, has_segment_id: bool,
                 request_model: Optional[str], response_model: Optional[str],
                 path_params: List[str], source_file: str, docstring: Optional[str] = None):
        self.func_name = func_name
        self.path = path
        self.has_draft_id = has_draft_id
        self.has_segment_id = has_segment_id
        self.request_model = request_model
        self.response_model = response_model
        self.path_params = path_params
        self.source_file = source_file
        self.docstring = docstring
