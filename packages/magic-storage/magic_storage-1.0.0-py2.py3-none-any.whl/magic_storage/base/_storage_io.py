from __future__ import annotations

from ._reader import ReaderBase
from ._writer import WriterBase

__all__ = ["StorageIOBase"]


class StorageIOBase(ReaderBase, WriterBase):
    def configure(self) -> None:
        """Configure resource storage access."""
