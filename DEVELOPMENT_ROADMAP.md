# 项目功能开发历程

本文档记录项目各个功能和规范的开发顺序，解释每个功能出现的应用背景、原因和具体实现方法，帮助开发者理解项目架构。

## 开发顺序

### 1. 项目基础结构 - [Issue #2](https://github.com/Gardene-el/CozeJianYingAssistent/issues/2), [PR #3](https://github.com/Gardene-el/CozeJianYingAssistent/pull/3)

**应用背景**: 项目从空白仓库开始，需要建立标准的 Python 项目结构以支持后续 Coze 插件开发

**实现要求**: 
- 需要引用 pyJianYingDraft 项目作为核心依赖
- 建立标准的 Python 包管理结构

**具体做法**:
- 采用标准 Python 包结构 (`coze_jianying_assistant/` 主包目录)
- 选择 `pyJianYingDraft>=0.2.5` 作为核心依赖，通过 GitHub Advisory Database 验证安全性
- 建立 `requirements.txt`、`setup.py` 等标准配置文件
- 设置 GPL-3.0 开源协议

### 2. Coze 平台开发规范 - [Issue #6](https://github.com/Gardene-el/CozeJianYingAssistent/issues/6), [PR #7](https://github.com/Gardene-el/CozeJianYingAssistent/pull/7)

**应用背景**: Coze 平台有独特的运行环境限制，需要建立专门的开发规范来适配这些约束

**核心约束问题**:
- `/tmp` 目录只有 512MB 空间限制
- 无共同头文件概念，每个工具函数需重复定义依赖
- 强制函数式编程风格，不能存储状态变量
- 必须导出 `handler` 函数作为工具入口

**具体做法**:
- 确立四阶段工作流架构: `Coze 工作流 → Coze插件(本项目) → 草稿生成器 → 剪映`
- 建立分离式架构设计，解决文件空间限制和中间数据索引干扰
- 制定标准的 Coze 工具函数模板，包含 `Args[Input] -> Output` 结构
- 建立完整的开发规范文档 (`.github/copilot-instructions.md`)

### 3. 媒体时长分析工具 - [Issue #8](https://github.com/Gardene-el/CozeJianYingAssistent/issues/8), [PR #9](https://github.com/Gardene-el/CozeJianYingAssistent/pull/9)

**应用背景**: Coze 工作流需要准确的媒体时长信息来进行时间轴计算，但传入的都是网络链接而非本地文件

**实现需求**:
- 接收网络链接数组，获取每个媒体文件的时长
- 计算累积时间轴，为后续视频编辑提供时间控制信息
- 需要处理各种网络媒体格式和特殊服务(如 Volcano Engine TTS)

**具体做法**:
- 实现 `get_media_duration` 工具函数
- 支持输入格式: `{"links": ["https://.../1.mp4", "https://.../2.mp4"]}`
- 输出累积时间轴: `{"all_timelines": [{"start": 0, "end": total}], "timelines": [individual_ranges]}`
- 针对 Volcano Engine TTS 添加专门的 URL 过期检查和错误处理
- 建立网络资源处理的标准模式

### 4. UUID 草稿管理系统 - [Issue #10](https://github.com/Gardene-el/CozeJianYingAssistent/issues/10), [PR #11](https://github.com/Gardene-el/CozeJianYingAssistent/pull/11)

**应用背景**: Coze 平台的变量索引模式会在工作流中产生大量中间数据索引，对用户造成干扰

**核心问题**:
- 如果仅靠 input/output 传递数据，会导致 Coze 变量系统保留大量中间数据
- 需要一个独立的草稿管理方案来避免变量索引复杂性
- 需要支持草稿的创建、修改、导出全生命周期管理

**具体做法**:
- 设计 UUID 管理系统: `用户输入 → create_draft → UUID → 添加内容工具 → export_drafts`
- 实现 `create_draft` 工具: 输入项目基本设置(分辨率、帧率等)，输出 UUID
- 实现 `export_drafts` 工具: 输入 UUID 或 UUID 数组，输出标准化 JSON 数据
- 草稿存储在 `/tmp/jianying_assistant/drafts/{uuid}` 结构化目录中
- 添加 `export_all` 功能支持批量导出所有草稿
- 建立完整的参数映射，覆盖 pyJianYingDraft 的所有配置选项
- 处理 NoneType 参数错误，添加默认值处理逻辑

### 5. 项目架构整理 - [Issue #12](https://github.com/Gardene-el/CozeJianYingAssistent/issues/12), [PR #13](https://github.com/Gardene-el/CozeJianYingAssistent/pull/13)

