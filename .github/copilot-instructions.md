# Copilot Instructions for CozeJianYingAssistent

## 项目概述

这是一个专为 Coze 平台设计的剪映草稿生成工具，基于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 构建。本项目用于演示和开发将来会在 Coze 插件中使用的 Python 工具函数。

### Coze 关键概念

- **插件 (Plugin)**: Coze 平台上的扩展工具，包含一个或多个工具函数，为 AI 工作流提供特定功能
- **工作流 (Workflow)**: 在 Coze 平台上创建的自动化流程，可以调用多个插件和工具来完成复杂任务
- **工具 (Tool)**: 插件中的具体功能单元，每个工具函数必须有 `handler` 入口函数，处理特定的输入输出

### 整体工作流程概述

本项目是 **Coze 到剪映自动化视频生成工作流** 中的关键组件之一。完整的工作流涉及四个项目的协作：

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│    Coze     │───▶│ Coze插件     │───▶│ 草稿生成器   │───▶│    剪映     │
│   工作流    │    │ (本项目)     │    │ (未建项目)   │    │             │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

#### 详细流程说明

1. **Coze 工作流** → 生成素材和对应的参数
2. **Coze 插件 (本项目)** → 在 Coze 中调用本项目展示的插件工具，将素材和参数导入，导出目标的 JSON 数据
3. **草稿生成器** → 将目标的 JSON 数据导入进草稿生成器 *(占位符：具体实现待草稿生成器项目建立后补充)*
4. **剪映** → 草稿生成器生成对应内容至剪映草稿文件夹

#### 设计理念与技术约束

这种看似繁琐的分离式架构设计是基于以下考虑：

- **Coze 文件空间限制**: Coze 平台的文件系统存储空间有限 (`/tmp` 目录仅 512MB)
- **工作流完整性需求**: 在 Coze 中单个工作流需要生成完整的剪映草稿内容参数
- **资源传输优化**: Coze 生成的素材都是网页链接形式，插件传输给草稿生成器不会直接传递资源文件，而是传递链接列表

### 本项目的角色定位

本项目主要承担以下职责：

1. **参数处理与验证**: 接收 Coze 工作流传递的素材链接和处理参数
2. **pyJianYingDraft 功能映射**: 将 pyJianYingDraft 库中所有可设置的剪映参数选项包装为 Coze 工具函数
3. **JSON 数据生成**: 生成标准化的 JSON 格式数据，供草稿生成器使用
4. **链接资源管理**: 处理和验证 Coze 传递的网页链接资源

#### pyJianYingDraft 深度集成

本项目包含 pyJianYingDraft 依赖库不仅是为了生成剪映草稿文件，更重要的是：

- **参数完整性**: 理解和应用 pyJianYingDraft 中剪映内容的所有可配置参数
- **功能覆盖**: 确保剪映中所有可选择的参数设置都能在本项目的工具函数中体现
- **标准化输出**: 为草稿生成器提供标准化的数据结构和参数格式

## 项目当前状态

### ✅ 已完成的核心功能
1. **create_draft 工具** - UUID 草稿创建，支持完整的项目配置参数
2. **export_drafts 工具** - 单个和批量草稿导出，支持 `export_all` 功能
3. **get_media_duration 工具** - 网络媒体时长分析和时间轴计算
4. **完整数据模型** - 草稿生成器接口和媒体处理模型
5. **测试体系** - 7个测试文件，覆盖主要功能模块
6. **文档体系** - 完整的项目文档和开发指南

### 🔄 技术架构特点
- **UUID 管理系统**: 解决 Coze 平台状态管理难题
- **网络资源处理**: 支持 Coze 平台的链接资源模式  
- **向后兼容性**: 所有系统更新保持 100% 向后兼容
- **错误处理完善**: 包含 NoneType 处理、参数验证等关键修复

### 📋 待扩展功能
- `add_video_track` - 视频轨道添加工具
- `add_audio_track` - 音频轨道添加工具
- `add_text_track` - 文本/字幕轨道添加工具
- `add_effects` - 特效和滤镜添加工具

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

