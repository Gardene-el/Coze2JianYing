#!/usr/bin/env python3
"""
Coze剪映小助手使用示例

运行前请确保已安装所有依赖：
pip install -r requirements.txt
"""

import sys
import os

# 添加当前目录到Python路径，以便导入本地包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from coze_plugin.coze_jianying_assistant import CozeJianYingAssistant
    
    def example_usage():
        """示例使用方法"""
        print("=== Coze剪映小助手使用示例 ===")
        
        # 创建助手实例
        assistant = CozeJianYingAssistant()
        print("✓ 已创建助手实例")
        
        # 创建新的剪映草稿
        draft = assistant.create_draft("示例项目")
        print("✓ 已创建剪映草稿项目")
        
        # 这里可以添加更多示例操作
        # assistant.process_video("path/to/your/video.mp4")
        # assistant.export_draft("path/to/output")
        
        print("=== 示例运行完成 ===")
    
    if __name__ == "__main__":
        example_usage()
        
except ImportError as e:
    print(f"导入错误：{e}")
    print("\n请先安装依赖：")
    print("pip install -r requirements.txt")
    sys.exit(1)