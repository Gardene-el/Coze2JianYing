"""
Coze剪映草稿生成器 - 主程序入口 (统一入口)

默认启动GUI模式，可通过命令行参数切换到CLI模式
"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def is_cli_mode():
    """
    判断是否为CLI模式
    
    通过检查命令行参数来判断：
    - 如果有参数（除了脚本名称）
    - 且第一个参数是CLI相关的（命令或选项）
    
    Returns:
        bool: True if CLI mode, False for GUI mode
    """
    if len(sys.argv) <= 1:
        return False
    
    first_arg = sys.argv[1]
    
    # CLI选项和命令
    # 包括：--help, -h, --version, 以及所有CLI命令
    cli_indicators = {
        '--help', '-h',
        '--version',
        'generate',
        'info',
    }
    
    return first_arg in cli_indicators


def main():
    """
    主函数 - 根据命令行参数决定启动GUI还是CLI
    
    如果检测到CLI模式标识符，则使用CLI；否则启动GUI
    """
    if is_cli_mode():
        from CLI.main import main as cli_main
        cli_main()
    else:
        # 否则启动GUI模式
        from GUI.main import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