### 实际项目结构 (当前状态)
```
CozeJianYingAssistent/
├── coze_jianying_assistant/    # 主包目录
│   ├── __init__.py            # 包初始化文件
│   └── main.py                # 主程序入口
├── tools/                     # Coze 工具函数脚本 (已实现)
│   ├── create_draft/          # ✅ 创建草稿工具
│   │   ├── handler.py         
│   │   └── README.md          
│   ├── export_drafts/         # ✅ 导出草稿工具
│   │   ├── handler.py         
│   │   └── README.md
│   └── get_media_duration/    # ✅ 媒体时长分析工具
│       ├── handler.py         
│       └── README.md
├── data_structures/           # 数据结构定义 (已实现)
│   ├── draft_generator_interface/  # ✅ 草稿生成器接口
│   │   ├── models.py         
│   │   └── README.md
│   └── media_models/          # ✅ 媒体文件模型
│       ├── models.py         
│       └── README.md
├── examples/                  # ✅ 使用示例
│   ├── coze_workflow_examples/
│   │   ├── draft_management_example.py
│   │   └── get_media_duration_example.py
│   └── json_output_samples/
│       ├── batch_draft_export.json
│       └── complete_draft_export.json
├── tests/                     # ✅ 测试文件目录 (新增)
│   ├── __init__.py
│   ├── README.md             # 测试指南
│   ├── test_basic.py         # 基础功能测试
│   ├── test_tools.py         # 工具函数测试
│   └── [其他测试文件...]
├── requirements.txt           # ✅ 项目依赖
├── setup.py                  # ✅ 安装配置
├── DRAFT_MANAGEMENT_GUIDE.md # ✅ 草稿管理指南
├── DEVELOPMENT_ROADMAP.md    # ✅ 项目发展路线图 (新增)
└── README.md                 # ✅ 项目说明 (已更新)
```

### 规划中的扩展结构
```
tools/ (待扩展)
├── add_video_track/          # 计划：添加视频轨道工具
├── add_audio_track/          # 计划：添加音频轨道工具  
├── add_text_track/           # 计划：添加文本轨道工具
└── add_effects/              # 计划：添加特效工具
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

5. **资源链接处理**：
   - Coze 传递的素材均为网页链接格式
   - 工具函数应验证链接有效性
   - 传递链接列表而非直接下载资源文件
   - 为草稿生成器保留链接信息以便后续处理

### pyJianYingDraft 集成与参数覆盖

#### 核心集成目标

本项目使用 pyJianYingDraft 不仅仅是为了生成草稿文件，更重要的是：

1. **完整参数映射**: 将 pyJianYingDraft 中所有可配置的剪映参数选项包装为 Coze 工具函数
2. **功能全覆盖**: 确保剪映中所有可设置的参数都能通过本项目的工具函数进行配置
3. **参数验证**: 理解并验证各种参数组合的有效性和兼容性

#### 1. 正确的导入方式：
```python
from pyJianYingDraft import DraftFolder, VideoMaterial, AudioMaterial
from pyJianYingDraft import VideoSegment, AudioSegment, TextSegment
from pyJianYingDraft import FilterType, TransitionType, EffectSegment
# 导入所有相关的参数类型和枚举
```

#### 2. 链接资源处理模式：
```python
# 处理 Coze 传递的网页链接
def process_media_links(args: Args[Input]) -> Output:
    video_links = args.input.video_urls  # 网页链接列表
    audio_links = args.input.audio_urls  # 音频链接列表
    
    # 验证链接有效性但不下载
    validated_links = validate_media_links(video_links + audio_links)
    
    # 生成 JSON 数据供草稿生成器使用
    draft_json = {
        "video_resources": video_links,
        "audio_resources": audio_links,
        "processing_parameters": extract_jianyingdraft_params(args.input)
    }
    
    return {"draft_json": draft_json}
```

#### 3. 参数映射示例：
```python
# 将 pyJianYingDraft 的所有参数选项映射到工具函数
def map_video_parameters(input_params):
    """映射视频相关的所有可配置参数"""
    return {
        "filter_type": FilterType.from_string(input_params.filter),
        "transition_type": TransitionType.from_string(input_params.transition),
        "crop_settings": CropSettings(**input_params.crop_config),
        "effect_settings": process_effect_parameters(input_params.effects),
        # ... 包含所有 pyJianYingDraft 支持的参数
    }
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

### 测试指南

项目在 `tests/` 目录中包含完整的测试体系，遵循以下原则：

#### 测试组织
- **`tests/`** 目录包含所有测试文件
- 每个测试文件独立运行，无相互依赖
- 使用 `/tmp` 目录进行临时文件操作，自动清理
- 测试文件命名：`test_[功能名称].py`

#### 测试类型
- **基础功能测试** (`test_basic.py`): 数据结构和核心功能
- **工具函数测试** (`test_tools.py`): Coze 工具的端到端测试
- **修复验证测试**: 验证特定bug修复的有效性
- **架构变更测试**: 验证系统升级的向后兼容性