**应用背景**: 项目已具备完整功能，但缺乏系统性的架构组织和文档体系

**整理需求**:
- 测试文件散布在根目录，需要统一管理
- README.md 需要反映实际项目状态
- 缺乏功能开发历程的记录和说明
- 开发规范需要基于实际架构进行优化

**具体做法**:
- 创建 `tests/` 目录，移动所有测试文件并添加测试文档
- 更新 README.md，准确描述四阶段工作流架构和已实现功能
- 创建本文档，记录功能开发的背景和实现方法

### 6. 图片轨道添加功能 - [Issue #16](https://github.com/Gardene-el/CozeJianYingAssistent/issues/16), [PR #17](https://github.com/Gardene-el/CozeJianYingAssistent/pull/17), [PR #25](https://github.com/Gardene-el/CozeJianYingAssistent/pull/25)

**应用背景**: 需要向草稿添加图片内容，支持 Coze 工作流中的动态图片配置需求

**核心需求**:
- 支持 Coze 传递的图片链接数组
- 实现图片片段的完整参数配置（位置、缩放、动画、滤镜等）
- 需要辅助工具来动态生成图片配置字符串
- 支持多种输入格式以适应不同使用场景

**具体做法**:
- 实现 `add_images` 工具：向草稿添加图片轨道
  - 支持三种输入格式：数组对象、数组字符串、JSON 字符串
  - 每次调用创建一个新的图片轨道
  - 基于 ImageSegmentConfig 数据结构（25个参数：3必需 + 22可选）
  - 包含完整的变换、裁剪、效果、背景、动画参数
- 实现 `make_image_info` 工具：生成单个图片配置 JSON 字符串
  - 只输出非默认值参数，保持输出紧凑
  - 完整的参数验证（时间范围、数值范围等）
  - 输出可直接用于 add_images 的数组字符串格式
- PR #25 添加数组字符串格式支持，解决 Coze 工作流中动态配置的传递问题
- 移除 width/height 元数据字段，避免用户误解（实际尺寸由 scale_x/y 和 fit_mode 控制）

### 7. 音频轨道添加功能 - [Issue #26](https://github.com/Gardene-el/CozeJianYingAssistent/issues/26)

**应用背景**: 参考图片工具的完整设计过程，实现音频轨道添加功能以支持背景音乐、旁白、音效等需求

**设计参考**:
- PR #17 和 #25 的 add_images 和 make_image_info 实现过程
- Issue #16 和 #24 中发现和解决的问题
- AudioSegmentConfig 数据模型（简化版，无视觉相关参数）

**核心需求**:
- 支持多种音频配置：背景音乐、旁白、音效等
- 实现音频特有参数：音量、淡入淡出、音频效果、速度控制
- 支持音频裁剪（material_range）从长音频中提取片段
- 保持与图片工具相同的输入格式灵活性

**具体做法**:
- 实现 `make_audio_info` 工具（`tools/make_audio_info/`）：
  - 10个参数：3个必需（audio_url, start, end）+ 7个可选
  - 可选参数：volume, fade_in, fade_out, effect_type, effect_intensity, speed, material_start/end
  - 参数验证：volume (0.0-2.0), speed (0.5-2.0), fade 时间 >= 0
  - material_range 验证：start 和 end 必须同时提供
  - 只输出非默认值，保持紧凑输出
- 实现 `add_audios` 工具（`tools/add_audios/`）：
  - 支持三种输入格式（与 add_images 一致）
  - 每次调用创建新的音频轨道
  - 基于 AudioSegmentConfig 数据结构
  - 创建完整的音频片段结构：time_range, material_range, audio properties, keyframes
- 完整的测试体系：
  - `test_make_audio_info.py`：3个测试套件（基础功能、参数验证、边界情况）
  - `test_add_audios.py`：4个测试套件（基础功能、格式支持、集成测试、验证）
  - 所有测试通过，覆盖主要功能和错误场景
- 示例和文档：
  - `make_audio_info_demo.py`：7个示例场景（BGM、旁白、效果、裁剪等）
  - `add_audios_demo.py`：完整工作流演示（从创建草稿到添加多层音频）
  - 详细的 README 文档，包含参数说明和使用示例

**与图片工具的对比**:
- 图片：25个参数（包含变换、裁剪、动画等视觉参数）
- 音频：10个参数（专注于音量、淡入淡出、效果、速度）
- 相同点：支持相同的输入格式、相同的工具组合模式（make_*_info + add_*s）
- 不同点：音频无视觉参数（position, scale, rotation, crop, animations 等）

