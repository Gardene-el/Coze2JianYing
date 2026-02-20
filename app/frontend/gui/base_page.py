import customtkinter as ctk
from app.backend.utils.logger import get_logger

class BasePage(ctk.CTkFrame):
    """页面基类"""
    
    def __init__(self, parent, page_name: str):
        super().__init__(parent)
        self.page_name = page_name
        self.logger = get_logger(f"{__name__}.{page_name}")
        
        # 页面特定的变量字典
        self._page_variables = {}
        
        # 创建UI组件
        self._create_widgets()
        self._setup_layout()
        
        self.logger.info(f"页面 '{page_name}' 已初始化")
        
    def _create_widgets(self):
        """创建UI组件（子类应重写此方法）"""
        pass
    
    def _setup_layout(self):
        """设置布局（子类应重写此方法）"""
        pass
        
    def cleanup(self):
        """清理资源"""
        self.logger.info(f"页面 '{self.page_name}' 清理资源")
        self._page_variables.clear()