#### 测试编写规范
```python
#!/usr/bin/env python3
"""
Test description and purpose
"""

def test_specific_function():
    """Test the specific function with description"""
    print("=== Testing specific function ===")
    
    # Setup
    # Test execution
    # Assertions
    # Cleanup
    
    print("✅ Test passed!")
    return True

if __name__ == "__main__":
    # Run all tests
    results = []
    results.append(test_specific_function())
    
    print(f"\\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
```

#### 测试运行
```bash
# 运行单个测试
python tests/test_basic.py

# 运行所有测试
cd tests && python test_*.py
```

### 性能优化
- 避免大文件在 `/tmp` 中的长期存储
- 使用流式处理处理大型媒体文件
- 合理使用内存缓存

### 原有测试考虑
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

## 草稿生成器接口规范

### 数据交换格式

本项目生成的 JSON 数据需要符合草稿生成器的输入规范：

```python
# 标准输出格式 (占位符定义)
{
    "project_info": {
        "name": "项目名称",
        "resolution": "1920x1080",
        "frame_rate": 30
    },
    "media_resources": {
        "video_urls": ["https://example.com/video1.mp4", ...],
        "audio_urls": ["https://example.com/audio1.mp3", ...],
        "image_urls": ["https://example.com/image1.jpg", ...]
    },
    "timeline_config": {
        "video_tracks": [...],  # 视频轨道配置
        "audio_tracks": [...],  # 音频轨道配置
        "text_tracks": [...]    # 文字轨道配置
    },
    "processing_parameters": {
        # 所有 pyJianYingDraft 参数的完整映射
        # *占位符：待草稿生成器项目建立后详细定义*
    }
}
```

### 接口设计原则

- **链接传递**: 所有媒体资源均以 URL 形式传递
- **参数完整**: 包含 pyJianYingDraft 支持的所有配置选项
- **向前兼容**: 设计时考虑未来草稿生成器的扩展需求
- **验证机制**: 提供数据格式验证和错误处理

*注：具体接口规范将在草稿生成器项目建立后进行详细补充和完善*

## 开发历程文档规范

### DEVELOPMENT_ROADMAP.md 编写规范

当添加新功能或进行重要更新时，必须在 `DEVELOPMENT_ROADMAP.md` 中记录开发过程。遵循以下规范：

#### 文档目标
- 帮助开发者和学习者快速理解项目架构
- 解释每个功能出现的应用背景和原因
- 记录具体的实现方法和技术决策
- 保持简洁务实，避免营销性语言

#### 内容结构
每个新功能的记录应包含以下部分：

```markdown
### N. 功能名称 - [Issue #X](链接), [PR #Y](链接)

**应用背景**: 说明为什么需要这个功能，解决什么实际问题

**实现需求**: (如果复杂功能需要)
- 列出主要的技术需求
- 说明约束条件和挑战

**具体做法**:
- 详细说明实现方案
- 列出关键的技术细节
- 包含重要的代码结构或API设计
- 说明如何解决主要挑战
```

#### 编写原则
1. **重点在于技术实现**: 重点解释应用背景、原因和具体做法
2. **链接到实际Issues/PRs**: 必须包含GitHub issue和PR的完整链接
3. **避免时间线营销**: 不强调"第几阶段"、"里程碑"等营销性描述
4. **保持实用性**: 专注于帮助理解架构和功能，不包含项目展望或成长数据
5. **按开发顺序**: 按照功能开发的实际顺序记录，体现依赖关系

#### 禁止内容
- 避免"第一阶段"、"成熟化"等阶段性描述
- 不包含"核心技术概念演进"、"设计决策记录"等理论性章节
- 不添加"项目成长数据"、"未来展望"等市场化内容
- 减少时间戳和日期，除非对理解技术演进必要

#### 更新要求
- 每次添加新功能时必须更新此文档
- 保持文档与实际代码同步
- 定期检查链接有效性
- 确保新内容符合既定格式

## 相关资源

### Coze 平台资源
- [Coze 开发者文档](https://www.coze.cn/open/docs/developer_guides)
- [Coze 插件开发指南](https://www.coze.cn/open/docs/developer_guides)
- [GitHub Copilot 最佳实践](https://gh.io/copilot-coding-agent-tips)

### pyJianYingDraft 资源
- [pyJianYingDraft 文档](https://github.com/GuanYixuan/pyJianYingDraft)
- [剪映草稿格式说明](https://github.com/GuanYixuan/pyJianYingDraft/blob/main/README.md)

### 项目生态系统
- **Coze 工作流**: AI 驱动的内容生成和参数配置
- **本项目 (Coze 插件)**: 参数处理和 JSON 数据生成
- **草稿生成器** *(占位符)*: JSON 数据转换为剪映草稿文件
- **剪映**: 最终的视频编辑和输出