# ngrok 重启错误修复文档

## 问题描述

用户在快速重启 ngrok 时遇到以下错误：

### 错误 1: 超时错误
当用户点击"停止 ngrok"后立即启动 ngrok（终端未关闭），出现：
```
ngrok client exception, URLError: timed out
```

### 错误 2: 连接重置错误
关闭终端后重启时，出现：
```
[WinError 10054] 远程主机强迫关闭了一个现有的连接。
ConnectionResetError
```

## 根本原因分析

1. **陈旧进程残留**: 停止 ngrok 后，ngrok 进程或连接可能未完全清理
2. **快速重启冲突**: 新的 ngrok 连接尝试时，旧连接仍在使用相关资源
3. **错误处理不足**: 原代码没有处理连接重置和超时等临时性错误
4. **无重试机制**: 遇到临时性错误时直接失败，不尝试恢复

## 解决方案

### 1. 添加陈旧进程清理机制

在 `ngrok_manager.py` 中新增 `_cleanup_stale_ngrok_processes()` 方法：

```python
def _cleanup_stale_ngrok_processes(self):
    """清理陈旧的 ngrok 进程和连接
    
    在启动新隧道前调用，确保没有残留的 ngrok 进程或连接
    """
    if not PYNGROK_AVAILABLE:
        return
    
    try:
        # 检查是否有活动的隧道
        existing_tunnels = ngrok.get_tunnels()
        if existing_tunnels:
            # 断开所有现有隧道
            for tunnel in existing_tunnels:
                ngrok.disconnect(tunnel.public_url)
            time.sleep(0.5)  # 给时间让连接完全关闭
    except Exception as e:
        # 如果检查失败，强制终止所有 ngrok 进程
        ngrok.kill()
        time.sleep(1)  # 等待进程完全终止
    
    # 清理本地状态
    self.tunnel = None
    self.public_url = None
    self.is_running = False
```

**关键点**：
- 在启动新隧道前自动调用
- 检测并断开现有隧道
- 失败时强制终止所有进程
- 清理本地状态以确保一致性

### 2. 实现重试机制

修改 `start_tunnel()` 方法，添加智能重试逻辑：

```python
def start_tunnel(self, port: int, ...) -> Optional[str]:
    # 清理可能存在的陈旧进程
    self._cleanup_stale_ngrok_processes()
    
    max_retries = 2
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # 尝试启动隧道
            self.tunnel = ngrok.connect(port, protocol, bind_tls=True)
            # ...成功后返回
            return self.public_url
            
        except (PyngrokNgrokURLError, ConnectionResetError, ConnectionError, OSError) as e:
            # 连接错误，可能是陈旧进程导致
            retry_count += 1
            if retry_count <= max_retries:
                # 强制清理后重试
                ngrok.kill()
                time.sleep(1)
            else:
                # 重试失败
                return None
```

**关键点**：
- 最多重试 2 次（总共 3 次尝试）
- 特别处理连接相关错误
- 重试前强制清理所有 ngrok 进程
- 适当的等待时间确保进程完全终止

### 3. 增强异常处理

导入更多 pyngrok 异常类型：

```python
from pyngrok.exception import (
    PyngrokError, 
    PyngrokNgrokError, 
    PyngrokNgrokURLError,      # 新增：URL 连接错误
    PyngrokNgrokHTTPError      # 新增：HTTP 错误
)
```

捕获更多类型的错误：
- `ConnectionResetError`: 连接被重置
- `ConnectionError`: 一般连接错误
- `OSError`: 系统级错误
- `PyngrokNgrokURLError`: ngrok URL 错误

### 4. 改进用户错误信息

在 `cloud_service_tab.py` 中更新 `_on_ngrok_start_failed()` 方法：

