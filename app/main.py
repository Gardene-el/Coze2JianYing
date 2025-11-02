"""
Coze剪映草稿生成器 - 主程序入口
"""
import sys
import os
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.gui.main_window import MainWindow
from app.utils.logger import setup_logger, get_logger


def main():
    """主函数"""
    # 确保logs目录存在
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 设置日志系统
    setup_logger(log_dir / "app.log")
    logger = get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info("应用程序启动")
    logger.info("=" * 60)
    
    try:
        # 创建并运行主窗口
        app = MainWindow()
        logger.info("主窗口已创建")
        app.run()
    except Exception as e:
        logger.error(f"应用程序运行出错: {e}", exc_info=True)
        raise
    finally:
        logger.info("应用程序退出")


if __name__ == "__main__":
    main()
