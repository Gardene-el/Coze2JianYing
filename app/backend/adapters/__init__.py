"""
adapters 包 — 第三方库适配层。

各模块负责将内部数据结构（config dict 等）转换为对应第三方库的对象，
均为无状态纯函数，不含任何 I/O 操作。
"""
from app.backend.adapters import jianying_adapter  # noqa: F401
