# Export Drafts Tool

导出草稿数据供草稿生成器使用的Coze工具函数。

## 功能描述

本工具用于从`/tmp`目录中读取已创建的草稿配置，将其转换为标准化的JSON格式数据，供草稿生成器使用。支持单个草稿导出或批量导出多个草稿，并可选择是否在导出后清理临时文件。

## 核心特性

### 灵活的导出模式
- **单草稿导出**: 传入单个UUID字符串
- **批量导出**: 传入UUID字符串数组
- **混合处理**: 自动处理部分成功、部分失败的情况
- **格式标准化**: 生成统一的草稿生成器数据格式

### 完整的数据验证
- UUID格式验证
- 文件存在性检查
- JSON格式验证
- 配置完整性验证

### 可选的文件清理
- 支持导出后自动清理`/tmp`中的临时文件
- 仅清理成功导出的文件
- 详细的清理状态报告

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_ids: Union[str, List[str]]  # 单个UUID或UUID列表
    remove_temp_files: bool = False   # 是否删除临时文件
```

### 参数详细说明

#### draft_ids (string | array)
- **描述**: 要导出的草稿ID，可以是单个UUID字符串或UUID字符串数组
- **单个草稿**: `"123e4567-e89b-12d3-a456-426614174000"`
- **多个草稿**: `["uuid1", "uuid2", "uuid3"]`
- **约束**: 必须是有效的UUID格式

#### remove_temp_files (boolean)
- **描述**: 是否在导出成功后删除`/tmp`中的临时文件
- **默认值**: `false`
- **true**: 导出后删除对应的草稿文件夹
- **false**: 保留临时文件，便于后续操作

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    draft_data: str        # 草稿生成器JSON字符串
    exported_count: int    # 成功导出的草稿数量
    success: bool = True   # 操作是否成功
    message: str = "草稿导出成功"  # 详细状态消息
```

### 输出字段说明

#### draft_data (string)
- **描述**: 格式化的JSON字符串，包含完整的草稿数据
- **格式**: 标准化的草稿生成器数据格式
- **编码**: UTF-8，支持中文内容
- **用途**: 直接传递给草稿生成器使用

#### exported_count (integer)
- **描述**: 成功导出的草稿数量
- **范围**: 0到请求的草稿总数
- **用途**: 用于判断批量导出的成功率

#### success (boolean)
- **描述**: 整体操作是否成功
- **true**: 至少有一个草稿成功导出
- **false**: 所有草稿都导出失败

#### message (string)
- **描述**: 详细的操作结果描述
- **成功示例**: "成功导出 2 个草稿; 临时文件已清理"
- **失败示例**: "失败 1 个: uuid1: 草稿文件夹不存在"

## 使用示例

### 单草稿导出

#### 基本导出（保留临时文件）
```json
{
  "draft_ids": "123e4567-e89b-12d3-a456-426614174000",
  "remove_temp_files": false
}
```

**预期输出**:
```json
{
  "draft_data": "{\"format_version\":\"1.0\",\"export_type\":\"single_draft\",\"draft_count\":1,\"drafts\":[...]}",
  "exported_count": 1,
  "success": true,
  "message": "成功导出 1 个草稿"
}
```

#### 导出并清理临时文件
```json
{
  "draft_ids": "123e4567-e89b-12d3-a456-426614174000",
  "remove_temp_files": true
}
```

### 批量草稿导出

#### 导出多个草稿
```json
{
  "draft_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234f5678-f90c-23e4-b567-537725285111",
    "345a6789-a01d-34f5-c678-648836396222"
  ],
  "remove_temp_files": true
}
```

**预期输出**:
```json
{
  "draft_data": "{\"format_version\":\"1.0\",\"export_type\":\"batch_draft\",\"draft_count\":3,\"drafts\":[...]}",
  "exported_count": 3,
  "success": true,
  "message": "成功导出 3 个草稿; 临时文件已清理"
}
```

### 在Coze工作流中的使用

#### 单草稿导出
```json
{
  "tool": "export_drafts",
  "input": {
    "draft_ids": "{{draft_creation.draft_id}}",
    "remove_temp_files": true
  },
  "output_variable": "exported_draft"
}
```

#### 批量导出（收集多个草稿ID）
```json
{
  "tool": "export_drafts",
  "input": {
    "draft_ids": ["{{draft1.draft_id}}", "{{draft2.draft_id}}", "{{draft3.draft_id}}"],
    "remove_temp_files": false
  },
  "output_variable": "batch_exported_drafts"
}
```

