"""
Services package — 业务逻辑层

包含所有业务逻辑处理模块，从 utils/ 重构迁移而来：
- converter.py       DraftInterfaceConverter：数据结构转换（接口数据 → pyJianYingDraft 类型）
- coze_parser.py     CozeOutputParser：解析 Coze 输出的四种格式
- material.py       MaterialService：媒体资源下载与缓存管理
- draft_generator.py DraftGenerator：编排门面，Coze JSON → 解析 → 转换 → 下载 → 保存草稿
- draft_saver.py     DraftSaver：状态数据 → pyJianYingDraft 调用 → 保存草稿文件
"""

__version__ = "0.1.0"
