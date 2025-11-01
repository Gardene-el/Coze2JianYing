"""
Coze剪映草稿生成器 - 主程序入口 (统一入口)

默认启动GUI模式，可通过命令行参数切换到CLI模式
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """
    主函数 - 根据命令行参数决定启动GUI还是CLI
    
    如果没有命令行参数，或第一个参数不是已知的CLI命令，则启动GUI
    """
    # 检查是否有CLI命令参数
    # CLI命令包括: generate, info, --help, --version
    cli_commands = {'generate', 'info', '--help', '-h', '--version'}
    
    # 如果有参数且第一个参数是CLI命令，则使用CLI模式
    if len(sys.argv) > 1 and sys.argv[1] in cli_commands:
        from CLI.main import main as cli_main
        cli_main()
    else:
        # 否则启动GUI模式
        from GUI.main import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
