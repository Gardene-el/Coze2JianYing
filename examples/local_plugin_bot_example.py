#!/usr/bin/env python3
"""
Coze2JianYing 端插件示例 - Bot 模式

本示例演示如何使用端插件在 Bot 对话中生成剪映草稿。
无需公网 IP，本地应用直接连接 Coze 云端。

使用方法：
1. 在 Coze 平台创建 Bot 并配置端插件
2. 设置环境变量或修改下方配置
3. 运行此脚本
4. 在 Coze 平台与 Bot 对话

环境变量：
- COZE_API_TOKEN: Coze API Token (必需)
- COZE_BOT_ID: Bot ID (必需)
- COZE_BASE_URL: API 基础 URL (可选，默认国内版)
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.local_plugin_service import (
    LocalPluginService,
    create_draft_tool_handler,
    is_cozepy_available
)
from app.utils.draft_generator import DraftGenerator
from app.utils.logger import get_logger

# ==================== 配置区域 ====================

# 从环境变量读取配置（推荐）
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN", "")
COZE_BOT_ID = os.getenv("COZE_BOT_ID", "")
COZE_BASE_URL = os.getenv("COZE_BASE_URL", "https://api.coze.cn")

# 或者直接在这里配置（不推荐，仅用于测试）
# COZE_API_TOKEN = "pat_xxxxx..."
# COZE_BOT_ID = "73xxxxxxxxx19"

# ==================================================


def check_configuration():
    """检查配置是否完整"""
    logger = get_logger(__name__)
    
    if not is_cozepy_available():
        logger.error("❌ cozepy 未安装")
        logger.error("请运行: pip install cozepy")
        return False
    
    if not COZE_API_TOKEN:
        logger.error("❌ 未设置 COZE_API_TOKEN")
        logger.error("请设置环境变量:")
        logger.error('  export COZE_API_TOKEN="your-token-here"')
        logger.error("或在 Coze 平台获取: https://www.coze.cn/open/oauth/pats")
        return False
    
    if not COZE_BOT_ID:
        logger.error("❌ 未设置 COZE_BOT_ID")
        logger.error("请设置环境变量:")
        logger.error('  export COZE_BOT_ID="your-bot-id-here"')
        return False
    
    logger.info("✓ 配置检查通过")
    return True


def main():
    """主函数"""
    # 创建日志记录器
    logger = get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info("Coze2JianYing 端插件服务 - Bot 模式")
    logger.info("=" * 60)
    
    # 检查配置
    if not check_configuration():
        return 1
    
    try:
        # 创建草稿生成器
        logger.info("初始化草稿生成器...")
        draft_generator = DraftGenerator()
        
        # 创建端插件服务
        logger.info("创建端插件服务...")
        service = LocalPluginService(
            coze_token=COZE_API_TOKEN,
            base_url=COZE_BASE_URL,
            logger=logger
        )
        
        # 注册草稿生成工具
        logger.info("注册工具: generate_draft")
        draft_handler = create_draft_tool_handler(draft_generator)
        service.register_tool("generate_draft", draft_handler)
        
        # 启动 Bot 模式
        logger.info("=" * 60)
        logger.info("启动端插件服务（Bot 模式）...")
        logger.info(f"Bot ID: {COZE_BOT_ID}")
        logger.info(f"API URL: {COZE_BASE_URL}")
        logger.info("=" * 60)
        
        # 注意：这里没有设置 initial_message，因为我们想让用户主动在 Coze 平台与 Bot 对话
        # 如果需要自动发起对话，可以设置：
        # initial_message="帮我生成一个视频草稿"
        
        success = service.start_bot_mode(
            bot_id=COZE_BOT_ID,
            user_id="local-user"
        )
        
        if not success:
            logger.error("❌ 服务启动失败")
            return 1
        
        logger.info("✓ 服务已启动")
        logger.info("")
        logger.info("💡 使用说明：")
        logger.info("   1. 打开 Coze 平台: https://www.coze.cn/")
        logger.info("   2. 找到你的 Bot 并开始对话")
        logger.info("   3. 当 Bot 调用 generate_draft 工具时，本地会自动执行")
        logger.info("   4. 草稿将生成到剪映的草稿目录")
        logger.info("")
        logger.info("按 Ctrl+C 停止服务...")
        logger.info("=" * 60)
        
        # 保持运行
        try:
            while service.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("")
            logger.info("收到中断信号，正在停止服务...")
            service.stop()
            logger.info("✓ 服务已停止")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ 运行时错误: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
