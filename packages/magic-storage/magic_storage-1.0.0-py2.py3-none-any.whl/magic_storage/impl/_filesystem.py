from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from unittest.mock import sentinel

from cachetools import Cache, RRCache, cachedmethod

from magic_storage._atomic_file import AtomicFile
from magic_storage._utils import make_uid
from magic_storage.base import StorageIOBase
from magic_storage.mixins import FullyFeaturedMixin

__all__ = ["FilesystemStorage"]


class FilesystemStorage(StorageIOBase, FullyFeaturedMixin):
    """Implementation of storage class which operates on filesystem items to
    preserve saved items between sessions. Loading procedures can optionally
    use caching, they do by default, therefore without disabling it you can't
    rely on loads being always instantly up to date with stores.

    Encoding used to read text files, as well as cache can be changed
    using .configure() method.

    Parameters
    ----------
    __root : str | Path
        root dir for fs storage, if __root points to file, parent directory of
        this file will be used.
    subdir : Optional[str], optional
        nested directory to use for file storage, when None, data will be stored
        directly in __root, by default "data". When __root is file, subdirectory
        in __root parent directory will be used.

    Example
    -------
    ```
    >>> tmp = getfixture('tmp_path')
    >>> from magic_storage import StoreType
    >>> fs = FilesystemStorage(tmp)
    >>> example_item = {"foo": 32}
    >>> UID = "EXAMPLE UID"
    >>> fs.store_as(StoreType.JSON, uid=UID, item=example_item)
    '4c9e95de851b875493ba6c6dfb16b6aaae5c3e167aef9ab6edfeb0dbca2f6574'
    >>> fs.is_available(UID)
    True
    >>> fs.load_as(StoreType.JSON, uid=UID)
    {'foo': 32}
    >>>
    ```
    """

    def __init__(
        self, __root: str | Path, *, subdir: Optional[str] = "data"
    ) -> None:

        # store details about location in filesystem
        __root = Path(__root)
        # when __file__ is used, replace it with parent dir
        if __root.is_file():
            __root = __root.parent
        if subdir is not None:
            self._data_dir = __root / subdir
        else:
            self._data_dir = __root
        self._data_dir.mkdir(0o777, True, True)

        self._cache: Optional[RRCache] = RRCache(maxsize=128)
        self._encoding = "utf-8"
        super().__init__()

    def _filepath(self, __uid: str) -> Path:
        __uid = make_uid(__uid)
        assert isinstance(__uid, str)

        return self._data_dir / __uid

    def _get_cache(self) -> Optional[Cache]:
        return self._cache

    def _is_available(self, __uid: str) -> bool:
        fname = self._filepath(__uid)
        return fname.exists() and fname.is_file()

    @cachedmethod(_get_cache)
    def _read_text(self, uid: str) -> str:
        with AtomicFile(self._filepath(uid)) as file:
            return file.read_text(encoding=self._encoding)

    @cachedmethod(_get_cache)
    def _read_bytes(self, uid: str) -> bytes:
        with AtomicFile(self._filepath(uid)) as file:
            return file.read_bytes()

    def _write_text(self, uid: str, item: str) -> None:
        with AtomicFile(self._filepath(uid)) as file:
            file.write_text(item, encoding=self._encoding)

    def _write_bytes(self, uid: str, item: bytes) -> None:
        with AtomicFile(self._filepath(uid)) as file:
            file.write_bytes(item)

    def configure(
        self,
        *,
        encoding: str | sentinel = sentinel,
        cache: Optional[Cache] | sentinel = sentinel,
    ) -> None:
        """Configure FileStorage instance.

        Parameters
        ----------
        encoding : str | sentinel, optional
            Change encoding used to read/write text, when sentinel, old value is kept, by default "utf-8"
        cache : Optional[Cache] | sentinel, optional
            Change cache instance used for caching, set to None to disable caching, when sentinel, old value is kept, by default RRCache(maxsize=128)
        """
        if encoding is not sentinel:
            self._encoding = encoding
            logging.debug(f"Changed encoding of FileStorage to {encoding}.")

        if cache is not sentinel:
            self._cache = cache  # type: ignore
            logging.debug(f"Changed cache of FileStorage to {cache}.")
