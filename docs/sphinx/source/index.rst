Welcome to Coze2JianYing's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/coze_plugin
   modules/src

Coze2JianYing - 开源的Coze剪映小助手
=====================================

Coze2JianYing 是一个完整的 Coze 到剪映工作流项目，整合了两个强关联但相对独立的子项目：

* **Coze 插件** (``coze_plugin/``) - Coze 平台上的工具函数，处理参数和导出 JSON
* **草稿生成器** (``src/``) - 独立应用，将 JSON 转换为剪映草稿文件

项目概述
--------

工作流程概述
~~~~~~~~~~~~

完整的工作流涉及四个步骤的协作：

1. **Coze 工作流** → 生成素材和对应的参数
2. **Coze 插件** (``coze_plugin/``) → 在 Coze 中调用工具函数，将素材和参数处理后导出标准 JSON 数据
3. **草稿生成器** (``src/``) → 将 JSON 数据转换为剪映草稿文件，下载素材，生成完整项目
4. **剪映** → 用户在剪映中打开生成的草稿，进行最终编辑

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
