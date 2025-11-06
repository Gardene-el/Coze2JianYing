"""
ngrok 管理器模块

用于管理 ngrok 隧道，提供公网访问本地服务的能力
"""
import threading
import time
from typing import Optional, Dict, Any
import logging

try:
    from pyngrok import ngrok, conf
    from pyngrok.exception import PyngrokError, PyngrokNgrokError
    PYNGROK_AVAILABLE = True
except ImportError:
    PYNGROK_AVAILABLE = False


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
    
    def stop_tunnel(self):
        """停止 ngrok 隧道"""
        if not self.is_running:
            self.logger.warning("ngrok 隧道未运行")
            return
        
        try:
            # 停止监控线程
            self._stop_monitor.set()
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=3)
            
            # 关闭隧道
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
                self.logger.info(f"ngrok 隧道已关闭: {self.public_url}")
            
            # 重置状态
            self.tunnel = None
            self.public_url = None
            self.is_running = False
            self._stop_monitor.clear()
            
        except Exception as e:
            self.logger.error(f"停止 ngrok 隧道时发生错误: {e}", exc_info=True)
    
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
    
    def kill_all(self):
        """终止所有 ngrok 进程"""
        if not PYNGROK_AVAILABLE:
            return
        
        try:
            ngrok.kill()
            self.tunnel = None
            self.public_url = None
            self.is_running = False
            self.logger.info("所有 ngrok 进程已终止")
        except Exception as e:
            self.logger.error(f"终止 ngrok 进程失败: {e}")
    
    def _start_monitor(self):
        """启动监控线程"""
        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_tunnel,
            daemon=True
        )
        self._monitor_thread.start()
    
    def _monitor_tunnel(self):
        """监控隧道状态（在后台线程中运行）"""
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
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"监控隧道时发生错误: {e}")
                break
    
    def __del__(self):
        """析构函数：确保资源清理"""
        try:
            if self.is_running:
                self.stop_tunnel()
        except:
            pass
