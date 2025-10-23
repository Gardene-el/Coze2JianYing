# make_image_info 和数组字符串支持更新总结

## 问题描述

根据 Issue 的需求：
1. 当前 `image_infos` 支持**数组对象**和**字符串**格式
2. 需要添加对**数组字符串**格式的支持
3. 创建 `make_image_info` 工具函数，用于生成单个图片配置的字符串
4. 使用场景：多次调用 `make_image_info` 生成字符串 → 收集到数组 → 传递给 `add_images`

## 实现的更改

### 1. 新增 `make_image_info` 工具 (`tools/make_image_info/`)

#### 功能
- 接收图片的所有可配置参数
- 输出紧凑的 JSON 字符串表示
- 只包含非默认值的参数（优化输出）

#### 支持的参数
**必需参数：**
- `image_url`: 图片 URL
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

**可选参数：**
- 尺寸：`width`, `height`
- 变换：`position_x`, `position_y`, `scale_x`, `scale_y`, `rotation`, `opacity`
- 裁剪：`crop_enabled`, `crop_left`, `crop_top`, `crop_right`, `crop_bottom`
- 效果：`filter_type`, `filter_intensity`, `transition_type`, `transition_duration`
- 背景：`background_blur`, `background_color`, `fit_mode`
- 动画：`in_animation`, `in_animation_duration`, `outro_animation`, `outro_animation_duration`

#### 输出示例
```json
{"image_url":"https://example.com/image.jpg","start":0,"end":3000,"width":1920,"height":1080}
```

### 2. 修改 `add_images` 工具以支持数组字符串

#### 更新 `parse_image_infos` 函数
在 `tools/add_images/handler.py` 中，添加了对数组字符串的检测和解析：

```python
if isinstance(image_infos_input, list):
    # 检查是否为数组字符串格式
    if image_infos_input and isinstance(image_infos_input[0], str):
        # 数组字符串 - 解析每个字符串为 JSON
        parsed_infos = []
        for i, info_str in enumerate(image_infos_input):
            try:
                parsed_info = json.loads(info_str)
                parsed_infos.append(parsed_info)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in image_infos[{i}]: {str(e)}")
        image_infos = parsed_infos
    else:
        # 数组对象（原有行为）
        image_infos = image_infos_input
```

### 3. 支持的输入格式

现在 `add_images` 的 `image_infos` 参数支持以下格式：

#### 格式1: 数组对象（原有，适合静态配置）
```json
[
  {
    "image_url": "https://example.com/image.jpg",
    "start": 0,
    "end": 3000,
    "width": 1920,
    "height": 1080
  }
]
```

#### 格式2: 数组字符串（新增，适合动态配置）
```json
[
  "{\"image_url\":\"https://example.com/image1.jpg\",\"start\":0,\"end\":3000}",
  "{\"image_url\":\"https://example.com/image2.jpg\",\"start\":3000,\"end\":6000}"
]
```

#### 格式3: JSON字符串（原有）
```json
"[{\"image_url\":\"https://example.com/image.jpg\",\"start\":0,\"end\":3000}]"
```

### 4. 完整的工作流示例

```python
# 步骤 1: 使用 make_image_info 生成图片信息字符串
image1 = make_image_info(
    image_url="https://example.com/image1.jpg",
    start=0,
    end=3000,
    width=1920,
    height=1080
)
# 返回: {"image_url":"https://example.com/image1.jpg","start":0,"end":3000,"width":1920,"height":1080}

image2 = make_image_info(
    image_url="https://example.com/image2.jpg",
    start=3000,
    end=6000,
    in_animation="轻微放大"
)
# 返回: {"image_url":"https://example.com/image2.jpg","start":3000,"end":6000,"in_animation":"轻微放大"}

# 步骤 2: 将字符串收集到数组中
image_infos_array = [
    image1.image_info_string,
    image2.image_info_string
]

# 步骤 3: 传递数组字符串给 add_images
add_images(
    draft_id="your-draft-uuid",
    image_infos=image_infos_array  # 数组字符串格式
)
```

## 测试覆盖

### 新增测试文件
- `tests/test_make_image_info.py` - 测试 make_image_info 工具和数组字符串集成

#### 测试场景
1. **make_image_info 基本功能**
   - 最小必需参数
   - 完整可选参数
   - 默认值不包含在输出中
   - 错误处理（缺少参数、无效时间范围）

2. **add_images 数组字符串支持**
   - 数组字符串解析
   - 向后兼容性（数组对象仍然工作）
   - 空数组处理
   - 无效 JSON 错误处理

3. **完整集成测试**
   - make_image_info → 数组 → add_images
   - 草稿配置正确更新
   - 所有参数正确传递

4. **中文字符支持**
   - 中文动画名称和滤镜名称

### 更新的测试文件
- `tests/test_add_images.py` - 修复了测试中的类型注解问题

### 测试结果
所有测试通过 ✅
- `test_make_image_info.py`: 4/4 通过
- `test_add_images_simple.py`: 5/5 通过
- `test_add_images.py`: 4/4 通过

## 文档更新

### 新增文档
1. `tools/make_image_info/README.md` - make_image_info 工具完整文档
2. `examples/make_image_info_demo.py` - 完整工作流演示

### 更新文档
1. `tools/add_images/README.md` - 添加数组字符串格式说明和示例

## 向后兼容性

✅ **100% 向后兼容**
- 所有原有的输入格式继续正常工作
- 数组对象格式（推荐用于静态配置）
- JSON 字符串格式
- 新增的数组字符串格式不影响现有功能

## 在 Coze 工作流中的应用

这个更新特别适合 Coze 工作流的动态场景：

```
1. [make_image_info 节点1] → 生成第一张图片配置
   输出: image_info_string

2. [make_image_info 节点2] → 生成第二张图片配置
   输出: image_info_string

3. [数组收集节点] → 组合多个字符串
   输出: [string1, string2, ...]

4. [add_images 节点] → 添加到草稿
   输入: draft_id + image_infos (数组字符串)
```

## 关键技术点

1. **灵活的输入解析**：通过检查数组第一个元素的类型来区分数组字符串和数组对象
2. **参数优化**：make_image_info 只输出非默认值，保持字符串紧凑
3. **完整的参数支持**：涵盖所有 pyJianYingDraft 支持的图片参数
4. **错误处理**：详细的验证和错误消息
5. **中文支持**：正确处理中文字符（动画、滤镜名称等）

## 文件变更清单

### 新增文件
- `tools/make_image_info/handler.py`
- `tools/make_image_info/README.md`
- `tests/test_make_image_info.py`
- `examples/make_image_info_demo.py`

### 修改文件
- `tools/add_images/handler.py` - 添加数组字符串支持
- `tools/add_images/README.md` - 更新文档
- `tests/test_add_images.py` - 修复类型注解

## 使用建议

### 何时使用数组字符串格式
✅ 推荐使用场景：
- Coze 工作流中需要动态生成图片配置
- 需要在多个节点之间传递图片信息
- 每个图片的配置来自不同的数据源

### 何时使用数组对象格式
✅ 推荐使用场景：
- 静态配置，图片信息固定
- 在 Python 代码中直接构建配置
- 不需要序列化传递的场景
