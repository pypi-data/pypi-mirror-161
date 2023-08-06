from __future__ import annotations

from magic_storage.base import StorageIOBase
from magic_storage.mixins import FullyFeaturedMixin


class InMemoryStorage(StorageIOBase, FullyFeaturedMixin):

    """Implementation of storage class which operates only in RAM and thus will
    be lost after garbage collection.

    However it is much faster than any other cache type.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__storage: dict[str, str | bytes] = {}

    def _is_available(self, uid: str) -> bool:
        return uid in self.__storage

    def _read_text(self, uid: str) -> str:
        value = self.__storage[uid]
        assert isinstance(value, str)

        return value

    def _read_bytes(self, uid: str) -> bytes:
        value = self.__storage[uid]
        assert isinstance(value, bytes)

        return value

    def _write_text(self, uid: str, item: str) -> None:
        self.__storage[uid] = item

    def _write_bytes(self, uid: str, item: bytes) -> None:
        self.__storage[uid] = item
