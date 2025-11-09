"""
端插件服务模块

提供基于 cozepy SDK 的端插件（Local Plugin）功能，
使本地应用可以监听 Coze Bot/Workflow 的 SSE 事件流，
在本地执行草稿生成等操作，无需公网 IP。

关键特性：
- 本地应用主动连接到 Coze 云端（无需公网 IP）
- 通过 SSE (Server-Sent Events) 接收事件
- 监听 REQUIRES_ACTION 事件并执行本地功能
- 将结果提交回 Coze Bot/Workflow

使用场景：
- 个人用户无需配置 ngrok 或云服务器
- 直接在本地生成剪映草稿
- 适合快速原型和个人使用
"""

import json
import logging
import threading
from typing import Optional, Dict, Any, Callable
from enum import Enum

try:
    from cozepy import (
        Coze,
        TokenAuth,
        ChatEvent,
        ChatEventType,
        Message,
        Stream,
        ToolOutput,
        COZE_CN_BASE_URL,
        COZE_COM_BASE_URL,
    )
    COZEPY_AVAILABLE = True
except ImportError:
    COZEPY_AVAILABLE = False
    # Provide dummy values for type hints
    Coze = Any
    ChatEvent = Any
    Stream = Any


class PluginMode(str, Enum):
    """端插件模式"""
    BOT = "bot"           # Bot 对话模式
    WORKFLOW = "workflow" # Workflow 工作流模式


