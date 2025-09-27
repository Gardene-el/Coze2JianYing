# 开源的Coze剪映小助手

一个基于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 构建的剪映草稿生成工具，专为 Coze 平台设计。

## 特性

- 🎬 基于 pyJianYingDraft 的强大剪映草稿生成能力
- 🤖 专为 Coze 平台优化的交互体验
- 🐍 纯 Python 实现，易于扩展和自定义
- 📦 标准的 Python 项目结构

## 安装

### 从源码安装

1. 克隆仓库：
```bash
git clone https://github.com/Gardene-el/CozeJianYingAssistent.git
cd CozeJianYingAssistent
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装项目：
```bash
pip install -e .
```

## 使用方法

### 命令行使用

```bash
coze-jianying
```

### Python 代码使用

```python
from coze_jianying_assistant import CozeJianYingAssistant

# 创建助手实例
assistant = CozeJianYingAssistant()

# 创建新的剪映草稿
draft = assistant.create_draft("我的项目")

# 处理视频文件
assistant.process_video("path/to/video.mp4")

# 导出草稿
assistant.export_draft()
```

## 依赖项目

本项目基于以下开源项目构建：

- [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) - 轻量、灵活、易上手的Python剪映草稿生成及导出工具

## 开发

### 项目结构

```
CozeJianYingAssistent/
├── coze_jianying_assistant/    # 主包目录
│   ├── __init__.py            # 包初始化文件
│   └── main.py                # 主程序入口
├── requirements.txt           # 项目依赖
├── setup.py                  # 安装配置
├── .gitignore               # Git忽略文件
├── LICENSE                  # 开源协议
└── README.md               # 项目说明
```

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！
