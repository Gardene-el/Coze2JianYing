"""
共享常量和工具函数
集中管理各模块间重复定义的常量和逻辑
"""

# ── 类型分类 ────────────────────────────────────────────────────────

BASIC_TYPES = frozenset({
    "str", "int", "float", "bool", "None", "Any",
    "List", "Dict", "Tuple", "Set", "Optional", "Union",
})
"""基本类型集合 — 不属于此集合的 PascalCase 标识符视为自定义类型"""

# ── ID 引用字段 ─────────────────────────────────────────────────────

ID_REFERENCE_FIELDS = frozenset({"draft_id", "segment_id"})
"""作为对象引用的 ID 字段名（区别于 effect_id 等配置字符串）"""

# ── Output 过滤 ─────────────────────────────────────────────────────

EXCLUDED_OUTPUT_FIELDS = frozenset({"timestamp"})
"""从 Output 类和 README 输出参数中过滤掉的字段"""

# ── api_call 字段判定 ───────────────────────────────────────────────

_ADD_FUNCTIONS_WITHOUT_API_CALL = frozenset({"add_track", "add_segment"})


def should_have_api_call_field(func_name: str) -> bool:
    """判断函数是否应该在 Output 中包含 api_call 字段"""
    return (
        func_name.startswith("add_")
        and func_name not in _ADD_FUNCTIONS_WITHOUT_API_CALL
    )


# ── 默认值推断 ──────────────────────────────────────────────────────


def infer_default_for_type(field_type: str) -> str:
    """根据字段类型推断合理的默认值字符串

    用于 Output 类字段和 handler 返回值中需要对缺少默认值的字段
    提供一个安全的默认值。
    """
    ft = field_type.lower()
    if "int" in ft:
        return "0"
    if "str" in ft:
        return '""'
    if "bool" in ft:
        return "False"
    if "list" in ft:
        return "[]"
    if "dict" in ft:
        return "{}"
    return "None"
