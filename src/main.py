"""
Coze剪映草稿生成器 - 主程序入口

用法：
    python -m src.main              # 启动 GUI 管理 API（供 Electron 调用）
    python -m src.main --gui-only   # 同上（局密框架兼容别名）
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径（用于导入 backend 与 app.gui）
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.utils.logger import setup_logger, logger


def _start_gui_only(host: str, port: int) -> None:
    """启动 GUI 管理服务器（Electron 模式）。"""
    from src.backend.gui_main import run as run_gui
    logger.info("启动 GUI 管理服务: http://%s:%d", host, port)
    run_gui(host=host, port=port)


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="Coze2JianYing 主程序")
    parser.add_argument(
        "--gui-only",
        action="store_true",
        help="（保留，供向后兼容）",
    )
    parser.add_argument("--host", default="127.0.0.1", help="GUI 管理 API 监听地址")
    parser.add_argument("--port", type=int, default=20210, help="GUI 管理 API 监听端口")
    args = parser.parse_args()

    # 确保logs目录存在
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # 设置日志系统
    log_file = "gui.log" if args.gui_only else "app.log"
    setup_logger(log_dir / log_file)

    logger.info("=" * 60)
    logger.info("应用程序启动")
    logger.info("=" * 60)

    try:
        _start_gui_only(host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"应用程序运行出错: {e}", exc_info=True)
        raise
    finally:
        logger.info("应用程序退出")


if __name__ == "__main__":
    main()
