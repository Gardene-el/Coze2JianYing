# Coze 到剪映草稿转换指南

本指南介绍如何使用新创建的工具将 Coze Draft Generator Interface 的输出转换为剪映草稿。

## 📋 目录

1. [概述](#概述)
2. [文件结构](#文件结构)
3. [快速开始](#快速开始)
4. [API 参考](#api参考)
5. [工作流程](#工作流程)
6. [示例代码](#示例代码)
7. [常见问题](#常见问题)

---

## 概述

### 功能特性

✅ **双层 JSON 解析** - 自动处理 Coze 的嵌套 JSON 格式(`{"output": "..."}`)  
✅ **批量草稿生成** - 支持一次性生成多个草稿  
✅ **自动素材下载** - 从 URL 下载音频/视频/图片素材  
✅ **完整轨道支持** - 支持 audio、image、text 轨道  
✅ **详细日志记录** - 完整的转换过程追踪

### 输入格式

Coze 的输出格式为:

```json
{
  "output": "{\"format_version\": \"1.0\", \"export_type\": \"single_draft\", \"drafts\": [...]}"
}
```

注意:

- 外层是普通 JSON 对象,包含`output`字段
- `output`字段的值是一个**JSON 字符串**(需要二次解析)

---

## 文件结构

### 新增文件

```
src/utils/
├── coze_parser.py        # Coze输出解析器
└── coze_to_draft.py      # 完整转换流程

test_coze_conversion.py   # 测试脚本
docs/
└── COZE_CONVERSION_GUIDE.md  # 本文档
```

### 依赖关系

```
coze_to_draft.py
├── coze_parser.py          # 解析Coze输出
├── converter.py            # 数据结构转换
├── material_manager.py     # 素材下载管理
└── pyJianYingDraft         # 生成草稿
```

---

## 快速开始

### 方法 1: 从文件转换

```python
from src.utils.coze_to_draft import convert_coze_to_draft

# 从JSON文件转换
draft_paths = convert_coze_to_draft(
    input_source='coze_output.json',
    is_file=True,
    output_dir='./JianyingProjects'
)

print(f"生成了 {len(draft_paths)} 个草稿")
for path in draft_paths:
    print(f"  - {path}")
```

### 方法 2: 从剪贴板转换

```python
import pyperclip
from src.utils.coze_to_draft import convert_coze_to_draft

# 从剪贴板获取内容
clipboard_text = pyperclip.paste()

# 转换
draft_paths = convert_coze_to_draft(
    input_source=clipboard_text,
    is_file=False,
    output_dir='./JianyingProjects'
)
```

### 方法 3: 使用类接口(更灵活)

```python
from src.utils.coze_to_draft import CozeToDraftConverter

converter = CozeToDraftConverter(output_base_dir='./JianyingProjects')

# 从文件
draft_paths = converter.convert_from_file('coze_output.json')

# 或从剪贴板
import pyperclip
draft_paths = converter.convert_from_clipboard(pyperclip.paste())
```

---

## API 参考

### CozeOutputParser

解析 Coze 输出的 JSON 结构。

#### 方法

##### `parse_from_clipboard(clipboard_text: str) -> Dict`

从剪贴板文本解析。

```python
parser = CozeOutputParser()
data = parser.parse_from_clipboard(clipboard_text)
```

##### `parse_from_file(file_path: str) -> Dict`

从文件解析。

```python
parser = CozeOutputParser()
data = parser.parse_from_file('coze_output.json')
```

##### `get_drafts() -> List[Dict]`

获取所有草稿列表。

```python
drafts = parser.get_drafts()
for draft in drafts:
    print(draft['project']['name'])
```

##### `get_draft_info(draft: Dict) -> Dict`

获取草稿统计信息。

```python
info = parser.get_draft_info(drafts[0])
print(f"分辨率: {info['resolution']}")
print(f"轨道数量: {info['track_count']}")
print(f"总片段数: {info['total_segments']}")
```

##### `print_summary()`

打印解析摘要。

```python
parser.parse_from_file('coze_output.json')
parser.print_summary()
```

输出示例:

```
============================================================
Coze输出解析摘要
============================================================
格式版本: 1.0
导出类型: single_draft
草稿数量: 1

草稿 1:
  ID: 6a65b7a9-5e3b-45f1-9c9b-583d8a5fd1f6
  项目名称: Coze剪映项目
  分辨率: 1440x1080
  帧率: 30 fps
  总时长: 0 ms
  轨道数量: 3
  轨道类型: {'audio': 1, 'image': 1, 'text': 1}
  总片段数: 30
  状态: created
```

---

### CozeToDraftConverter

完整的转换流程管理器。

#### 初始化

```python
converter = CozeToDraftConverter(output_base_dir='./JianyingProjects')
```

**参数:**

- `output_base_dir`: 草稿输出根目录(默认: `./JianyingProjects`)

#### 方法

##### `convert_from_file(file_path: str) -> List[str]`

从文件转换生成草稿。

```python
draft_paths = converter.convert_from_file('coze_output.json')
```

**返回:** 生成的草稿路径列表

##### `convert_from_clipboard(clipboard_text: str) -> List[str]`

从剪贴板转换生成草稿。

```python
draft_paths = converter.convert_from_clipboard(clipboard_text)
```

**返回:** 生成的草稿路径列表

---

### 便捷函数

#### `convert_coze_to_draft(input_source, is_file=True, output_dir='./JianyingProjects')`

一步完成转换。

```python
from src.utils.coze_to_draft import convert_coze_to_draft

# 从文件
paths = convert_coze_to_draft('coze_output.json')

# 从剪贴板
import pyperclip
paths = convert_coze_to_draft(pyperclip.paste(), is_file=False)
```

---

## 工作流程

### 完整转换流程图

```
┌─────────────────────┐
│  Coze JSON输出      │
│ {"output": "..."}   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  1. 解析JSON        │
│  CozeOutputParser   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. 创建草稿文件夹  │
│  ./JianyingProjects/│
│    └── 项目名/      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. 初始化组件      │
│  - DraftFolder      │
│  - MaterialManager  │
│  - Converter        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. 处理轨道        │
│  遍历每条轨道:      │
│  - audio            │
│  - image            │
│  - text             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. 处理片段        │
│  遍历每个片段:      │
│  - 下载素材(URL)    │
│  - 转换数据结构     │
│  - 添加到草稿       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. 保存草稿        │
│  生成:              │
│  - draft_content    │
│  - draft_meta_info  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ✅ 完成!           │
│  草稿可导入剪映     │
└─────────────────────┘
```

### 数据流转

```
Coze JSON
    ↓
CozeOutputParser.parse_from_file()
    ↓ (parsed_data)
CozeToDraftConverter._convert_drafts()
    ↓ (draft_data)
CozeToDraftConverter._convert_single_draft()
    ↓ (segments)
    ├─→ MaterialManager.create_material()  # 下载素材
    │       ↓ (Material对象)
    └─→ DraftInterfaceConverter.convert_***_segment_config()
            ↓ (Segment对象)
        Script.save()  # 保存到磁盘
```

---

## 示例代码

### 示例 1: 批量转换多个草稿

假设 Coze 输出包含 3 个草稿:

```json
{
  "output": "{\"draft_count\": 3, \"drafts\": [...]}"
}
```

转换代码:

```python
from src.utils.coze_to_draft import convert_coze_to_draft

draft_paths = convert_coze_to_draft('multi_drafts.json')

print(f"生成了 {len(draft_paths)} 个草稿:")
for i, path in enumerate(draft_paths, 1):
    print(f"{i}. {path}")
```

输出:

```
步骤1: 解析Coze输出...
格式版本: 1.0
导出类型: multiple_drafts
草稿数量: 3

步骤2: 开始转换 3 个草稿...
============================================================
正在处理草稿 1/3
============================================================
...
✅ 草稿 1 生成成功: ./JianyingProjects/项目1
✅ 草稿 2 生成成功: ./JianyingProjects/项目2
✅ 草稿 3 生成成功: ./JianyingProjects/项目3
```

---

### 示例 2: 仅解析不生成

如果只想查看 Coze 输出的信息,不生成草稿:

```python
from src.utils.coze_parser import CozeOutputParser

parser = CozeOutputParser()
data = parser.parse_from_file('coze_output.json')

# 打印摘要
parser.print_summary()

# 获取详细信息
for i, draft in enumerate(parser.get_drafts(), 1):
    info = parser.get_draft_info(draft)

    print(f"\n草稿 {i}: {info['project_name']}")
    print(f"  分辨率: {info['resolution']}")
    print(f"  轨道统计: {info['track_stats']}")
    print(f"  总片段数: {info['total_segments']}")

    # 遍历轨道
    for track in draft['tracks']:
        track_type = track['track_type']
        segments = track['segments']

        print(f"\n  {track_type} 轨道:")
        for seg in segments[:3]:  # 只显示前3个
            time_range = seg['time_range']
            print(f"    - {seg['type']}: {time_range['start']}ms ~ {time_range['end']}ms")
```

---

### 示例 3: 集成到 GUI

将转换功能集成到现有 GUI:

```python
# main_window.py
from src.utils.coze_to_draft import convert_coze_to_draft
import pyperclip

def on_import_from_coze_clicked(self):
    """从Coze导入按钮点击事件"""
    try:
        # 从剪贴板获取
        clipboard_text = pyperclip.paste()

        # 显示进度
        self.show_progress("正在转换Coze输出...")

        # 转换
        draft_paths = convert_coze_to_draft(
            input_source=clipboard_text,
            is_file=False,
            output_dir=self.output_dir
        )

        # 显示结果
        self.show_success(f"成功生成 {len(draft_paths)} 个草稿!")
        for path in draft_paths:
            self.log(f"  - {path}")

    except Exception as e:
        self.show_error(f"导入失败: {e}")
```

---

## 常见问题

### Q1: 如何处理 URL 过期的素材?

**A:** MaterialManager 会自动下载素材到本地 Assets 文件夹。如果 URL 过期导致下载失败,会记录错误日志但继续处理其他片段。

解决方案:

1. 确保 Coze 输出中的 URL 在有效期内
2. 如果 URL 已过期,需要重新从 Coze 生成输出

---

### Q2: 支持哪些素材类型?

**A:** 当前支持:

- ✅ 音频: `.mp3`, `.wav`, `.m4a`等
- ✅ 图片: `.jpg`, `.png`, `.webp`等(作为 VideoMaterial)
- ⚠️ 视频: `.mp4`等(需要确认 pyJianYingDraft 支持)

---

### Q3: 转换后的草稿在哪里?

**A:** 默认在`./JianyingProjects/`目录下,结构如下:

```
JianyingProjects/
└── Coze剪映项目/
    ├── Coze剪映项目/
    │   ├── draft_content.json      # 草稿内容
    │   ├── draft_meta_info.json    # 草稿元信息
    │   └── Assets/                 # 素材文件夹
    │       ├── audio_xxx.mp3
    │       ├── image_yyy.jpg
    │       └── ...
```

将`Coze剪映项目`文件夹复制到剪映的草稿目录即可导入。

---

### Q4: 如何自定义输出目录?

**A:**

```python
# 方法1: 使用便捷函数
draft_paths = convert_coze_to_draft(
    'coze_output.json',
    output_dir='C:/MyDrafts'
)

# 方法2: 使用类接口
converter = CozeToDraftConverter(output_base_dir='C:/MyDrafts')
draft_paths = converter.convert_from_file('coze_output.json')
```

---

### Q5: 为什么有些片段没有被转换?

**A:** 可能的原因:

1. **素材下载失败** - 检查 URL 是否有效
2. **不支持的片段类型** - 当前支持 audio/image/text,video 支持有限
3. **数据格式错误** - 检查 Coze 输出格式是否正确

查看日志文件`logs/app.log`获取详细错误信息。

---

### Q6: 如何调试转换过程?

**A:**

1. **使用测试脚本**:

```bash
python test_coze_conversion.py
```

2. **启用详细日志**:

```python
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.setLevel('DEBUG')  # 设置为DEBUG级别
```

3. **分步测试**:

```python
# 第1步: 只解析
parser = CozeOutputParser()
data = parser.parse_from_file('coze_output.json')
parser.print_summary()

# 第2步: 检查数据
drafts = parser.get_drafts()
print(drafts[0]['tracks'])

# 第3步: 完整转换
convert_coze_to_draft('coze_output.json')
```

---

## 运行测试

```bash
# 测试解析和转换
python test_coze_conversion.py

# 仅测试解析器
python -m src.utils.coze_parser

# 查看帮助
python -c "from src.utils.coze_to_draft import convert_coze_to_draft; help(convert_coze_to_draft)"
```

---

## 进阶使用

### 自定义素材处理

如果需要自定义素材下载或处理逻辑:

```python
class CustomConverter(CozeToDraftConverter):
    def _process_segment(self, segment, track_type, converter, material_manager, seg_idx):
        # 自定义处理逻辑
        if segment.get('type') == 'video':
            # 特殊处理视频
            pass
        else:
            # 使用默认处理
            super()._process_segment(segment, track_type, converter, material_manager, seg_idx)

# 使用自定义转换器
custom = CustomConverter()
draft_paths = custom.convert_from_file('coze_output.json')
```

---

## 总结

✅ **简单易用** - 一行代码完成转换  
✅ **功能完整** - 支持多草稿、多轨道、多片段类型  
✅ **自动化** - 自动下载素材、自动创建文件夹  
✅ **可扩展** - 类接口支持自定义扩展

现在你可以轻松将 Coze 的输出转换为剪映草稿了! 🎉
