# 针对 Issue 提出问题的直接回答

## 问题 1: 为什么会在 Releases 中发布 v1.0.0 版本？

### 直接回答

**原因**：pyproject.toml 中的 `major_on_zero = false` 配置被误解了。

### 详细解释

您在配置文件中这样写的：

```toml
major_on_zero = false  # 强制保持 0.x.x 版本，feat 只触发 MINOR 升级
```

但是 **注释是错误的**！`major_on_zero` 的实际含义与您理解的相反：

| 配置值 | 实际效果 |
|--------|----------|
| `major_on_zero = true` | ✅ 在 0.x.x 阶段，遇到 `feat` 提交 → 触发 MINOR 升级 (0.0.4 → 0.1.0) |
| `major_on_zero = false` | ❌ 在 0.x.x 阶段，遇到 `feat` 提交 → 触发 MAJOR 升级 (0.0.4 → 1.0.0) |

### 触发事件

在从 v0.0.4 到 v1.0.0 之间的 15 个提交中，有一个关键提交：

```
feat: 测试版本 (#179)
```

这是一个符合 Conventional Commits 规范的 `feat` 类型提交。

**semantic-release 的判断逻辑**：
1. 检测到 `feat:` 提交
2. 当前版本是 0.0.4（0.x.x 阶段）
3. 配置是 `major_on_zero = false`（不使用 Zero-Ver 模式）
4. 结论：**项目准备离开 0.x.x，升级到 1.0.0**

### 您的预期 vs 实际配置

您的预期：
> "没有我主动使用 `feat!` 之类的情况下，不会更新大版本号"

要实现这个预期，应该配置：
```toml
major_on_zero = true  # 在 0.x.x 阶段，feat 只触发 MINOR 升级
```

## 问题 2: 为什么 Releases 里没有详细的提交信息？

### 直接回答

有 **三个原因** 导致 Release Notes 只显示 "Initial Release"：

### 原因 1：Changelog 排除规则太严格

您的配置排除了大部分提交：

```toml
[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "^chore\\(release\\):",
    "^Merge pull request",   # ← 排除了所有 PR 合并
    "^Merge branch",          # ← 排除了所有分支合并
]
```

从 v0.0.4 到 v1.0.0 的 15 个提交中：
- "Develop (#186)" → 被排除（是 merge）
- "Develop (#185)" → 被排除（是 merge）
- "Merge branch 'develop'" → 被排除
- "Merge pull request #176" → 被排除

### 原因 2：提交消息格式不规范

semantic-release 只识别符合 Conventional Commits 格式的提交：

**✅ 能识别**：
- `feat: 测试版本 (#179)`
- `fix: 测试 (#182)`
- `fix: see if merge (#181)`

**❌ 不能识别**（缺少类型前缀）：
- "Develop (#186)"
- "更新当前项目管理框架 (#180)"
- "测试推送 (#178)"
- "更新当前项目配置 (#177)"

### 原因 3：首次运行 semantic-release

v0.0.4 可能是手动创建的 release，semantic-release 首次运行时：
1. 找不到上一次 release 的记录
2. 找到的符合格式的提交很少
3. 所以显示为 "Initial Release"

### 您的预期 vs 实际情况

您的预期：
> "在 develop 把那么多 commit 合并提交的时候，这些各个的 commit 会汇总到 Releases 对应的发布里面去"

实际情况：
- ❌ Merge commits 被配置排除了
- ❌ 大多数 commit 消息格式不规范，无法识别
- ❌ 即使不排除 merge，内容也不会自动展开（只会显示 merge 消息本身）

## 如何解决？

### 立即行动（选择一个）

#### 选项 A：接受 v1.0.0（推荐）

**理由**：
- v1.0.0 已经发布并被下载
- 回退会造成混乱
- 可以视为项目进入稳定阶段

**操作**：
1. 保持配置不变
2. 在 README 中说明："v1.0.0 标志着项目进入稳定阶段"
3. 继续使用标准 semantic versioning

#### 选项 B：回退到 0.x.x

**操作**：
```bash
# 1. 删除 v1.0.0
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
# 在 GitHub UI 删除 Release

# 2. 修改配置
# 在 pyproject.toml 中改为：
major_on_zero = true

# 3. 手动创建 v0.0.5
# 更新 pyproject.toml 和 app/__init__.py 中的版本号为 0.0.5
git add .
git commit -m "fix: 修正版本号和配置"
git tag v0.0.5
git push origin v0.0.5 main
```

**风险**：
- 已有用户下载了 v1.0.0
- 需要发公告解释

### 长期改进

#### 1. 修正配置（如果选择保持 0.x.x）

```toml
[tool.semantic_release]
# 在 0.x.x 阶段，feat 触发 MINOR 而非 MAJOR
major_on_zero = true  # 改为 true
```

#### 2. 优化 Changelog 规则

```toml
[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "^chore\\(release\\):",
    # 移除 merge 相关的排除，让更多提交出现在 changelog 中
]
```

#### 3. 规范提交格式

使用 PR 模板强制规范格式，创建 `.github/pull_request_template.md`：

```markdown
<!-- PR 标题格式：feat: 描述 或 fix: 描述 -->

## 变更类型
- [ ] feat: 新功能
- [ ] fix: Bug修复
- [ ] docs: 文档
- [ ] chore: 杂项

## 描述
<!-- 详细描述，这将出现在 Release Notes 中 -->

## 破坏性变更
- [ ] 是（标题末尾加 `!`）
- [ ] 否
```

#### 4. 使用 Squash Merge

在 GitHub 仓库设置中：
- Settings → General → Pull Requests
- 只启用 "Allow squash merging"
- 每个 PR 合并时变成一个规范的 commit

## 总结

### 核心问题

1. **配置误解**：`major_on_zero = false` 会在遇到 `feat` 时升级到 1.0.0
2. **Changelog 配置**：排除了 merge commits 和格式不规范的提交
3. **提交规范**：大多数提交缺少类型前缀（`feat:`、`fix:` 等）

### 快速记忆

```
major_on_zero = true  → 保持 0.x.x  ← 您想要的
major_on_zero = false → 升级到 1.0.0 ← 实际配置
```

### 推荐配置

```toml
[tool.semantic_release]
major_on_zero = true  # 在 0.x.x 阶段，feat 触发 MINOR

[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "^chore\\(release\\):",
    # 减少排除，保留更多提交信息
]
```

## 参考文档

详细的分析报告请查看：
- [完整调查报告](./v1.0.0_release_analysis.md)
- [快速参考](./README.md)

相关文档链接：
- [Python Semantic Release - major_on_zero](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#config-major-on-zero)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [语义化版本](https://semver.org/lang/zh-CN/)
