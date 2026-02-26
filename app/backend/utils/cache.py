from collections import OrderedDict
from typing import Optional, Type, TypeVar, overload

import pyJianYingDraft as draft
from pyJianYingDraft.segment import BaseSegment

from app.backend.exceptions import CustomError, CustomException

# 全局缓存：draft_id → ScriptFile（OrderedDict 末尾为最近使用）
DRAFT_CACHE: OrderedDict[str, draft.ScriptFile] = OrderedDict()
SEGMENT_CACHE: OrderedDict[str, BaseSegment] = OrderedDict()
MAX_CACHE_SIZE = 1000


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


SegT = TypeVar("SegT", bound=BaseSegment)


@overload
def get_segment_cache(key: str) -> Optional[BaseSegment]:
    ...


@overload
def get_segment_cache(key: str, segment_type: Type[SegT]) -> Optional[SegT]:
    ...


@overload
def get_segment_cache(key: str, segment_type: tuple[Type[SegT], ...]) -> Optional[SegT]:
    ...


def get_segment_cache(
    key: str,
    segment_type: Optional[Type[SegT] | tuple[Type[SegT], ...]] = None,
) -> Optional[BaseSegment] | Optional[SegT]:
    if key not in SEGMENT_CACHE:
        return None

    segment = SEGMENT_CACHE.pop(key)
    SEGMENT_CACHE[key] = segment

    if segment_type is not None and not isinstance(segment, segment_type):
        return None
    return segment


@overload
def require_segment(key: str) -> BaseSegment:
    ...


@overload
def require_segment(key: str, segment_type: Type[SegT]) -> SegT:
    ...


@overload
def require_segment(key: str, segment_type: tuple[Type[SegT], ...]) -> SegT:
    ...


def require_segment(
    key: str,
    segment_type: Optional[Type[SegT] | tuple[Type[SegT], ...]] = None,
) -> BaseSegment | SegT:
    segment = get_segment_cache(key)
    if segment is None:
        raise CustomException(CustomError.SEGMENT_NOT_FOUND)

    if segment_type is not None and not isinstance(segment, segment_type):
        expect = (
            ", ".join(seg_t.__name__ for seg_t in segment_type)
            if isinstance(segment_type, tuple)
            else segment_type.__name__
        )
        raise CustomException(CustomError.INVALID_SEGMENT_TYPE, f"expect {expect}, got {type(segment).__name__}")
    return segment

