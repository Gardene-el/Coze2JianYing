"""
ngrok 管理器模块

归属：core/ — 基础设施管理，
负责 ngrok 隧道的生命周期管理（启动、停止、状态监控），
为 API 服务提供公网访问能力。
"""
import threading
import time
import sys
import os
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

try:
    from pyngrok import ngrok, conf
    from pyngrok.exception import PyngrokError, PyngrokNgrokError
    PYNGROK_AVAILABLE = True
except ImportError:
    PYNGROK_AVAILABLE = False


@contextmanager
def suppress_stdout_stderr():
    """上下文管理器：临时抑制 stdout 和 stderr 输出

    用于在 GUI 应用中避免 pyngrok 安装时的输出问题
    """
    # 保存原始的 stdout 和 stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # 将 stdout 和 stderr 重定向到 devnull
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
    finally:
        # 恢复原始的 stdout 和 stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class NgrokManager:
    """ngrok 隧道管理器

    管理 ngrok 隧道的生命周期，包括启动、停止、状态监控等
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化 ngrok 管理器

        Args:
            logger: 日志记录器实例
        """
        self.logger = logger or logging.getLogger(__name__)
        self.tunnel = None
        self.public_url = None
        self.is_running = False
        self._monitor_thread = None
        self._stop_monitor = threading.Event()

        if not PYNGROK_AVAILABLE:
            self.logger.warning("pyngrok 未安装，ngrok 功能将不可用")

    def is_ngrok_available(self) -> bool:
        """检查 ngrok 是否可用"""
        return PYNGROK_AVAILABLE

    def set_authtoken(self, authtoken: str) -> bool:
        """
        设置 ngrok authtoken

        Args:
            authtoken: ngrok 认证令牌

        Returns:
            bool: 设置是否成功
        """
        if not PYNGROK_AVAILABLE:
            self.logger.error("pyngrok 未安装")
            return False

        try:
            # 使用 suppress_stdout_stderr 避免 GUI 应用中的输出问题
            with suppress_stdout_stderr():
                ngrok.set_auth_token(authtoken)
            self.logger.info("ngrok authtoken 设置成功")
            return True
        except Exception as e:
            self.logger.error(f"设置 ngrok authtoken 失败: {e}")
            return False

    def start_tunnel(
        self,
        port: int,
        authtoken: Optional[str] = None,
        region: str = "us",
        protocol: str = "http"
    ) -> Optional[str]:
        """
        启动 ngrok 隧道

        Args:
            port: 本地服务端口
            authtoken: ngrok 认证令牌（可选）
            region: ngrok 服务器区域（us, eu, ap, au, sa, jp, in）
            protocol: 协议类型（http, tcp）

        Returns:
            Optional[str]: 公网 URL，失败返回 None
        """
        if not PYNGROK_AVAILABLE:
            self.logger.error("pyngrok 未安装，无法启动隧道")
            return None

        if self.is_running:
            self.logger.warning("ngrok 隧道已在运行")
            return self.public_url

        try:
            # 设置 authtoken（如果提供）
            if authtoken:
                self.set_authtoken(authtoken)

            # 配置 ngrok
            conf.get_default().region = region

            # 启动隧道
            self.logger.info(f"启动 ngrok 隧道: port={port}, region={region}, protocol={protocol}")

            # 使用 suppress_stdout_stderr 避免 GUI 应用中的输出问题
            # 这在首次运行时下载 ngrok 二进制文件时特别重要
            with suppress_stdout_stderr():
                self.tunnel = ngrok.connect(
                    port,
                    protocol,
                    bind_tls=True  # 强制使用 HTTPS
                )

            self.public_url = self.tunnel.public_url
            self.is_running = True

            self.logger.info(f"ngrok 隧道已启动: {self.public_url}")

            # 启动监控线程
            self._start_monitor()

            return self.public_url

        except PyngrokNgrokError as e:
            self.logger.error(f"ngrok 启动失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"启动 ngrok 隧道时发生错误: {e}", exc_info=True)
            return None

    def stop_tunnel(self, async_mode: bool = False, callback=None):
        """停止 ngrok 隧道

        Args:
            async_mode: 是否在后台线程异步执行停止操作
            callback: 异步模式下，停止完成后的回调函数
        """
        if not self.is_running:
            self.logger.warning("ngrok 隧道未运行")
            return

        if async_mode:
            # 异步模式：在后台线程执行停止操作
            def async_stop():
                self._do_stop_tunnel()
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.error(f"执行停止回调时出错: {e}")

            stop_thread = threading.Thread(target=async_stop, daemon=True)
            stop_thread.start()
        else:
            # 同步模式：直接执行
            self._do_stop_tunnel()

    def _do_stop_tunnel(self):
        """执行实际的停止操作（内部方法）"""
        # 立即标记为非运行状态，防止重复调用
        self.is_running = False

        # 停止监控线程（不等待，让它自然结束）
        self._stop_monitor.set()

        # 尝试关闭隧道，设置较短的超时
        tunnel_closed = False
        if self.tunnel:
            try:
                # 使用 suppress_stdout_stderr 避免输出干扰
                with suppress_stdout_stderr():
                    ngrok.disconnect(self.tunnel.public_url)
                self.logger.info(f"ngrok 隧道已关闭: {self.public_url}")
                tunnel_closed = True
            except Exception as e:
                # 记录错误但继续清理本地状态
                self.logger.warning(f"关闭 ngrok 隧道时出错（可能是超时），将强制清理本地状态: {e}")

        # 清理本地状态
        self.tunnel = None
        self.public_url = None
        self._stop_monitor.clear()

        # 等待监控线程结束（最多1秒）
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1)

        if tunnel_closed:
            self.logger.info("ngrok 隧道已完全停止")
        else:
            self.logger.info("ngrok 本地状态已清理（隧道可能仍在远程运行）")

    def get_status(self) -> Dict[str, Any]:
        """
        获取 ngrok 状态信息

        Returns:
            Dict: 包含状态信息的字典
        """
        status = {
            "is_running": self.is_running,
            "public_url": self.public_url,
            "available": PYNGROK_AVAILABLE
        }

        if self.is_running and self.tunnel:
            try:
                status.update({
                    "name": self.tunnel.name,
                    "proto": self.tunnel.proto,
                    "config": self.tunnel.config
                })
            except Exception as e:
                self.logger.warning(f"获取隧道详细信息失败: {e}")

        return status

    def get_tunnels(self) -> list:
        """
        获取所有活动的 ngrok 隧道

        Returns:
            list: 隧道列表
        """
        if not PYNGROK_AVAILABLE:
            return []

        try:
            tunnels = ngrok.get_tunnels()
            return [
                {
                    "name": t.name,
                    "public_url": t.public_url,
                    "proto": t.proto,
                    "config": t.config
                }
                for t in tunnels
            ]
        except Exception as e:
            self.logger.error(f"获取隧道列表失败: {e}")
            return []

    def kill_all(self, async_mode: bool = False):
        """终止所有 ngrok 进程（强制清理）

        Args:
            async_mode: 是否在后台线程异步执行
        """
        # 立即标记为非运行状态
        self.is_running = False

        if not PYNGROK_AVAILABLE:
            return

        if async_mode:
            # 异步模式：在后台线程执行
            def async_kill():
                self._do_kill_all()

            kill_thread = threading.Thread(target=async_kill, daemon=True)
            kill_thread.start()
        else:
            # 同步模式：直接执行
            self._do_kill_all()

    def _do_kill_all(self):
        """执行实际的强制终止操作（内部方法）"""
        # 停止监控线程（不等待）
        self._stop_monitor.set()

        try:
            # 尝试终止所有 ngrok 进程
            with suppress_stdout_stderr():
                ngrok.kill()
            self.logger.info("所有 ngrok 进程已终止")
        except Exception as e:
            self.logger.warning(f"终止 ngrok 进程时出错: {e}")
        finally:
            # 清理本地状态
            self.tunnel = None
            self.public_url = None
            self._stop_monitor.clear()

            # 等待监控线程结束（最多1秒）
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=1)

    def _start_monitor(self):
        """启动监控线程"""
        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_tunnel,
            daemon=True
        )
        self._monitor_thread.start()

    def _monitor_tunnel(self):
        """监控隧道状态（在后台线程中运行）- 永久监控模式"""
        consecutive_errors = 0

        while not self._stop_monitor.is_set():
            try:
                if self.is_running and self.tunnel:
                    # 检查隧道是否仍然有效
                    tunnels = ngrok.get_tunnels()
                    tunnel_exists = any(
                        t.public_url == self.public_url for t in tunnels
                    )

                    if not tunnel_exists:
                        self.logger.warning("ngrok 隧道意外断开")
                        self.is_running = False
                        break

                    # 重置错误计数（成功时）
                    if consecutive_errors > 0:
                        self.logger.info("ngrok 监控恢复正常")
                        consecutive_errors = 0

                time.sleep(5)  # 每5秒检查一次

            except Exception as e:
                consecutive_errors += 1
                self.logger.warning(f"监控隧道时发生错误 (已连续 {consecutive_errors} 次): {e}")

                # 永不停止监控，持续重试
                # 等待较长时间后重试
                time.sleep(10)

    def __del__(self):
        """析构函数：确保资源清理"""
        try:
            if self.is_running:
                # 使用异步模式快速清理，避免阻塞程序退出
                self.stop_tunnel(async_mode=True)
        except:
            pass
