# add_captions - 添加字幕轨道工具

## 功能描述
将文本/字幕内容添加到现有草稿中，通过创建新的文本轨道。每次调用此工具都会创建一个包含所有字幕片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                               # 要修改的草稿UUID
    captions: List[Dict[str, Any]]              # 字幕字典列表
    font_family: Optional[str] = "思源黑体"      # 字体名称
    font_size: Optional[int] = 48               # 字体大小
    color: Optional[str] = "#FFFFFF"            # 文字颜色
    position_x: Optional[float] = 0.5           # 水平位置(0-1)
    position_y: Optional[float] = 0.9           # 垂直位置(0-1)
    alignment: Optional[str] = "center"         # 文字对齐方式
```

### 字幕字典格式
每个字幕必须包含以下字段：
```python
{
    "text": str,                    # 字幕文本内容(必需)
    "start_time": int,              # 开始时间(毫秒，必需)
    "end_time": int,                # 结束时间(毫秒，必需)
    "position_x": float,            # 可选：该字幕的水平位置(0-1)
    "position_y": float             # 可选：该字幕的垂直位置(0-1)
}
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **captions**: 字幕字典列表，必需参数，至少包含一个有效字幕
- **font_family**: 字体名称，默认为"思源黑体"
- **font_size**: 字体大小，默认为48像素
- **color**: 文字颜色，默认为白色"#FFFFFF"
- **position_x**: 默认水平位置(0-1)，0为左，1为右，默认0.5居中
- **position_y**: 默认垂直位置(0-1)，0为上，1为下，默认0.9底部
- **alignment**: 文字对齐方式，可选"left"、"center"、"right"

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    success: bool = True              # 操作成功状态
    message: str = "字幕轨道添加成功"    # 状态消息
    track_index: int = -1             # 创建的轨道索引
    total_captions: int = 0           # 添加的字幕总数
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_captions",
  "input": {
    "draft_id": "uuid-of-draft",
    "captions": [
      {
        "text": "欢迎使用Coze剪映助手",
        "start_time": 0,
        "end_time": 3000
      },
      {
        "text": "让视频制作更简单",
        "start_time": 3000,
        "end_time": 6000
      }
    ]
  }
}
```

### 自定义样式和位置
```json
{
  "tool": "add_captions",
  "input": {
    "draft_id": "uuid-of-draft",
    "captions": [
      {
        "text": "标题字幕",
        "start_time": 1000,
        "end_time": 4000,
        "position_x": 0.5,
        "position_y": 0.2
      },
      {
        "text": "底部字幕",
        "start_time": 4000,
        "end_time": 7000
      }
    ],
    "font_family": "微软雅黑",
    "font_size": 56,
    "color": "#FFD700",
    "position_x": 0.5,
    "position_y": 0.85,
    "alignment": "center"
  }
}
```

### 在Coze工作流中使用
```json
{
  "step": 4,
  "name": "添加字幕文本",
  "tool": "add_captions",
  "input": {
    "draft_id": "{{project_draft.draft_id}}",
    "captions": "{{user_input.subtitle_list}}",
    "font_family": "{{user_input.font_name}}",
    "font_size": "{{user_input.font_size}}",
    "color": "{{user_input.text_color}}"
  },
  "output_variable": "captions_added"
}
```

## 注意事项

### 输入验证
- draft_id必须是有效的UUID格式
- captions不能为空，必须包含至少一个有效字幕
- 每个字幕必须有text、start_time、end_time字段
- end_time必须大于start_time
- position_x和position_y必须在0-1范围内
- font_size必须是正整数
- color必须是有效的十六进制颜色码

### 字幕时间管理
- 时间单位为毫秒
- 字幕可以重叠显示
- 支持单个字幕的自定义位置
- 自动更新草稿总时长

### 文字样式支持
- 支持系统字体和自定义字体
- 颜色格式：#RRGGBB (如 #FFFFFF 白色)
- 位置坐标：(0,0)左上角，(1,1)右下角
- 对齐方式：left左对齐、center居中、right右对齐

### 高级功能预留
- 描边效果：stroke设置
- 阴影效果：shadow设置  
- 背景色：background设置
- 动画效果：intro/outro动画
- 关键帧：position/scale/rotation/opacity关键帧

### 常见使用场景
- **对话字幕**: 电影、访谈等对话字幕
- **标题字幕**: 视频开头标题、章节标题
- **说明字幕**: 产品介绍、教程说明
- **装饰文字**: 创意视频的装饰文字

### 错误处理
- UUID格式验证失败会返回详细错误信息
- 草稿不存在会返回相应错误
- 字幕格式验证失败会指出具体问题
- 时间范围验证失败会返回错误详情

## 相关工具

- `create_draft`: 创建新草稿
- `add_videos`: 添加视频轨道
- `add_audios`: 添加音频轨道
- `add_effects`: 添加特效轨道
- `export_drafts`: 导出草稿数据