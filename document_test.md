# 工具函数 Add Images

工具名称：add_images
工具描述：添加图片工具处理器
向现有草稿添加图片片段，创建新的图片轨道。
每次调用创建一个包含所有指定图片的新轨道。

## 输入参数

```python
class Input(NamedTuple):
    draft_id: str  # 现有草稿的 UUID
    image_infos: List[str]  # 包含image信息的 JSON 字符串列表
```

### 字段说明

- `draft_id`: 现有草稿的 UUID
- `image_infos`: 包含image信息的 JSON 字符串列表

## 输出参数

```python
class Output(NamedTuple):
    segment_ids: List[str]  # 生成的片段 UUID 列表
    success: bool = True  # 操作成功状态
    message: str = '图片添加成功'  # 状态消息
```

### 字段说明

- `segment_ids`: 生成的片段 UUID 列表
