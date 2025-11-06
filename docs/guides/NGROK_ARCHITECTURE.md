# ngrok 集成架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Coze2JianYing Application                      │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              GUI - Cloud Service Tab (云端服务)                │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────┐      │    │
│  │  │          FastAPI Service Management                  │      │    │
│  │  │  • Port configuration                                │      │    │
│  │  │  • Start/Stop service                                │      │    │
│  │  │  • Service status & logs                             │      │    │
│  │  │  • Local URL: http://localhost:8000                  │      │    │
│  │  └─────────────────────────────────────────────────────┘      │    │
│  │                          ↓                                      │    │
│  │  ┌─────────────────────────────────────────────────────┐      │    │
│  │  │          ngrok Tunnel Management (NEW!)              │      │    │
│  │  │                                                       │      │    │
│  │  │  Configuration:                                      │      │    │
│  │  │  • Authtoken (optional, with show/hide)             │      │    │
│  │  │  • Region selection (us/eu/ap/au/sa/jp/in)          │      │    │
│  │  │                                                       │      │    │
│  │  │  Status Display:                                     │      │    │
│  │  │  • Status indicator (🔴/🟢)                         │      │    │
│  │  │  • Public URL display                                │      │    │
│  │  │  • Copy to clipboard button                          │      │    │
│  │  │                                                       │      │    │
│  │  │  Controls:                                           │      │    │
│  │  │  • Start ngrok button                                │      │    │
│  │  │  • Stop ngrok button                                 │      │    │
│  │  │                                                       │      │    │
│  │  │  Logs:                                               │      │    │
│  │  │  • Real-time ngrok operation logs                    │      │    │
│  │  │  • Clear log button                                  │      │    │
│  │  └─────────────────────────────────────────────────────┘      │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              Backend - NgrokManager                             │    │
│  │              (app/utils/ngrok_manager.py)                       │    │
│  │                                                                 │    │
│  │  Core Features:                                                │    │
│  │  • start_tunnel(port, authtoken, region)                       │    │
│  │  • stop_tunnel()                                               │    │
│  │  • get_status() - Real-time status                            │    │
│  │  • set_authtoken(token)                                        │    │
│  │  • _monitor_tunnel() - Background monitoring                   │    │
│  │                                                                 │    │
│  │  Dependencies:                                                 │    │
│  │  • pyngrok library                                             │    │
│  │  • threading for monitoring                                    │    │
│  │  • logging for debugging                                       │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    ┌───────────────────────────┐
                    │      pyngrok Library       │
                    │  (ngrok Python wrapper)    │
                    └───────────────────────────┘
                                    ↓
                    ┌───────────────────────────┐
                    │     ngrok Binary          │
                    │  (Auto-downloaded)        │
                    └───────────────────────────┘
                                    ↓
                    ┌───────────────────────────┐
                    │    ngrok Cloud Service     │
                    │  (https://ngrok.com)      │
                    └───────────────────────────┘
                                    ↓
                      Public URL Generated
                 (e.g., https://abc123.ngrok.io)
                                    ↓
                    ┌───────────────────────────┐
                    │      Coze Platform        │
                    │  • Configures plugin      │
                    │  • Calls API endpoints    │
                    │  • Receives responses     │
                    └───────────────────────────┘
```

## 数据流向

### 启动流程
```
User Action (GUI)
    ↓
CloudServiceTab._start_ngrok()
    ↓
NgrokManager.start_tunnel(port, authtoken, region)
    ↓
pyngrok.ngrok.connect(port, protocol)
    ↓
ngrok binary downloads (first time)
    ↓
Tunnel established with ngrok cloud
    ↓
Public URL returned
    ↓
GUI updated with URL
    ↓
User copies URL
    ↓
User configures Coze plugin
```

### 请求流程
```
Coze Platform
    ↓
HTTPS Request to public URL
(e.g., https://abc123.ngrok.io/api/draft/create)
    ↓
ngrok Cloud Service
    ↓
ngrok Tunnel
    ↓
Local FastAPI Service (localhost:8000)
    ↓
Process request
    ↓
Response back through tunnel
    ↓
Coze Platform receives response
```

## 组件职责

### 1. CloudServiceTab (GUI)
- 提供用户界面
- 管理用户输入
- 显示状态和日志
- 调用 NgrokManager

### 2. NgrokManager (Backend)
- 管理 ngrok 生命周期
- 处理隧道启停
- 监控隧道状态
- 资源清理

### 3. pyngrok (Library)
- Python 到 ngrok 的桥接
- 管理 ngrok 二进制文件
- 提供 Python API

### 4. ngrok (Service)
- 建立安全隧道
- 提供公网访问
- 路由请求

## 安全考虑

```
Security Layers:

1. Application Level
   - FastAPI service with CORS
   - Input validation
   - Error handling

2. Tunnel Level
   - HTTPS encryption (bind_tls=True)
   - ngrok authtoken authentication
   - Region-based routing

3. Network Level
   - TLS/SSL encryption
   - ngrok cloud security
   - DDoS protection (ngrok)

4. User Level
   - Token visibility toggle
   - Manual start/stop control
   - Log monitoring
```

## 性能特性

```
Performance Characteristics:

Latency: Local service + Tunnel overhead
  • Local: < 1ms
  • Tunnel: + 50-200ms (region dependent)
  • Total: ~50-200ms

Bandwidth:
  • Free tier: Limited
  • Paid tier: Higher limits
  
Connections:
  • Free tier: Limited concurrent
  • Paid tier: Higher concurrency

Stability:
  • Monitor thread checks every 5 seconds
  • Auto-reconnect on failure detection
  • Graceful shutdown handling
```
