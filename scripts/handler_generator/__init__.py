"""
Handler Generator Package
包含 A-E 五个脚本模块，用于从 API 端点自动生成 Coze handler
"""

from .api_endpoint_info import APIEndpointInfo
from .a_api_scanner import APIScanner
from .b_folder_creator import FolderCreator
from .c_input_output_generator import InputOutputGenerator
from .d_handler_function_generator import HandlerFunctionGenerator
from .e_api_call_code_generator import APICallCodeGenerator
from .schema_extractor import SchemaExtractor

__all__ = [
    'APIEndpointInfo',
    'APIScanner',
    'FolderCreator',
    'InputOutputGenerator',
    'HandlerFunctionGenerator',
    'APICallCodeGenerator',
    'SchemaExtractor',
]
