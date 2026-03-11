# GUI 模块重构说明

本目录包含基于 `customtkinter` 重构后的 GUI 代码。

## 目录结构

- `main_window.py`: 主窗口，包含侧边栏导航和页面管理。
- `log_window.py`: 独立日志窗口。
- `base_page.py`: 所有页面的基类。
- `pages/`: 包含各个功能页面的实现。
  - `draft_generator_page.py`: 草稿生成页面。
  - `cloud_service_page.py`: 云端服务页面。
  - `script_executor_page.py`: 脚本执行页面。
  - `settings_page.py`: 系统设置页面。

## 已弃用的文件

以下文件是旧版 `tkinter` 实现的遗留文件，不再被使用，可以安全删除：

- `base_tab.py`
- `cloud_service_tab.py`
- `draft_generator_tab.py`
- `script_executor_tab.py`
- `example_tab.py`

## 设置管理

全局设置现在通过 `app/utils/settings_manager.py` 进行管理，并持久化保存到 `data/settings.json`。