```python
def _on_ngrok_start_failed(self, error_msg: str = ""):
    # 根据错误类型提供针对性建议
    if "timed out" in error_msg.lower():
        error_text = """启动 ngrok 隧道超时。
        
可能的原因:
1. 上一个 ngrok 进程未完全终止
2. 网络连接不稳定
3. ngrok 服务器响应缓慢

建议:
- 等待几秒后再次尝试
- 检查网络连接
- 尝试更换区域（region）设置"""
    
    elif "connection" in error_msg.lower() and "reset" in error_msg.lower():
        error_text = """连接被重置或拒绝。
        
可能的原因:
1. 陈旧的 ngrok 进程残留
2. 端口冲突
3. 防火墙阻止连接

建议:
- 已自动尝试清理，请重启应用后再试
- 检查防火墙设置
- 确认本地服务正在运行"""
    # ... 其他错误类型
```

**关键点**：
- 根据错误类型提供具体建议
- 告知用户系统已尝试的自动修复措施
- 给出明确的下一步操作建议

## 技术细节

### 时序改进

**修复前**:
```
1. 用户点击"停止" → stop_tunnel()
2. 异步停止开始，但可能未完成
3. 用户点击"启动" → start_tunnel()
4. 尝试连接到可能仍在运行的 ngrok 进程
5. ❌ 超时或连接错误
```

**修复后**:
```
1. 用户点击"停止" → stop_tunnel(async_mode=True)
2. 异步停止开始
3. 用户点击"启动" → start_tunnel()
4. ✅ _cleanup_stale_ngrok_processes() 清理残留
5. 尝试连接（最多重试 2 次）
6. ✅ 成功启动或提供详细错误信息
```

### 错误恢复流程

```
启动 ngrok
    ↓
清理陈旧进程
    ↓
尝试连接
    ↓
成功? ───Yes→ 返回 URL
    ↓
   No
    ↓
连接错误? ───Yes→ 强制清理 + 重试（最多2次）
    ↓                ↓
   No               成功? ───Yes→ 返回 URL
    ↓                ↓
其他错误             No
    ↓                ↓
记录错误并返回 None ←┘
```

## 测试验证

### 自动化测试

创建了全面的测试套件：

1. **test_ngrok_restart.py** - 重启功能测试
   - 清理陈旧进程测试
   - 多次清理调用测试
   - 无效端口处理测试
   - 异常处理测试
   - 重试逻辑验证

2. **manual_test_ngrok_restart.py** - 手动测试脚本
   - 快速重启场景模拟
   - 多次快速重启压力测试
   - 错误信息质量验证

### 测试结果

```
✅ 所有测试通过
- 快速重启场景: 通过
- 多次快速重启: 通过
- 错误信息质量: 通过
```

## 向后兼容性

所有改动均保持 100% 向后兼容：

- ✅ 现有 API 接口未更改
- ✅ 现有功能行为保持一致
- ✅ 只增强错误处理和恢复能力
- ✅ 不影响正常使用场景

## 用户影响

### 改进前
- ❌ 快速重启经常失败
- ❌ 需要手动重启应用
- ❌ 错误信息不明确

### 改进后
- ✅ 快速重启自动恢复
- ✅ 智能清理和重试
- ✅ 详细的错误诊断和建议

## 最佳实践建议

虽然修复后可以支持快速重启，但仍建议：

1. **正常停止**: 等待 ngrok 完全停止（显示"未启动"）后再启动
2. **遇到错误**: 如果仍遇到问题，等待 5-10 秒后重试
3. **持续问题**: 重启整个应用以完全清理状态

## 未来改进空间

1. **进程监控**: 添加 ngrok 进程健康检查
2. **自动恢复**: 检测到异常时自动重启
3. **状态持久化**: 保存 ngrok 配置，支持断点恢复
4. **日志增强**: 更详细的诊断日志

## 相关文件

- `app/utils/ngrok_manager.py` - 核心修复
- `app/gui/cloud_service_tab.py` - UI 改进
- `tests/test_ngrok_restart.py` - 自动化测试
- `tests/manual_test_ngrok_restart.py` - 手动测试脚本

## 修复版本

- 修复日期: 2025-11-08
- 修复分支: `copilot/fix-ngrok-start-error`
- Issue: #[待填写]
- PR: #[待填写]
