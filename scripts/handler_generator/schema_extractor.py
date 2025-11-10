"""
Schema Extractor - 辅助模块
用于从 Pydantic schema 文件中提取类字段信息
供 C/D/E 脚本使用
"""

import ast
from pathlib import Path
from typing import List, Dict, Any


class SchemaExtractor:
    """提取 Pydantic Schema 的字段信息"""
    
    def __init__(self, schema_file: str):
        self.schema_file = Path(schema_file)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载 schema 文件内容"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # 查找所有类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    fields = self._extract_class_fields(node)
                    self.schemas[node.name] = fields
        
        except Exception as e:
            print(f"警告: 加载 schema 文件时出错: {e}")
    
    def _extract_class_fields(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """提取类的字段信息"""
        fields = []
        
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign):
                # 这是一个带类型注解的赋值
                field_name = item.target.id if isinstance(item.target, ast.Name) else None
                if field_name:
                    field_type = self._get_type_string(item.annotation)
                    default_value = self._get_default_value(item.value)
                    
                    # 提取 Field 的描述
                    description = ""
                    if isinstance(item.value, ast.Call):
                        if (isinstance(item.value.func, ast.Name) and 
                            item.value.func.id == 'Field'):
                            for keyword in item.value.keywords:
                                if keyword.arg == 'description':
                                    if isinstance(keyword.value, ast.Constant):
                                        description = keyword.value.value
                    
                    fields.append({
                        'name': field_name,
                        'type': field_type,
                        'default': default_value,
                        'description': description
                    })
        
        return fields
    
    def _get_type_string(self, annotation) -> str:
        """获取类型注解的字符串表示"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # 处理 Optional[T], List[T] 等
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    inner_type = annotation.slice.id
                    return f"{base_type}[{inner_type}]"
                return base_type
        return "Any"
    
    def _get_default_value(self, value_node) -> str:
        """获取默认值"""
        if value_node is None:
            return "..."
        elif isinstance(value_node, ast.Constant):
            if isinstance(value_node.value, str):
                return f'"{value_node.value}"'
            return str(value_node.value)
        elif isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name) and value_node.func.id == 'Field':
                # 从 Field() 提取默认值
                if value_node.args:
                    if isinstance(value_node.args[0], ast.Constant):
                        val = value_node.args[0].value
                        if isinstance(val, str):
                            return f'"{val}"'
                        return str(val)
                return "..."
        return "..."
    
    def get_schema_fields(self, schema_name: str) -> List[Dict[str, Any]]:
        """获取指定 schema 的字段"""
        return self.schemas.get(schema_name, [])
