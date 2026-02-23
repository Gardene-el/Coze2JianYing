from collections import OrderedDict

import pyJianYingDraft as draft
from pyJianYingDraft.segment import BaseSegment

# 全局缓存：draft_id → ScriptFile（OrderedDict 末尾为最近使用）
DRAFT_CACHE: OrderedDict[str, draft.ScriptFile] = OrderedDict()
SEGMENT_CACHE: OrderedDict[str, BaseSegment] = OrderedDict()
MAX_CACHE_SIZE = 10000


def update_draft_cache(key: str, value: 'draft.ScriptFile') -> None:
    """写入缓存，若容量满则淘汰最久未使用（队头）条目。"""
    if key in DRAFT_CACHE:
        DRAFT_CACHE.pop(key)
    elif len(DRAFT_CACHE) >= MAX_CACHE_SIZE:
        DRAFT_CACHE.popitem(last=False)
    DRAFT_CACHE[key] = value


def update_segment_cache(key: str, value: BaseSegment) -> None:
    """写入缓存，若容量满则淘汰最久未使用（队头）条目。"""
    if key in SEGMENT_CACHE:
        SEGMENT_CACHE.pop(key)
    elif len(SEGMENT_CACHE) >= MAX_CACHE_SIZE:
        SEGMENT_CACHE.popitem(last=False)
    SEGMENT_CACHE[key] = value

