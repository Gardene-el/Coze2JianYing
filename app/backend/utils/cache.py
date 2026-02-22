from collections import OrderedDict
from typing import Dict

import pyJianYingDraft as draft

# 全局缓存：draft_id → ScriptFile（OrderedDict 末尾为最近使用）
DRAFT_CACHE: Dict[str, 'draft.ScriptFile'] = OrderedDict()
MAX_CACHE_SIZE = 50000


def update_draft_cache(key: str, value: 'draft.ScriptFile') -> None:
    """写入缓存，若容量满则淘汰最久未使用（队头）条目。"""
    if key in DRAFT_CACHE:
        DRAFT_CACHE.pop(key)
    elif len(DRAFT_CACHE) >= MAX_CACHE_SIZE:
        DRAFT_CACHE.popitem(last=False)
    DRAFT_CACHE[key] = value
