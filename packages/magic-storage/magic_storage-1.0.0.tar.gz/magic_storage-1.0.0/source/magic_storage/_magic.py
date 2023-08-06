from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from .impl._filesystem import FilesystemStorage

__all__ = ["MagicStorage"]


T = TypeVar("T", bound="MagicStorage")


class MagicStorage:
    """This class instantiated and caches loaders which can be acquired with
    dedicated methods.

    Resource storages are neither guaranteed to be cached, nor to be
    always newly created.
    """

    def filesystem(self, __root: str | Path) -> FilesystemStorage:
        """Return local cache storage for current file. This object will be
        configured to use cache.

        Parameters
        ----------
        current_file : str
            Either directory or file, when file, its parent directory will be used.

        Returns
        -------
        FilesystemStorage
            new storage object.
        """
        return FilesystemStorage(__root)

    def filesystem_no_cache(self, __root: str | Path) -> FilesystemStorage:
        """Return local cache storage for current file. This object will be
        configured to not use cache.

        Parameters
        ----------
        current_file : str
            Either directory or file, when file, its parent directory will be used.

        Returns
        -------
        FilesystemStorage
            new storage object.
        """
        fs = FilesystemStorage(__root)
        fs.configure(cache=None)
        return fs
