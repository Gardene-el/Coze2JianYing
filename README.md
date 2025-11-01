<h1 align="center">开源的Coze剪映小助手：Coze2JianYing</h1>

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

</div>

---

## 📑 目录

<div align="center">

<table>
<tr>
<td width="33%">

- [为什么是 Coze2JianYing](#-为什么是-coze2jianying)
- [Coze2JianYing 的缺点](#%EF%B8%8F-coze2jianying-%E7%9A%84%E7%BC%BA%E7%82%B9)
- [最速上手 Coze2JianYing](#-最速上手-coze2jianying)

</td>
<td width="33%">

- [从源码开始构建](#-从源码开始构建-coze2jianying)
  - [从零复刻 Coze 插件](#-1-从零复刻-coze-插件)
  - [编译草稿生成器程序](#️-2-编译草稿生成器程序)

</td>
<td width="33%">

- [关于流程说明](#-关于-扣子-2-剪映-的流程说明)
- [贡献机制](#-贡献机制)
- [赞助支持](#-赞助支持)
- [许可证](#-许可证)

</td>
</tr>
</table>

</div>

---

## 🎯 为什么是 Coze2JianYing

相比市面上其他的剪映小助手，Coze2JianYing 具有以下核心优势：

### ✅ 完全开源 - 用户可独立部署

- **源代码完全公开** - 遵循 GPL-3.0 许可证，所有代码透明可审查
- **自主部署构建** - 用户可以完全独立地部署和构建相关应用
- **无后门风险** - 开源代码可审计，不存在隐藏的数据收集行为
- **自由修改定制** - 支持根据个人需求进行二次开发和功能定制

### 💰 完全免费 - 无广告无收费

- **永久免费使用** - 不存在任何付费功能或服务
- **无广告干扰** - 应用使用过程中不会有任何广告弹窗
- **无隐藏收费** - 不会有任何形式的内购、订阅或额外收费
- **无使用限制** - 不限制生成次数、视频时长或素材数量

### 🔒 数据安全 - 完全用户掌控

- **素材本地托管** - 所有素材文件由用户自行管理和存储
- **不上传第三方** - 除用户自己的 Coze 和 剪映 的云端服务外，不会上传到任何第三方数据库
- **隐私完全保护** - 草稿内容、素材数据不会被收集或分析
- **数据自主可控** - 用户对所有数据拥有完全的控制权和处置权

---

## ⚠️ Coze2JianYing 的缺点

**实话实说，Coze2JianYing 仍处于早期阶段**，以下是当前待解决的主要问题：

### 🔧 应用功能待完善

- [ ] **视频轨道功能缺失** - 目前不支持视频轨道添加和编辑
- [ ] **关键帧动画未实现** - 无法创建复杂的时间轴动画效果
- [ ] **高级特效支持不足** - 部分剪映高级特效和滤镜尚未支持
      ...

### 📊 项目管理待成熟

- [ ] **版本管理不规范** - 缺乏系统的版本发布和更新机制
- [ ] **工作流不完整** - CI/CD 流程不够完善，自动化测试覆盖率低
- [ ] **文档待补充** - 部分功能缺少详细文档和使用示例
- [ ] **测试覆盖不足** - 缺少全面的单元测试和集成测试
- [ ] **更新节奏不稳定** - 功能更新和 bug 修复没有明确的时间表
      ...

### 🌱 社区建设待发展

- [ ] **社区处于早期** - 项目社区刚刚起步，缺少活跃的贡献者
- [ ] **答疑机制欠缺** - 用户问题反馈和解答响应速度较慢
- [ ] **贡献流程不明确** - 缺少清晰的贡献指南和代码审查流程
      ...

> **💡 说明**：非常抱歉，由于贡献机制尚未完善，目前暂时无法接受 PR 和其他形式的代码协作。但我非常欢迎您：
>
> - **提出问题和建议** - 在 [Issues](https://github.com/Gardene-el/Coze2JianYing/issues) 中反馈使用问题或功能建议
> - **报告 Bug** - 帮助发现和记录项目中的问题
> - **表达贡献意愿** - 如果您希望参与贡献，请在 Issue 中说明，我会优先完善相关的协作机制

---

## 🚀 最速上手 Coze2JianYing

Coze2JianYing 的完整工作流程包含四个主要阶段：

### 🔄 完整工作流

```mermaid
graph LR
    A[Coze 工作流] -->|生成素材和参数| B[Coze 插件（本项目提供）]
    B -->|导出 JSON 数据| C[草稿生成器（本项目提供）]
    C -->|生成草稿文件| D[剪映软件]
```

### 快速开始步骤

**1. 收藏 Coze 插件**

访问并收藏本项目发布的 Coze 插件，方便后续在工作流中使用：

🔗 [Coze2JianYing 插件](https://www.coze.cn/store/plugin/7565396538596818950?from=plugin_card)

**2. 下载草稿生成器**

前往 [Releases 页面](https://github.com/Gardene-el/Coze2JianYing/releases) 下载最新版本的 `CozeJianYingDraftGenerator.exe`

**3. 下载工作流示例**

下载 `workflow_demo.zip`（暂时占位符 - 文件准备中）

**4. 导入并试运行工作流**

- 解压 `workflow_demo.zip`
- 在 Coze 平台中导入工作流文件
- 打开工作流，点击试运行
- 在输入框中输入几句话，让 AI 生成内容

---

## 🔨 从源码开始构建 Coze2JianYing

本项目包含两个主要部分，可以分别构建和使用：

### 📦 1. 从零复刻 Coze 插件

**适合场景**：需要在 Coze 平台（扣子）上从零开始创建插件工具

#### 前置准备

1. **克隆仓库到本地**

```bash
git clone https://github.com/Gardene-el/Coze2JianYing.git
cd Coze2JianYing
```

2. **准备 Coze 平台账号**
   - 访问 [Coze 平台](https://www.coze.cn/)
   - 注册并登录账号
   - 进入扣子空间

#### 创建插件步骤

**第一步：创建插件**

1. 在扣子空间的**资源库页面**点击右上角的 **"+ 资源"**
2. 插件工具创建方式选择：**"云侧插件 - 在 Coze IDE 中创建"**
3. IDE 运行时选择：**Python3**
4. 插件名称和插件描述：可以随意填写（建议填写 "Coze2JianYing" 和简短描述）

**第二步：逐个创建工具函数**

#### 工具函数文件结构

每个工具函数文件夹包含：

- `handler.py` - 主处理函数（符合 Coze 平台规范）
- `README.md` - 详细使用文档和参数说明

#### 创建流程

`coze_plugin/tools/` 目录下的每个文件夹对应一个工具函数，需要逐个创建：

| 文件夹名称           | 工具功能     | 创建顺序建议  | 备注                      |
| -------------------- | ------------ | ------------- | ------------------------- |
| `create_draft/`      | 创建草稿     | ⭐ 第一个创建 |                           |
| `make_video_info/`   | 生成视频配置 | 按需创建      |                           |
| `make_image_info/`   | 生成图片配置 | 第二个创建    |                           |
| `make_audio_info/`   | 生成音频配置 | 第三个创建    |                           |
| `make_caption_info/` | 生成字幕配置 | 第四个创建    |                           |
| `make_effect_info/`  | 生成特效配置 | ~~按需创建~~  | ⚠️ 已弃用，未来会重新实现 |
| `add_videos/`        | 添加视频轨道 | 按需创建      |                           |
| `add_images/`        | 添加图片轨道 | 第五个创建    |                           |
| `add_audios/`        | 添加音频轨道 | 第六个创建    |                           |
| `add_captions/`      | 添加字幕轨道 | 第七个创建    |                           |
| `add_effects/`       | 添加特效轨道 | ~~按需创建~~  | ⚠️ 已弃用，未来会重新实现 |
| `export_drafts/`     | 导出草稿     | ⭐ 最后创建   |                           |

> **💡 说明**：`make_effect_info` 和 `add_effects` 工具当前已弃用，暂不建议创建。这些功能正在重新设计中，未来版本会提供更完善的实现。

**对于每个工具函数，按以下步骤操作：**

1. **填写工具名称**：使用文件夹名称（如 `create_draft`）

2. **填写工具介绍**：

   - 打开对应文件夹中的 `README.md`
   - 复制"功能描述"部分的内容
   - 粘贴到工具介绍框中

3. **复制代码**：

   - 打开文件夹中的 `handler.py` 文件
   - 将全部内容复制
   - 粘贴覆盖 Coze IDE 中的默认代码

4. **配置输入参数**（元数据 - Input）：

   - 在对应文件夹的 `README.md` 中找到 **Input 类型定义**
   - 点击"编辑"按钮，逐个添加参数：
     - **参数名**：使用 Input 类中定义的变量名
     - **参数类型**：根据类型定义选择（str→string, int→number, bool→boolean, list→array）
     - **是否必选**：如果类型是 `Optional[*]`，则**不打勾**；否则**打勾**
     - **参数描述**：复制 README 中该参数的说明

5. **配置输出参数**（元数据 - Output）：
   - 在 `README.md` 中找到 **Output 类型定义**
   - 添加方式与输入参数相同

**第三步：测试工具函数**

发布插件前必须测试所有工具，测试顺序很重要！

**测试顺序和注意事项：**

1. **首先测试 `create_draft`**

   - 填写测试参数：draft_name（如"测试项目"）、width（1920）、height（1080）、fps（30）

   > **💡 说明**：保存返回的 `draft_id` 值，后续所有测试都需要用到这个 ID

2. **测试 `make_*_info` 系列工具**（在测试 `add_*s` 之前）

   - 先测试 `make_image_info`、`make_audio_info`、`make_caption_info`
   - 保存这些工具生成的 JSON 字符串结果

3. **测试 `add_*s` 系列工具**

   - 使用上一步保存的 `draft_id` 作为输入参数之一
   - 使用对应 `make_*_info` 生成的结果作为配置参数

4. **最后测试 `export_drafts`**
   - `draft_ids` 参数可以**留空**
   - `export_all` 参数**打勾**（选择 true）
   - 这样会导出所有草稿用于验证

**第四步：发布插件**

- 所有工具测试通过后，点击"发布"按钮
- 发布成功后即可在 Coze 工作流中使用

---

### 🖥️ 2. 编译草稿生成器程序

**适合场景**：需要自行编译草稿生成器 exe 文件

> **⚠️ 平台限制**：本项目仅支持 Windows 平台,因为剪映官方不支持 Linux,且作者没有 Mac 设备进行测试。

#### 前置准备

**安装 Python**（如果你没有）

可以通过 [Python 官网](https://www.python.org/downloads/) 或 `winget install Python.Python.3.12` 安装。如需详细教程,推荐在 B 站 搜索或询问 AI 助手。

**了解虚拟环境**（如果你不了解）

为了避免依赖冲突。相关概念可以通过 AI 或搜索引擎进一步了解。

#### 编译步骤

**1. 克隆仓库**

```bash
git clone https://github.com/Gardene-el/Coze2JianYing.git
cd Coze2JianYing
```

**2. 创建并激活虚拟环境**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

> **💡 说明**：激活成功后，命令行前会显示 `(venv)` 标识

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

**4. 执行编译脚本**

```bash
python build.py
```

编译过程可能需要几分钟，请耐心等待。

**5. 获取编译后的 exe 文件**

编译完成后，在 `dist/` 目录下找到生成的文件：

```
dist/
├── CozeJianYingDraftGenerator-GUI.exe  # GUI版本（图形界面）
└── CozeJianYingDraftGenerator-CLI.exe  # CLI版本（命令行）
```

这两个 exe 文件：

- 可以在任何 Windows 系统上运行（无需安装 Python）
- 可以独立分发给其他用户
- 包含了所有必需的依赖

**GUI版本** 提供图形界面，适合日常使用；**CLI版本** 提供命令行界面，适合脚本自动化和批处理

---

### 📁 项目结构说明

```
Coze2JianYing/
├── coze_plugin/              # Coze 插件子项目
│   ├── tools/                # 各种工具函数
│   │   ├── create_draft/     # 创建草稿工具
│   │   ├── add_images/       # 添加图片工具
│   │   ├── add_audios/       # 添加音频工具
│   │   ├── add_captions/     # 添加字幕工具
│   │   ├── add_effects/      # 添加特效工具
│   │   └── export_drafts/    # 导出草稿工具
│   ├── examples/             # 使用示例和演示代码
│   ├── tests/                # 测试文件
│   └── main.py               # 核心助手类
├── src/                      # 草稿生成器应用
│   ├── GUI/                  # GUI 界面模块
│   │   ├── main.py           # GUI 主入口
│   │   └── main_window.py    # 主窗口实现
│   ├── CLI/                  # CLI 命令行模块
│   │   └── main.py           # CLI 主入口
│   ├── utils/                # 核心工具模块
│   │   ├── draft_generator.py    # 草稿生成主逻辑
│   │   ├── coze_parser.py        # Coze 数据解析
│   │   ├── material_manager.py   # 素材下载管理
│   │   └── logger.py             # 日志系统
│   └── main.py               # 统一入口（支持GUI/CLI）
├── data_structures/          # 数据结构定义
│   ├── draft_generator_interface/  # 草稿生成器接口
│   └── media_models/         # 媒体文件模型
├── docs/                     # 完整项目文档
├── scripts/                  # 实用工具脚本
│   ├── coze_json_formatter.py    # Coze JSON 格式化工具
│   └── test_coze_json_formatter.py  # 测试脚本
├── build.py                  # PyInstaller 打包脚本
├── requirements.txt          # 项目依赖列表
└── setup.py                  # 项目安装配置
```

---

## 📋 关于 扣子 2 剪映 的流程说明

Coze2JianYing 的完整工作流程包含四个主要阶段：

### 🔄 完整工作流

```mermaid
graph LR
    A[Coze 工作流] -->|生成素材和参数| B[Coze 插件]
    B -->|导出 JSON 数据| C[草稿生成器]
    C -->|生成草稿文件| D[剪映软件]
```

### 1️⃣ Coze 工作流阶段

在 Coze 平台上创建 AI 工作流，自动生成视频内容：

- **素材生成**：利用 AI 生成文本、图片、音频等素材
- **参数配置**：工作流或者 AI 自动配置字幕样式、音频时长、特效参数等
- **内容编排**：工作流或者 AI 安排素材的时间轴和展示顺序

### 2️⃣ Coze 插件阶段（本项目提供）

使用 Coze 插件记录、暂存和导出数据：

### 3️⃣ 草稿生成器阶段（本项目提供）

将 JSON 数据转换为剪映草稿文件：

- **JSON 解析**：解析 Coze 插件导出的 JSON 数据
- **素材下载**：自动从网络下载所需的媒体文件
- **草稿生成**：调用 pyJianYingDraft 生成剪映草稿结构
- **文件输出**：生成完整的草稿文件夹到指定位置

**支持的数据格式**：

- 单个草稿 JSON
- 批量草稿数组
- 多种嵌套格式兼容

### 4️⃣ 剪映编辑阶段

在剪映软件中打开生成的草稿：

- 所有素材已经就位
- 时间轴已经配置完成
- 字幕、音频、特效等已添加
- 用户可以进行最终的微调和导出

### 💡 设计理念

这种分离式架构的好处：

- **解决空间限制**：Coze 平台 `/tmp` 目录仅 512MB，大型素材由草稿生成器下载
- **避免变量干扰**：UUID 系统避免 Coze 工作流变量索引的复杂性
- **提高灵活性**：每个阶段相对独立，便于调试和优化
- **支持离线使用**：草稿生成器可打包为 exe，独立于 Coze 平台运行

---

## 🤝 贡献机制

<div align="center">

🚧 **施工中** 🚧

_贡献机制正在搭建中，敬请期待..._

</div>

---

## 💖 赞助支持

<div align="center">

� **装修中** 🎨

_赞助渠道正在准备中，感谢您的关注..._

</div>

---

## 📄 许可证

本项目采用 [GPL-3.0](LICENSE) 许可证开源。

这意味着：

- ✅ 您可以自由使用、修改、分发本项目
- ✅ 可用于商业用途，但需遵循 GPL-3.0 条款
- ✅ 修改后的代码必须同样以 GPL-3.0 开源
- ✅ 必须保留原作者的版权声明
- ❌ 您不能声称本项目的版权归您所有
- ❌ 不提供任何形式的担保

---

## 🙏 致谢 Credit！

感谢以下开源项目：

- [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) - 核心的剪映草稿生成库

以及所有为项目做出贡献的开发者！

---

<div align="center">

**[⬆ 返回顶部](#-目录)**

Made with ❤️ by [Gardene-el](https://github.com/Gardene-el)

</div>