### 8. 字幕/文本轨道添加功能 - [Issue #29](https://github.com/Gardene-el/CozeJianYingAssistent/issues/29)

**应用背景**: 参考图片和音频工具的完整设计过程，实现字幕/文本轨道添加功能以支持视频字幕、标题、文字说明等需求

**设计参考**:
- PR #17 和 #25 的 add_images 和 make_image_info 实现过程
- Issue #16 和 #24 中发现和解决的问题
- Issue #26 的 add_audios 和 make_audio_info 实现经验
- TextSegmentConfig 和 TextStyle 数据模型（最复杂，包含完整的文本渲染参数）

**核心需求**:
- 支持多种文本配置：普通字幕、标题、文字说明、多语言字幕等
- 实现完整的文本样式参数：字体、颜色、大小、粗细、斜体
- 实现文本效果参数：描边、阴影、背景
- 支持文本对齐和位置控制
- 支持文本动画效果（入场、出场、循环）
- 保持与图片/音频工具相同的输入格式灵活性

**具体做法**:
- 实现 `make_caption_info` 工具（`tools/make_caption_info/`）：
  - 32个参数：4个必需（content, start, end）+ 28个可选
  - 必需参数：文本内容和时间范围
  - 位置变换参数（5个）：position_x, position_y, scale, rotation, opacity
  - 文本样式参数（5个）：font_family, font_size, font_weight, font_style, color
  - 描边效果参数（3个）：stroke_enabled, stroke_color, stroke_width
  - 阴影效果参数（5个）：shadow_enabled, shadow_color, shadow_offset_x/y, shadow_blur
  - 背景效果参数（3个）：background_enabled, background_color, background_opacity
  - 对齐方式参数（1个）：alignment (left/center/right)
  - 动画效果参数（3个）：intro_animation, outro_animation, loop_animation
  - 完整的参数验证：时间范围、位置范围（0.0-1.0）、透明度范围、枚举值验证
  - 只输出非默认值，保持紧凑输出
- 实现 `add_captions` 工具（`tools/add_captions/`）：
  - 支持三种输入格式（与 add_images/add_audios 一致）
  - 每次调用创建新的文本轨道
  - 基于 TextSegmentConfig 和 TextStyle 数据结构
  - 创建完整的文本片段结构：content, time_range, transform, style, alignment, animations, keyframes
  - 支持文本样式的完整嵌套结构（stroke, shadow, background）
- 完整的测试体系：
  - `test_make_caption_info.py`：4个测试套件（基础功能、数组字符串支持、集成测试、中文字符）
  - 包含9个基础功能测试（最小参数、文本样式、默认值、阴影/背景、动画、错误处理等）
  - 包含6个数组字符串支持测试（格式兼容性、错误处理）
  - 包含完整集成测试（make_caption_info → 数组 → add_captions → 验证配置）
  - 中文字符支持测试
  - 所有测试通过，覆盖主要功能和错误场景
- 示例和文档：
  - `make_caption_info_demo.py`：10个示例场景（基本字幕、标题、样式、阴影、背景、动画、完整样式、对齐、多字幕工作流、错误处理）
  - `add_captions_demo.py`：5个完整工作流演示（简单字幕、样式字幕、动态字幕、双语字幕、完整功能展示）
  - 详细的 README 文档，包含参数说明、使用示例、常见场景、技术细节

**与图片/音频工具的对比**:
- **图片**：25个参数（变换、裁剪、滤镜、背景模糊、动画等视觉效果）
- **音频**：10个参数（音量、淡入淡出、速度、音效等音频处理）
- **字幕**：32个参数（文本样式、描边、阴影、背景、对齐、动画等文本渲染）
- 相同点：支持相同的三种输入格式、相同的工具组合模式（make_*_info + add_*s）
- 不同点：字幕参数最多最复杂，需要支持完整的文本渲染效果；图片侧重视觉变换；音频侧重声音处理

**字幕工具的独特性**:
- 参数数量最多（32个），因为文本渲染需要精细控制
- 支持嵌套的样式配置（TextStyle 包含 stroke, shadow, background）
- 位置采用归一化坐标（0.0-1.0），便于不同分辨率的适配
- 支持文本对齐方式，这是图片和音频所没有的
- 描边、阴影、背景可以独立启用和组合使用，提供灵活的可读性增强方案

- 更新 `.github/copilot-instructions.md`，基于实际项目结构优化开发规范