## 导出数据格式

### 单草稿导出格式
```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "123e4567-e89b-12d3-a456-426614174000",
      "project": {
        "name": "项目名称",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "video_quality": "1080p",
        "audio_quality": "320k",
        "background_color": "#000000"
      },
      "media_resources": [
        {
          "url": "https://example.com/video1.mp4",
          "resource_type": "video",
          "duration_ms": 30000,
          "format": "mp4"
        }
      ],
      "tracks": [
        {
          "track_type": "video",
          "segments": [...]
        }
      ],
      "total_duration_ms": 30000,
      "created_timestamp": 1703123456.789,
      "last_modified": 1703123456.789,
      "status": "created"
    }
  ]
}
```

### 批量草稿导出格式
```json
{
  "format_version": "1.0",
  "export_type": "batch_draft",
  "draft_count": 2,
  "drafts": [
    { /* 草稿1数据 */ },
    { /* 草稿2数据 */ }
  ]
}
```

## 错误处理

### 常见错误情况

#### UUID格式错误
```json
{
  "draft_data": "",
  "exported_count": 0,
  "success": false,
  "message": "无效的UUID格式: invalid-uuid"
}
```

#### 草稿文件不存在
```json
{
  "draft_data": "",
  "exported_count": 0,
  "success": false,
  "message": "无法加载任何草稿配置: 123e4567-e89b-12d3-a456-426614174000: 草稿文件夹不存在"
}
```

#### 部分成功情况
```json
{
  "draft_data": "{...}",
  "exported_count": 2,
  "success": true,
  "message": "成功导出 2 个草稿; 失败 1 个: uuid3: 草稿配置文件格式错误"
}
```

## 技术实现

### 文件系统操作
- 检查`/tmp/{uuid}/draft_config.json`文件存在性
- 读取和解析JSON配置文件
- 可选的递归删除草稿文件夹

### 数据验证流程
1. **UUID格式验证**: 使用标准UUID库验证格式
2. **文件存在性**: 检查草稿文件夹和配置文件
3. **JSON解析**: 验证配置文件格式正确性
4. **数据完整性**: 确保必要字段存在

### 批量处理逻辑
- 逐个处理每个草稿ID
- 收集成功和失败的结果
- 仅对成功的草稿进行清理操作
- 生成详细的状态报告

## 与草稿生成器的接口

### 数据传递流程
```
Coze工作流 → export_drafts → JSON字符串 → 草稿生成器 → 剪映草稿文件
```

### 格式兼容性
- **版本标识**: `format_version`字段标识数据格式版本
- **类型标识**: `export_type`区分单草稿和批量导出
- **数量信息**: `draft_count`提供草稿数量
- **标准结构**: 统一的草稿数据结构

## 注意事项

### Coze平台限制
- **文件系统**: 依赖`/tmp`目录中的草稿文件
- **内存限制**: 大量草稿批量导出时注意内存使用
- **JSON大小**: 输出JSON字符串可能很大，注意Coze变量限制

### 性能考虑
- **I/O操作**: 大量文件读取可能影响性能
- **JSON序列化**: 复杂草稿结构序列化耗时
- **批量处理**: 建议单次导出草稿数量不超过10个

### 数据安全
- **文件清理**: 使用`remove_temp_files=true`及时清理敏感数据
- **错误信息**: 避免在错误消息中泄露敏感路径信息
- **权限控制**: 确保仅操作`/tmp`目录下的草稿文件

### 最佳实践
- **及时导出**: 创建草稿后尽快导出，避免`/tmp`目录清理
- **错误检查**: 检查`success`字段和`exported_count`确认导出结果
- **批量限制**: 合理控制批量导出的草稿数量
- **清理策略**: 根据后续需求决定是否清理临时文件

### 故障排除

#### 常见问题
1. **"草稿文件夹不存在"**: 检查draft_id是否正确，草稿是否已被清理
2. **"草稿配置文件格式错误"**: 检查`draft_config.json`文件是否损坏
3. **"删除草稿文件失败"**: 检查文件权限和磁盘空间

#### 调试建议
- 使用单草稿导出测试基本功能
- 检查`/tmp`目录中的草稿文件结构
- 验证JSON输出格式的正确性
- 监控内存使用避免大批量导出问题

这个工具完成了整个UUID草稿管理系统的最后一环，为草稿生成器提供了标准化、可靠的数据接口。