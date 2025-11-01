"""
示例标签页模块

演示标签页架构和变量隔离
"""
import tkinter as tk
from tkinter import ttk, scrolledtext

from gui.base_tab import BaseTab


class ExampleTab(BaseTab):
    """示例标签页
    
    用于演示标签页架构的示例
    """
    
    def __init__(self, parent: ttk.Notebook):
        """
        初始化示例标签页
        
        Args:
            parent: 父Notebook组件
        """
        # 调用父类初始化
        super().__init__(parent, "示例标签页")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 标题标签
        self.title_label = ttk.Label(
            self.frame, 
            text="这是一个示例标签页",
            font=("Arial", 14, "bold")
        )
        
        # 说明文本
        info_text = """
此标签页用于演示标签页架构的功能特点：

1. 变量隔离：每个标签页有自己独立的变量空间
2. 组件独立：标签页之间的UI组件互不干扰
3. 资源管理：标签页可以独立管理自己的资源

您可以在此处添加新的功能标签页。
        """
        
        self.info_frame = ttk.LabelFrame(self.frame, text="说明", padding="10")
        self.info_label = ttk.Label(
            self.info_frame,
            text=info_text.strip(),
            justify=tk.LEFT,
            wraplength=600
        )
        
        # 测试区域
        self.test_frame = ttk.LabelFrame(self.frame, text="变量隔离测试", padding="10")
        
        self.test_label = ttk.Label(self.test_frame, text="标签页特定变量:")
        self.test_var = tk.StringVar(value="")
        self.test_entry = ttk.Entry(self.test_frame, textvariable=self.test_var, width=40)
        
        self.test_btn = ttk.Button(
            self.test_frame,
            text="保存到标签页变量",
            command=self._save_test_variable
        )
        
        self.test_result_label = ttk.Label(self.test_frame, text="保存的值: (无)")
        
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
    
    def _setup_layout(self):
        """设置布局"""
        # 标题
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 说明区域
        self.info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.info_label.pack(fill=tk.BOTH, expand=True)
        
        # 测试区域
        self.test_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.test_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.test_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.test_btn.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.test_result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        self.test_frame.columnconfigure(0, weight=1)
    
    def _save_test_variable(self):
        """保存测试变量"""
        value = self.test_var.get()
        self.set_tab_variable("test_value", value)
        
        # 更新显示
        saved_value = self.get_tab_variable("test_value")
        self.test_result_label.config(text=f"保存的值: {saved_value}")
        
        self.logger.info(f"保存变量: {value}")
