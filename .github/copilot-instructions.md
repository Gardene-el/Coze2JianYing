# Copilot Instructions for CozeJianYingAssistent

## 项目概述

这是一个专为 Coze 平台设计的剪映草稿生成工具，基于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 构建。本项目用于演示和开发将来会在 Coze 插件中使用的 Python 工具函数。

## Coze 平台特性与约束

### 代码架构约束
- **无共同头文件概念**：每个工具函数脚本文件需要重复定义所需的自定义类和工具函数
- **文件系统限制**：默认可读写文件夹是 `/tmp`，大小限制 512MB，生命周期管理复杂
- **函数式风格**：避免在本地空间或脚本中存储状态变量，所有数据都应该通过参数传递

### 标准代码结构
每个 Coze 工具函数必须遵循以下模板：

```python
from runtime import Args
from typings.custom_handler_name.custom_handler_name import Input, Output

"""
Each file needs to export a function named `handler`. This function is the entrance to the Tool.

Parameters:
args: parameters of the entry function.
args.input - input parameters, you can get test input value by args.input.xxx.
args.logger - logger instance used to print logs, injected by runtime.

Remember to fill in input/output in Metadata, it helps LLM to recognize and use tool.

Return:
The return data of the function, which should match the declared output parameters.
"""
def handler(args: Args[Input])->Output:
    return {"message": "Hello, world!"}
```

## 项目结构规划

### 核心组件

#### 1. 工具函数脚本 (Tool Function Scripts)
位置：`tools/` 目录

每个工具函数脚本应包含：
- 主要的 `handler` 函数
- 必要的数据类型定义（因为无共同头文件）
- 所需的工具函数实现
- 错误处理和日志记录
- 同名的 README.md 文档

#### 2. 数据结构脚本 (Data Structure Scripts)
位置：`data_structures/` 目录

包含可复用的数据结构定义：
- 剪映草稿相关的数据模型
- 视频处理参数类
- 音频处理参数类
- 文本和字幕相关类
- 同名的 README.md 文档

### 目录结构
```
CozeJianYingAssistent/
├── coze_jianying_assistant/    # 主包目录
├── tools/                      # Coze 工具函数脚本
│   ├── create_draft/
│   │   ├── handler.py         # 创建剪映草稿工具
│   │   └── README.md          # 工具说明文档
│   ├── process_video/
│   │   ├── handler.py         # 视频处理工具
│   │   └── README.md
│   └── export_draft/
│       ├── handler.py         # 导出草稿工具
│       └── README.md
├── data_structures/           # 数据结构定义
│   ├── draft_models/
│   │   ├── models.py         # 草稿相关数据模型
│   │   └── README.md
│   ├── media_models/
│   │   ├── models.py         # 媒体文件相关模型
│   │   └── README.md
│   └── processing_models/
│       ├── models.py         # 处理参数模型
│       └── README.md
└── examples/                  # 使用示例
```

## 编码指南

### Coze 工具函数开发规范

1. **函数入口**：
   - 必须导出名为 `handler` 的函数
   - 使用 `Args[Input]` 类型注解
   - 返回符合 `Output` 定义的数据

2. **依赖管理**：
   - 在每个脚本内部重新定义所需的类和函数
   - 可以 import 公共库如 `pyjianyingdraft`
   - 避免跨文件的自定义依赖

3. **文件操作**：
   - 尽量避免使用 `/tmp` 目录
   - 如必须使用，确保及时清理
   - 优先使用内存处理或参数传递

4. **状态管理**：
   - 避免全局变量和类属性存储状态
   - 所有状态通过函数参数传递
   - 采用函数式编程风格

### pyJianYingDraft 集成

1. **正确的导入方式**：
```python
from pyJianYingDraft import DraftFolder, VideoMaterial, AudioMaterial
from pyJianYingDraft import VideoSegment, AudioSegment, TextSegment
```

2. **常用操作模式**：
```python
# 创建草稿
draft = DraftFolder()

# 添加视频素材
video_material = VideoMaterial("video.mp4")
draft.add_video_material(video_material)

# 创建视频片段
video_segment = VideoSegment(video_material)
draft.add_video_segment(video_segment)
```

### 文档规范

每个工具函数和数据结构都必须有对应的 README.md，包含：

1. **功能描述**：简要说明工具的用途
2. **输入参数**：详细列出所有输入参数及其类型
3. **输出结果**：说明返回值的结构和含义
4. **使用示例**：提供完整的使用代码示例
5. **注意事项**：特殊限制或注意点

#### README 模板

```markdown
# [工具名称]

## 功能描述
[简要描述工具的功能和用途]

## 输入参数

### Input 类型定义
```python
class Input:
    param1: str  # 参数1说明
    param2: int  # 参数2说明
    # ...
```

## 输出结果

### Output 类型定义
```python
class Output:
    result1: str    # 结果1说明
    result2: bool   # 结果2说明
    # ...
```

## 使用示例
```python
# 示例代码
```

## 注意事项
- [列出重要的注意事项]
- [性能考虑]
- [错误处理说明]
```

## 开发最佳实践

### 错误处理
- 使用 `args.logger` 记录日志
- 提供详细的错误信息
- 优雅处理异常情况

### 性能优化
- 避免大文件在 `/tmp` 中的长期存储
- 使用流式处理处理大型媒体文件
- 合理使用内存缓存

### 测试考虑
- 每个工具函数都应该可以独立测试
- 提供不同场景的测试用例
- 考虑边界条件和异常情况

## 集成 Coze 平台

### Metadata 配置
确保在 Coze 平台上正确配置工具的 Metadata：
- 输入输出参数定义要与代码一致
- 提供清晰的工具描述
- 设置合适的超时时间

### 调试建议
- 使用 `args.logger` 输出调试信息
- 在开发阶段返回详细的中间结果
- 考虑添加调试模式开关

## 相关资源

- [Coze 开发者文档](https://www.coze.cn/open/docs/developer_guides)
- [pyJianYingDraft 文档](https://github.com/GuanYixuan/pyJianYingDraft)
- [剪映草稿格式说明](https://github.com/GuanYixuan/pyJianYingDraft/blob/main/README.md)