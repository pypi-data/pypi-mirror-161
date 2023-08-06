from __future__ import annotations

import json
import logging
import os
import tempfile
from inspect import Traceback
from pathlib import Path
from typing import Any, KeysView, Optional, Type

from filelock import FileLock

__all__ = ["AtomicFile", "IndexFile"]


class AtomicFile:
    """File like object supporting writing and reading in quasi atomic manor.

    All reading and writing is done under lock and writing is done with
    temporary files and os.replace().

    Example
    -------
    ```
    >>> tmp = getfixture("tmp_path")
    >>> with AtomicFile(tmp / "some_file.txt") as file:
    ...     file.write_text("Example content")
    ...
    >>> with AtomicFile(tmp / "some_file.txt") as file:
    ...     file.read_text()
    ...
    'Example content'
    >>>
    ```
    """

    def __init__(self, file_path: str | Path) -> None:
        file_path = Path(file_path)
        self._file = file_path.absolute()
        self._lock_file = (
            file_path.parent / f"{file_path.name}.lock"
        ).absolute()
        self._lock = FileLock(self._lock_file)

    def __enter__(self) -> AtomicFile:
        self._file.touch(0o777, True)
        logging.debug(f"Created {self._file}.")
        self._lock.acquire()
        logging.debug(f"Acquired {self._lock_file}.")
        return self

    def read_text(self, **kwargs: Any) -> str:
        """Read data from file. Requires lock to be acquired with context
        manager.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed to Path.read_text()

        Returns
        -------
        str
            data from file.
        """
        assert self._lock.is_locked
        value = self._file.read_text(**kwargs)
        logging.debug(f"Read text to {self._file}.")
        return value

    def write_text(
        self,
        content: str,
        encoding: str = "utf-8",
        errors: str = "strict",
    ) -> None:
        """Write data to file. Requires lock to be acquired with context
        manager.

        Parameters
        ----------
        content : str
            Content to be saved.
        encoding : str, optional
            Encoding to use, by default "utf-8"
        errors : str, optional
            Error mode, same rules as for open(), by default "strict"
        """
        assert self._lock.is_locked
        temp = tempfile.NamedTemporaryFile(
            mode="wt",
            delete=False,
            suffix=self._file.name,
            dir=self._file.parent,
            encoding=encoding,
            errors=errors,
        )
        temp.write(content)
        temp.flush()
        temp.close()
        os.replace(temp.name, self._file)
        logging.debug(f"Wrote text to {self._file}.")

    def read_bytes(self, **kwargs: Any) -> bytes:
        """Read data from file. Requires lock to be acquired with context
        manager.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed to Path.read_bytes()

        Returns
        -------
        str
            data from file.
        """
        assert self._lock.is_locked
        value = self._file.read_bytes(**kwargs)
        logging.debug(f"Read text to {self._file}.")
        return value

    def write_bytes(self, content: bytes) -> None:
        """Write data to file. Requires lock to be acquired with context
        manager.

        Parameters
        ----------
        content : str
            Content to be saved.
        """
        assert self._lock.is_locked
        temp = tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            suffix=self._file.name,
            dir=self._file.parent,
        )
        temp.write(content)
        temp.flush()
        temp.close()
        os.replace(temp.name, self._file)
        logging.debug(f"Wrote bytes to {self._file}.")

    def __exit__(
        self,
        _exception_type: Optional[Type[BaseException]],
        _exception_value: Optional[BaseException],
        _traceback: Traceback,
    ) -> None:
        self._lock.release()
        logging.debug(f"Released {self._lock_file}.")


class IndexFile(AtomicFile):
    def __init__(self, file_path: str | Path) -> None:
        super().__init__(file_path)
        self._index: Optional[dict[str, str]] = None

    def __enter__(self) -> IndexFile:
        super().__enter__()
        self._index = {}
        try:
            raw = self._file.read_text(encoding="utf-8")
            self._index = json.loads(raw)
        except Exception as e:
            logging.exception(e)
        return self

    @property
    def index(self) -> dict[str, str]:
        assert self._index is not None
        return self._index

    def __getitem__(self, __key: str) -> str:
        assert self._index is not None
        return self._index[__key]

    def get(self, __key: str, __default: str) -> str:
        assert self._index is not None
        return self._index.get(__key, __default)

    def __setitem__(self, __key: str, __value: str) -> None:
        assert self._index is not None
        self._index[__key] = __value

    def __delitem__(self, __key: str) -> None:
        assert self._index is not None
        del self._index[__key]

    def keys(self) -> KeysView:
        assert self._index is not None
        return self._index.keys()

    def __contains__(self, __key: str) -> bool:
        assert self._index is not None
        return __key in self._index

    def __exit__(
        self,
        _exception_type: Optional[Type[BaseException]],
        _exception_value: Optional[BaseException],
        _traceback: Traceback,
    ) -> None:
        try:
            self.write_text(json.dumps(self._index), encoding="utf-8")
        finally:
            self._index = None
            super().__exit__(_exception_type, _exception_value, _traceback)
