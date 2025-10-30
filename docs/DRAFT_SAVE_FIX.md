# 草稿保存修复说明

## 问题描述

当剪映打开时，使用剪映小助手生成草稿会出现以下错误：

```
FileNotFoundError: [Errno 2] No such file or directory: 
'C:\\Users\\aloud\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft\\e559681e-6730-4c6b-b7ba-4e785e2c9f86\\draft_content.json'
```

### 根本原因

剪映在运行时会监控草稿文件夹，并自动将新创建的草稿文件夹重命名为 `draft_meta_info.json` 中的 `draft_id` 字段值。例如：

1. 代码创建文件夹：`e559681e-6730-4c6b-b7ba-4e785e2c9f86`
2. 剪映自动重命名为：`686899BC-141F-4302-846A-F83BF61460CB`（`draft_meta_info.json` 中的内部UUID）
3. `script.save()` 尝试保存到原路径时失败

这是因为 pyJianYingDraft 在创建草稿时会内部存储文件夹路径，并且不会检测外部的文件夹重命名。

## 解决方案

实现了 `_save_draft_robust()` 方法，提供**三层回退保护**：

### 第一层：标准保存
```python
try:
    script.save()  # 尝试标准保存
except FileNotFoundError:
    # 如果失败，进入第二层
```

当剪映未运行或未重命名文件夹时，此方法工作正常。

### 第二层：智能检测
当标准保存失败时：

1. **扫描基础目录**：查找所有可能被重命名的文件夹
2. **筛选候选文件夹**：
   - 必须有 `draft_meta_info.json` 文件
   - 不能有 `draft_content.json` 文件（说明还未完成保存）
   - 不是预期的文件夹名称
3. **时间戳排序**：按创建时间排序，选择最新的文件夹
4. **手动保存**：使用 `script.dumps()` 获取内容并手动写入

```python
# 使用 dumps() 获取 JSON 内容
draft_content = script.dumps()

# 手动写入到检测到的文件夹
content_path = os.path.join(renamed_folder, "draft_content.json")
with open(content_path, 'w', encoding='utf-8') as f:
    f.write(draft_content)
```

### 第三层：手动创建
如果检测也失败（极端情况）：

```python
# 确保目标文件夹存在
os.makedirs(expected_draft_folder, exist_ok=True)

# 使用 dumps() 手动保存
draft_content = script.dumps()
content_path = os.path.join(expected_draft_folder, "draft_content.json")
with open(content_path, 'w', encoding='utf-8') as f:
    f.write(draft_content)
```

## 测试覆盖

创建了全面的测试套件，涵盖四种场景：

### 测试1：正常保存
- **场景**：剪映未运行，文件夹未被重命名
- **结果**：✅ 标准保存成功

### 测试2：文件夹重命名
- **场景**：剪映重命名了文件夹
- **结果**：✅ 成功检测并保存到重命名后的文件夹

### 测试3：多个草稿
- **场景**：同时存在多个草稿，需要识别最新的
- **结果**：✅ 通过时间戳正确识别

### 测试4：回退逻辑
- **场景**：检测失败，需要手动创建
- **结果**：✅ 成功回退并手动创建保存

## 使用说明

此修复已集成到 `DraftGenerator` 中，无需额外配置：

```python
from src.utils.draft_generator import DraftGenerator

generator = DraftGenerator(output_base_dir="./output")
draft_paths = generator.generate(coze_json_content)
# 自动处理文件夹重命名
```

## 技术细节

### 文件夹检测算法

```python
def detect_renamed_folder(base_dir, expected_folder_name):
    candidates = []
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        
        # 检查条件
        if (has_draft_meta_info(folder_path) and 
            not has_draft_content(folder_path) and
            folder != expected_folder_name):
            
            candidates.append({
                'path': folder_path,
                'ctime': os.path.getctime(folder_path)
            })
    
    # 按时间排序，返回最新的
    candidates.sort(key=lambda x: x['ctime'], reverse=True)
    return candidates[0] if candidates else None
```

### 日志输出

修复包含详细的日志输出，便于调试：

```
标准保存失败 (文件夹可能被剪映重命名): [Errno 2] ...
尝试检测重命名的文件夹...
发现可能被重命名的文件夹: 686899BC-141F-4302-846A-F83BF61460CB
  原预期名称: e559681e-6730-4c6b-b7ba-4e785e2c9f86
  剪映内部ID: 686899BC-141F-4302-846A-F83BF61460CB
✅ 检测到剪映重命名的文件夹
使用手动保存方式保存到: .../686899BC-141F-4302-846A-F83BF61460CB
✅ 草稿保存成功 (已处理文件夹重命名)
```

## 向后兼容性

此修复**完全向后兼容**：

- ✅ 不影响剪映关闭时的正常流程
- ✅ 不改变公共API
- ✅ 保持原有的错误处理机制
- ✅ 添加了额外的容错能力

## 已知限制

1. **UUID 冲突**：理论上 pyJianYingDraft 生成的 UUID 可能冲突（概率极低）
2. **文件系统竞争**：如果剪映在检测过程中重命名文件夹，可能需要重试
3. **多实例并发**：多个草稿生成器同时运行时，时间戳检测可能不够精确

这些限制在实际使用中几乎不会遇到，且都有第三层回退保护。

## 相关文件

- `src/utils/draft_generator.py` - 核心修复代码
- `test_draft_save_fix.py` - 基础测试
- `test_draft_save_comprehensive.py` - 综合测试套件
- `DRAFT_SAVE_FIX.md` - 本文档
