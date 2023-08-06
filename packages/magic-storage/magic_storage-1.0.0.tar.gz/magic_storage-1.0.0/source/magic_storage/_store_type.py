from __future__ import annotations

from enum import Enum
from typing import Iterable

__all__ = ["StoreType"]


__i = iter(range(1000))

BYTES_BIT = 1 << next(__i)
TEXT_BIT = 1 << next(__i)

SUPPORT_LIST_BIT = 1 << next(__i)
SUPPORT_TUPLE_BIT = 1 << next(__i)

SUPPORT_DICT_BIT = 1 << next(__i)

SUPPORT_STR_BIT = 1 << next(__i)
SUPPORT_BYTES_BIT = 1 << next(__i)

SUPPORT_OBJECT_BIT = 1 << next(__i)

SUPPORT_IMAGE = 1 << next(__i)

SUPPORT_ANY_BIT = (
    SUPPORT_LIST_BIT
    | SUPPORT_TUPLE_BIT
    | SUPPORT_DICT_BIT
    | SUPPORT_STR_BIT
    | SUPPORT_BYTES_BIT
    | SUPPORT_OBJECT_BIT
    | SUPPORT_IMAGE
)

JSON_BIT = 1 << next(__i)
PICKLE_BIT = 1 << next(__i)


class StoreType(Enum):
    # basic storage type
    TEXT = TEXT_BIT
    BINARY = BYTES_BIT
    # complex storage type
    JSON = (
        TEXT_BIT
        | SUPPORT_LIST_BIT
        | SUPPORT_TUPLE_BIT
        | SUPPORT_DICT_BIT
        | SUPPORT_STR_BIT
        | JSON_BIT
    )
    PICKLE = BYTES_BIT | SUPPORT_ANY_BIT | PICKLE_BIT

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name}:{self.value:>08b}"

    def is_text(self) -> bool:
        return bool(self.value & TEXT_BIT)

    def is_binary(self) -> bool:  # pragma: no cover
        return bool(self.value & BYTES_BIT)

    @classmethod
    def iter_text(cls) -> Iterable[StoreType]:
        return filter(lambda e: e.is_text(), cls)

    @classmethod
    def iter_binary(cls) -> Iterable[StoreType]:  # pragma: no cover
        return filter(lambda e: e.is_binary(), cls)
