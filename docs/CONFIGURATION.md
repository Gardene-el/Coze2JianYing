# 应用配置说明

## 概述

本应用使用统一的配置系统来管理文件和数据存储路径，支持跨平台部署（Windows、Linux、Mac）和云端/本地运行模式。

## 配置方式

### 方式一：环境变量（推荐用于云端部署）

通过设置环境变量来自定义存储路径：

```bash
# 云端模式开关（设置后将使用 /app/data 作为根目录）
export JIANYING_CLOUD_MODE=true

# 数据存储根目录（所有数据的基础目录）
export JIANYING_DATA_ROOT=/app/data

# 各子目录（可选，不设置则使用默认值）
export JIANYING_DRAFTS_DIR=/app/data/drafts
export JIANYING_SEGMENTS_DIR=/app/data/segments
export JIANYING_MATERIALS_CACHE_DIR=/app/data/materials_cache
export JIANYING_OUTPUT_DIR=/app/data/output
export JIANYING_LOG_DIR=/app/data/logs
```

### 方式二：使用默认路径

如果不设置环境变量，系统将根据运行平台自动选择合适的默认路径：

#### Windows 平台
- 数据根目录：`%APPDATA%\JianyingAssistant` 或 `%LOCALAPPDATA%\JianyingAssistant`
- 草稿目录：`%APPDATA%\JianyingAssistant\drafts`
- 片段目录：`%APPDATA%\JianyingAssistant\segments`
- 素材缓存：`%APPDATA%\JianyingAssistant\materials_cache`
- 输出目录：`%APPDATA%\JianyingAssistant\output`
- 日志目录：`%APPDATA%\JianyingAssistant\logs`

#### Linux/Mac 平台
- 数据根目录：`~/.local/share/jianying_assistant`
- 草稿目录：`~/.local/share/jianying_assistant/drafts`
- 片段目录：`~/.local/share/jianying_assistant/segments`
- 素材缓存：`~/.local/share/jianying_assistant/materials_cache`
- 输出目录：`~/.local/share/jianying_assistant/output`
- 日志目录：`~/.local/share/jianying_assistant/logs`

#### 云端环境（设置了 JIANYING_CLOUD_MODE=true）
- 数据根目录：`/app/data`
- 草稿目录：`/app/data/drafts`
- 片段目录：`/app/data/segments`
- 素材缓存：`/app/data/materials_cache`
- 输出目录：`/app/data/output`
- 日志目录：`/app/data/logs`

## 配置优先级

路径配置的优先级从高到低：

1. **环境变量** - 最高优先级
2. **云端模式判断** - 通过 `JIANYING_CLOUD_MODE` 环境变量
3. **平台默认路径** - Windows/Linux/Mac 各自的标准路径
4. **临时目录** - 最后备选方案

## Docker 部署示例

### Dockerfile 示例

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 复制应用代码
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV JIANYING_CLOUD_MODE=true
ENV JIANYING_DATA_ROOT=/app/data

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "-m", "uvicorn", "app.api_main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml 示例

```yaml
version: '3.8'

services:
  jianying-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JIANYING_CLOUD_MODE=true
      - JIANYING_DATA_ROOT=/app/data
    volumes:
      # 持久化数据存储
      - jianying-data:/app/data
    restart: unless-stopped

volumes:
  jianying-data:
    driver: local
```

### 直接运行 Docker 容器

```bash
# 构建镜像
docker build -t jianying-assistant .

# 运行容器（带数据卷持久化）
docker run -d \
  --name jianying-assistant \
  -p 8000:8000 \
  -e JIANYING_CLOUD_MODE=true \
  -e JIANYING_DATA_ROOT=/app/data \
  -v jianying-data:/app/data \
  jianying-assistant
```

## Kubernetes 部署示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jianying-config
data:
  JIANYING_CLOUD_MODE: "true"
  JIANYING_DATA_ROOT: "/app/data"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jianying-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jianying-assistant
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jianying-assistant
  template:
    metadata:
      labels:
        app: jianying-assistant
    spec:
      containers:
      - name: jianying-assistant
        image: jianying-assistant:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: jianying-config
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: jianying-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: jianying-assistant
spec:
  selector:
    app: jianying-assistant
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 本地开发配置

本地开发时，可以通过 `.env` 文件配置（需要使用 python-dotenv 库）：

```bash
# .env 文件
JIANYING_DATA_ROOT=./dev_data
JIANYING_DRAFTS_DIR=./dev_data/drafts
JIANYING_SEGMENTS_DIR=./dev_data/segments
JIANYING_MATERIALS_CACHE_DIR=./dev_data/materials_cache
JIANYING_OUTPUT_DIR=./dev_data/output
JIANYING_LOG_DIR=./dev_data/logs
```

然后在启动脚本中加载：

```python
from dotenv import load_dotenv
load_dotenv()

from app.api_main import app
```

## 查看当前配置

应用启动后，可以通过 API 查看当前配置：

```bash
curl http://localhost:8000/api/config
```

或在 Python 代码中：

```python
from app.config import get_config

config = get_config()
print(config.to_dict())
```

## 注意事项

1. **数据持久化**：在容器环境中，务必使用卷（Volume）来持久化 `/app/data` 目录
2. **权限问题**：确保应用有权限读写配置的目录
3. **磁盘空间**：素材缓存和输出目录可能占用较多空间，请预留足够磁盘
4. **路径分隔符**：配置系统会自动处理不同平台的路径分隔符，无需手动处理
5. **环境变量更新**：修改环境变量后需要重启应用才能生效

## 迁移指南

### 从旧版本迁移

如果你之前使用的是硬编码路径（`/tmp/jianying_assistant`），可以通过以下方式迁移：

```bash
# 1. 设置环境变量指向旧数据目录
export JIANYING_DATA_ROOT=/tmp/jianying_assistant

# 2. 启动应用，应用会继续使用旧目录

# 3. 迁移数据到新位置（可选）
mkdir -p ~/.local/share/jianying_assistant
cp -r /tmp/jianying_assistant/* ~/.local/share/jianying_assistant/

# 4. 更新环境变量或删除环境变量使用默认路径
unset JIANYING_DATA_ROOT
```

## 故障排查

### 问题1：找不到数据目录

**症状**：应用报错无法创建或访问目录

**解决方案**：
1. 检查环境变量是否正确设置
2. 检查目录权限
3. 查看应用日志中的配置信息

### 问题2：云端部署数据丢失

**症状**：容器重启后数据消失

**解决方案**：
1. 确保使用了持久化卷
2. 检查卷挂载路径是否正确
3. 验证 `JIANYING_DATA_ROOT` 环境变量指向卷挂载点

### 问题3：跨平台路径问题

**症状**：在不同操作系统间路径格式不兼容

**解决方案**：
1. 使用环境变量而非硬编码路径
2. 让配置系统自动处理路径格式
3. 避免在代码中直接拼接路径字符串