class LocalPluginService:
    """
    端插件服务
    
    负责连接 Coze Bot/Workflow，监听事件流，
    并在本地执行工具调用（如草稿生成）。
    """
    
    def __init__(
        self,
        coze_token: str,
        base_url: str = COZE_CN_BASE_URL,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化端插件服务
        
        Args:
            coze_token: Coze API Token (Personal Access Token)
            base_url: Coze API 基础 URL (默认国内版)
            logger: 日志记录器
        """
        if not COZEPY_AVAILABLE:
            raise ImportError("cozepy 未安装。请运行: pip install cozepy")
        
        self.logger = logger or logging.getLogger(__name__)
        self.coze_token = coze_token
        self.base_url = base_url
        
        # 创建 Coze 客户端
        self.coze = Coze(
            auth=TokenAuth(coze_token),
            base_url=base_url
        )
        
        # 服务状态
        self.is_running = False
        self.stop_event = threading.Event()
        self.service_thread: Optional[threading.Thread] = None
        
        # 工具函数注册表
        self.tool_handlers: Dict[str, Callable] = {}
        
        self.logger.info("端插件服务已初始化")
    
    def register_tool(self, tool_name: str, handler: Callable[[Dict], str]):
        """
        注册工具处理函数
        
        Args:
            tool_name: 工具名称（如 "generate_draft"）
            handler: 处理函数，接收参数字典，返回 JSON 字符串结果
        
        Example:
            def generate_draft_handler(args: dict) -> str:
                draft_id = create_draft(args['content'])
                return json.dumps({"draft_id": draft_id})
            
            service.register_tool("generate_draft", generate_draft_handler)
        """
        self.tool_handlers[tool_name] = handler
        self.logger.info(f"已注册工具: {tool_name}")
    
    def start_bot_mode(
        self,
        bot_id: str,
        user_id: str = "local-user",
        initial_message: Optional[str] = None
    ) -> bool:
        """
        启动 Bot 对话模式
        
        在此模式下，服务会持续监听用户与 Bot 的对话，
        当 Bot 决定调用端插件时，在本地执行并返回结果。
        
        Args:
            bot_id: Coze Bot ID
            user_id: 用户 ID（用于标识会话）
            initial_message: 初始消息（可选，用于启动对话）
        
        Returns:
            是否启动成功
        """
        if self.is_running:
            self.logger.warning("服务已在运行中")
            return False
        
        self.logger.info(f"启动 Bot 模式: bot_id={bot_id}, user_id={user_id}")
        
        try:
            def run_bot_service():
                self.is_running = True
                self.stop_event.clear()
                
                try:
                    # 如果有初始消息，发起对话
                    if initial_message:
                        self.logger.info(f"发送初始消息: {initial_message}")
                        stream = self.coze.chat.stream(
                            bot_id=bot_id,
                            user_id=user_id,
                            additional_messages=[
                                Message.build_user_question_text(initial_message)
                            ]
                        )
                        self._handle_stream(stream)
                    
                    # 持续监听（在实际应用中，这里需要更复杂的事件循环）
                    while not self.stop_event.is_set():
                        self.stop_event.wait(1)
                
                except Exception as e:
                    self.logger.error(f"Bot 服务运行错误: {e}", exc_info=True)
                finally:
                    self.is_running = False
                    self.logger.info("Bot 服务已停止")
            
            self.service_thread = threading.Thread(target=run_bot_service, daemon=True)
            self.service_thread.start()
            return True
        
        except Exception as e:
            self.logger.error(f"启动 Bot 服务失败: {e}", exc_info=True)
            return False
    
    def start_workflow_mode(
        self,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        启动 Workflow 工作流模式
        
        在此模式下，服务会运行指定的工作流，
        当工作流节点调用端插件时，在本地执行并返回结果。
        
        Args:
            workflow_id: Coze Workflow ID
            parameters: 工作流输入参数
        
        Returns:
            是否启动成功
        """
        if self.is_running:
            self.logger.warning("服务已在运行中")
            return False
        
        self.logger.info(f"启动 Workflow 模式: workflow_id={workflow_id}")
        
        try:
            def run_workflow_service():
                self.is_running = True
                self.stop_event.clear()
                
                try:
                    # 运行工作流
                    self.logger.info("开始执行工作流...")
                    stream = self.coze.workflows.run(
                        workflow_id=workflow_id,
                        parameters=parameters or {}
                    )
                    
                    # 处理工作流事件流
                    self._handle_workflow_stream(stream)
                
                except Exception as e:
                    self.logger.error(f"Workflow 服务运行错误: {e}", exc_info=True)
                finally:
                    self.is_running = False
                    self.logger.info("Workflow 服务已停止")
            
            self.service_thread = threading.Thread(target=run_workflow_service, daemon=True)
            self.service_thread.start()
            return True
        
        except Exception as e:
            self.logger.error(f"启动 Workflow 服务失败: {e}", exc_info=True)
            return False
    
    def stop(self):
        """停止服务"""
        if not self.is_running:
            self.logger.warning("服务未运行")
            return
        
        self.logger.info("正在停止服务...")
        self.stop_event.set()
        
        if self.service_thread and self.service_thread.is_alive():
            self.service_thread.join(timeout=5)
        
        self.is_running = False
        self.logger.info("服务已停止")
    
    def _handle_stream(self, stream: Stream[ChatEvent]):
        """
        处理 Bot 对话事件流
        
        Args:
            stream: SSE 事件流
        """
        try:
            for event in stream:
                if self.stop_event.is_set():
                    break
                
                # 普通消息
                if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                    content = event.message.content
                    self.logger.debug(f"Bot 回复: {content}")
                
                # 端插件调用请求
                elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
                    self.logger.info("检测到端插件调用请求")
                    self._handle_requires_action(event)
                
                # 对话完成
                elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                    self.logger.info("对话完成")
                    break
        
        except Exception as e:
            self.logger.error(f"处理事件流时出错: {e}", exc_info=True)
    
    def _handle_workflow_stream(self, stream):
        """
        处理 Workflow 事件流
        
        Args:
            stream: 工作流事件流
        """
        try:
            for event in stream:
                if self.stop_event.is_set():
                    break
                
                self.logger.debug(f"Workflow 事件: {event}")
                
                # 检查是否有端插件调用（具体事件类型需根据 cozepy 版本调整）
                # 注意：Workflow 的端插件支持可能需要特定的 API 版本
                if hasattr(event, 'event') and 'requires_action' in str(event.event).lower():
                    self.logger.info("检测到 Workflow 端插件调用")
                    self._handle_requires_action(event)
        
        except Exception as e:
            self.logger.error(f"处理 Workflow 事件流时出错: {e}", exc_info=True)
    
    def _handle_requires_action(self, event: ChatEvent):
        """
        处理端插件调用请求
        
        Args:
            event: REQUIRES_ACTION 事件
        """
        try:
            required_action = event.chat.required_action
            tool_calls = required_action.submit_tool_outputs.tool_calls
            
            outputs = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments
                call_id = tool_call.id
                
                self.logger.info(f"调用工具: {tool_name}")
                self.logger.debug(f"参数: {arguments}")
                
                # 执行工具
                result = self._execute_tool(tool_name, arguments)
                
                # 构建输出
                outputs.append(ToolOutput(
                    tool_call_id=call_id,
                    output=result
                ))
            
            # 提交结果
            self._submit_tool_outputs(event, outputs)
        
        except Exception as e:
            self.logger.error(f"处理端插件调用时出错: {e}", exc_info=True)
    
    def _execute_tool(self, tool_name: str, arguments: str) -> str:
        """
        执行工具函数
        
        Args:
            tool_name: 工具名称
            arguments: JSON 字符串参数
        
        Returns:
            执行结果（JSON 字符串）
        """
        try:
            # 解析参数
            args = json.loads(arguments)
            
            # 查找处理函数
            if tool_name not in self.tool_handlers:
                error_msg = f"未注册的工具: {tool_name}"
                self.logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            # 执行处理函数
            handler = self.tool_handlers[tool_name]
            result = handler(args)
            
            self.logger.info(f"工具 {tool_name} 执行成功")
            return result
        
        except json.JSONDecodeError as e:
            error_msg = f"参数解析失败: {e}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        except Exception as e:
            error_msg = f"工具执行失败: {e}"
            self.logger.error(error_msg, exc_info=True)
            return json.dumps({"error": error_msg})
    
    def _submit_tool_outputs(self, event: ChatEvent, outputs: list):
        """
        提交工具执行结果
        
        Args:
            event: 原始事件
            outputs: 工具输出列表
        """
        try:
            self.logger.info("提交工具执行结果...")
            
            # 提交结果并获取新的事件流
            new_stream = self.coze.chat.submit_tool_outputs(
                conversation_id=event.chat.conversation_id,
                chat_id=event.chat.id,
                tool_outputs=outputs,
                stream=True
            )
            
            # 继续处理新的事件流（递归）
            self._handle_stream(new_stream)
        
        except Exception as e:
            self.logger.error(f"提交工具结果时出错: {e}", exc_info=True)


def create_draft_tool_handler(draft_generator) -> Callable:
    """
    创建草稿生成工具处理函数的工厂函数
    
    Args:
        draft_generator: DraftGenerator 实例
    
    Returns:
        工具处理函数
    """
    def handler(args: dict) -> str:
        """
        草稿生成处理函数
        
        Args:
            args: 工具参数
                - content: JSON 内容（必需）
                - output_folder: 输出文件夹（可选）
        
        Returns:
            执行结果 JSON
        """
        try:
            content = args.get('content')
            output_folder = args.get('output_folder')
            
            if not content:
                return json.dumps({
                    "status": "error",
                    "message": "缺少必需参数: content"
                })
            
            # 执行草稿生成
            draft_ids = draft_generator.generate(
                content=content,
                output_folder=output_folder
            )
            
            # 返回结果
            return json.dumps({
                "status": "success",
                "message": f"成功生成 {len(draft_ids)} 个草稿",
                "draft_ids": draft_ids
            })
        
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"草稿生成失败: {str(e)}"
            })
    
    return handler


# 导出检查函数
def is_cozepy_available() -> bool:
    """检查 cozepy 是否可用"""
    return COZEPY_AVAILABLE
