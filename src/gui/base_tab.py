"""
标签页基类模块

提供标签页的基础功能和变量隔离
"""
import tkinter as tk
from tkinter import ttk
from utils.logger import get_logger


class BaseTab:
    """标签页基类
    
    所有标签页都应该继承此基类，以确保变量隔离和一致的接口
    """
    
    def __init__(self, parent: ttk.Notebook, tab_name: str):
        """
        初始化标签页
        
        Args:
            parent: 父Notebook组件
            tab_name: 标签页名称
        """
        self.parent = parent
        self.tab_name = tab_name
        self.logger = get_logger(f"{__name__}.{tab_name}")
        
        # 创建标签页主框架 - 这是标签页的根容器
        self.frame = ttk.Frame(parent, padding="10")
        
        # 将标签页添加到Notebook
        parent.add(self.frame, text=tab_name)
        
        # 标签页特定的变量字典（用于完全隔离）
        self._tab_variables = {}
        
        # 创建UI组件
        self._create_widgets()
        self._setup_layout()
        
        self.logger.info(f"标签页 '{tab_name}' 已初始化")
    
    def _create_widgets(self):
        """创建UI组件（子类应重写此方法）"""
        pass
    
    def _setup_layout(self):
        """设置布局（子类应重写此方法）"""
        pass
    
    def get_tab_variable(self, key: str, default=None):
        """
        获取标签页特定的变量
        
        Args:
            key: 变量键
            default: 默认值
            
        Returns:
            变量值或默认值
        """
        return self._tab_variables.get(key, default)
    
    def set_tab_variable(self, key: str, value):
        """
        设置标签页特定的变量
        
        Args:
            key: 变量键
            value: 变量值
        """
        self._tab_variables[key] = value
    
    def cleanup(self):
        """清理标签页资源（子类可重写此方法）"""
        self.logger.info(f"标签页 '{self.tab_name}' 清理资源")
        self._tab_variables.clear()
