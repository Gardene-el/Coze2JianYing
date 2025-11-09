#!/usr/bin/env python3
"""
Coze2JianYing 端插件示例 - Workflow 模式

本示例演示如何使用端插件在 Workflow 中生成剪映草稿。
适合批量处理和自动化任务。

使用方法：
1. 在 Coze 平台创建 Workflow 并配置端插件节点
2. 设置环境变量或修改下方配置
3. 运行此脚本
4. Workflow 将自动执行，调用本地端插件

环境变量：
- COZE_API_TOKEN: Coze API Token (必需)
- COZE_WORKFLOW_ID: Workflow ID (必需)
- COZE_BASE_URL: API 基础 URL (可选，默认国内版)
"""

import os
import sys
import time
import json
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
COZE_WORKFLOW_ID = os.getenv("COZE_WORKFLOW_ID", "")
COZE_BASE_URL = os.getenv("COZE_BASE_URL", "https://api.coze.cn")

# Workflow 输入参数（可根据你的 Workflow 定义调整）
WORKFLOW_PARAMETERS = {
    "topic": os.getenv("WORKFLOW_TOPIC", "中国美食"),
    "style": os.getenv("WORKFLOW_STYLE", "快节奏"),
}

# 或者直接在这里配置（不推荐，仅用于测试）
# COZE_API_TOKEN = "pat_xxxxx..."
# COZE_WORKFLOW_ID = "xxxxx"
# WORKFLOW_PARAMETERS = {"topic": "美食", "style": "快节奏"}

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
    
    if not COZE_WORKFLOW_ID:
        logger.error("❌ 未设置 COZE_WORKFLOW_ID")
        logger.error("请设置环境变量:")
        logger.error('  export COZE_WORKFLOW_ID="your-workflow-id-here"')
        return False
    
    logger.info("✓ 配置检查通过")
    return True


def main():
    """主函数"""
    # 创建日志记录器
    logger = get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info("Coze2JianYing 端插件服务 - Workflow 模式")
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
        
        # 启动 Workflow 模式
        logger.info("=" * 60)
        logger.info("启动端插件服务（Workflow 模式）...")
        logger.info(f"Workflow ID: {COZE_WORKFLOW_ID}")
        logger.info(f"API URL: {COZE_BASE_URL}")
        logger.info(f"输入参数: {json.dumps(WORKFLOW_PARAMETERS, ensure_ascii=False)}")
        logger.info("=" * 60)
        
        success = service.start_workflow_mode(
            workflow_id=COZE_WORKFLOW_ID,
            parameters=WORKFLOW_PARAMETERS
        )
        
        if not success:
            logger.error("❌ 服务启动失败")
            return 1
        
        logger.info("✓ Workflow 已启动")
        logger.info("")
        logger.info("💡 说明：")
        logger.info("   - Workflow 将自动执行")
        logger.info("   - 当 Workflow 节点调用 generate_draft 时，本地会执行")
        logger.info("   - 草稿将生成到剪映的草稿目录")
        logger.info("")
        logger.info("等待 Workflow 完成...")
        logger.info("按 Ctrl+C 可提前终止")
        logger.info("=" * 60)
        
        # 保持运行直到 Workflow 完成
        try:
            while service.is_running:
                time.sleep(1)
            
            logger.info("")
            logger.info("✓ Workflow 已完成")
        
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
