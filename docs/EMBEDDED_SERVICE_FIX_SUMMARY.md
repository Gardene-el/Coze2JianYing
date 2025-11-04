# 打包环境嵌入式服务修复总结

## 🎯 问题概述

在使用 PyInstaller 打包后,尝试在 GUI 中启动 FastAPI 服务时出现以下问题:

1. **多窗口启动**: 使用 multiprocessing.Process 启动服务时,Windows spawn 模式导致重复执行整个 exe,创建多个 GUI 窗口
2. **函数序列化失败**: 嵌套函数无法被 pickle 序列化,抛出 AttributeError
3. **日志配置错误**: uvicorn 日志系统在打包环境中找不到配置文件
4. **端口占用卡死**: 应用关闭时服务未正确停止,导致端口被占用,再次启动时卡死

## 💡 解决方案

### 1. 使用 threading.Thread 替代 multiprocessing.Process

**核心改变**: 从多进程切换到多线程

```python
# ❌ 之前的方案 (multiprocessing)
from multiprocessing import Process
process = Process(target=run_server)
process.start()

# ✅ 修复后的方案 (threading)
from threading import Thread
thread = Thread(target=run_server, daemon=True)
thread.start()
```

**为什么有效**:
- 线程在同一进程内运行,共享内存空间
- 不需要序列化函数,可以直接访问
- 不会重新执行 exe 文件
- 启动开销小,通信简单

### 2. 禁用 uvicorn 日志配置

```python
config = uvicorn.Config(
    app=app,
    host="127.0.0.1",
    port=port,
    log_level="error",
    access_log=False,
    log_config=None  # 🔑 关键修复
)
```

### 3. 添加资源清理机制

#### 方法 1: 析构函数
```python
def __del__(self):
    """对象销毁时停止服务"""
    try:
        if self.service_running:
            self._stop_service()
    except:
        pass
```

#### 方法 2: atexit 注册
```python
import atexit

def __init__(self, parent):
    # ... 初始化代码 ...
    atexit.register(self._cleanup_on_exit)

def _cleanup_on_exit(self):
    """应用退出时清理服务"""
    try:
        if self.service_running:
            self._stop_service()
    except:
        pass
```

#### 方法 3: 异常捕获
```python
try:
    self.uvicorn_server = uvicorn.Server(config)
    asyncio.run(self.uvicorn_server.serve())
except OSError as e:
    if e.errno == 10048:  # 端口占用
        self._append_to_info("❌ 端口已被占用", "error")
        self.service_running = False
```

### 4. 优雅停止服务

```python
def _stop_service(self):
    if not self.service_running:
        return
    
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen and self.uvicorn_server:
        # 打包环境: 设置停止标志
        self.uvicorn_server.should_exit = True
        # 等待线程结束
        if self.service_thread and self.service_thread.is_alive():
            self.service_thread.join(timeout=5)
    else:
        # 源码环境: 终止子进程
        if self.service_process:
            self.service_process.terminate()
            self.service_process.wait(timeout=5)
    
    self.service_running = False
```

## 📋 修改文件清单

### app/gui/local_service_tab.py
- 添加 `import atexit`
- 移除 multiprocessing 相关导入
- 添加 `__del__` 析构函数
- 添加 `_cleanup_on_exit` 清理函数
- 修改 `_start_embedded_service` 使用 threading.Thread
- 优化 `_stop_service` 支持线程停止
- uvicorn.Config 设置 `log_config=None`
- 添加 OSError 异常处理

## ✅ 验证步骤

### 测试 1: 基本启动和停止
```powershell
# 1. 运行打包后的程序
dist\CozeJianYingDraftGenerator.exe

# 2. 在"本地服务"标签页点击"启动服务"
# 3. 检查是否只有一个窗口
# 4. 访问 http://localhost:8000/docs 验证服务正常
# 5. 点击"停止服务"
# 6. 关闭程序
```

### 测试 2: 端口占用场景
```powershell
# 1. 先手动占用端口
python -m http.server 8000

# 2. 启动打包的程序
dist\CozeJianYingDraftGenerator.exe

# 3. 尝试启动服务
# 预期: 显示"端口已被占用"错误,程序不卡死

# 4. 关闭 python http.server
# 5. 再次尝试启动服务
# 预期: 成功启动
```

### 测试 3: 应用退出清理
```powershell
# 1. 启动程序并启动服务
# 2. 直接关闭窗口(不点停止服务)
# 3. 立即重新启动程序
# 4. 尝试启动服务
# 预期: 能够成功启动(端口已被释放)
```

## 📊 技术对比

| 特性 | multiprocessing | threading |
|------|-----------------|-----------|
| 打包环境适用性 | ❌ 失败 | ✅ 成功 |
| 函数序列化 | 需要 pickle | 不需要 |
| 启动方式 | 重新执行 exe | 创建线程 |
| 资源开销 | 大 | 小 |
| 通信复杂度 | 复杂 | 简单 |
| GUI 窗口影响 | 创建多个窗口 | 不影响 |

## 🔗 相关文档

- [完整技术解释](./THREAD_VS_PROCESS_EXPLANATION.md) - 详细的线程 vs 进程说明
- [开发历程](./guides/DEVELOPMENT_ROADMAP.md) - 功能开发过程
- [PyInstaller 多进程注意事项](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing)

## 📝 后续改进建议

1. **日志系统**: 考虑为嵌入式服务添加专门的日志面板
2. **端口检测**: 启动前自动检测端口可用性
3. **服务状态**: 实时监控服务健康状态
4. **错误恢复**: 服务崩溃时自动重启机制
