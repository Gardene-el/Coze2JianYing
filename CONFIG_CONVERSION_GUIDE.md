# 项目配置转换说明

## 概述

将项目从**依赖库配置**改为**应用配置**。

## 主要变更

### 1. setup.py 修改

#### 删除的内容
- 移除了 `from setuptools import find_packages` 导入
- 移除了 `packages=find_packages()` 参数

#### 修改的内容
- **Intended Audience 分类器**: 
  - 原值: `"Intended Audience :: Developers"`
  - 新值: `"Intended Audience :: End Users/Desktop"`
  - 原因: 应用程序面向最终用户，而不是开发者

- **Entry Point**:
  - 原值: `"coze-2-jianying=coze_plugin.main:main"`
  - 新值: `"coze-2-jianying=src.main:main"`
  - 原因: 指向 GUI 应用程序入口，而不是插件入口

### 2. 新增测试文件

创建了 `test_app_config.py` 用于验证应用配置的正确性。

测试内容包括:
- ✅ Entry point 是否正确创建
- ✅ 包不应该被导入（应用配置特性）
- ✅ setup.py 结构正确（无 find_packages）
- ✅ Classifiers 适合应用程序

## 库配置 vs 应用配置

### 库配置（之前）
- 使用 `find_packages()` 查找并导出所有 Python 包
- 可以被其他项目通过 `import` 导入使用
- 面向开发者
- 示例: `import coze_2_jianying`

### 应用配置（现在）
- 不导出包，只提供命令行入口
- 不能被其他项目导入
- 面向最终用户
- 使用方式: `coze-2-jianying` 命令启动应用

## 影响范围

### 不受影响的部分
- ✅ 依赖安装 (requirements.txt)
- ✅ CI/CD 工作流 (.github/workflows/build.yml)
- ✅ PyInstaller 打包 (build.py)
- ✅ 应用程序功能
- ✅ 项目文档

### 变更的部分
- ⚠️ 不能再通过 `import coze_2_jianying` 导入包
- ✅ 仍然可以通过 `coze-2-jianying` 命令运行应用
- ✅ 仍然可以使用 `pip install -e .` 进行开发安装

## 验证方法

```bash
# 1. 安装项目
pip install -e .

# 2. 验证入口点
which coze-2-jianying

# 3. 运行测试
python test_app_config.py

# 4. 验证不能作为库导入（预期失败）
python -c "import coze_2_jianying"  # 应该报错 ImportError
```

## 为什么要做这个改变？

1. **项目定位明确**: Coze2JianYing 是一个桌面应用程序，不是供其他项目导入的库
2. **减少混淆**: 避免用户误以为可以作为库导入使用
3. **更符合实际**: build.py 打包成 .exe 文件，明显是应用程序而非库
4. **更好的语义**: 应用配置更准确地反映了项目的实际用途
