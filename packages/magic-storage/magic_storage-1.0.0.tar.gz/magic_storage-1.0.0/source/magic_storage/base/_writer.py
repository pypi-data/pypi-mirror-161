from __future__ import annotations

import json
import logging
import pickle
from abc import ABC, abstractmethod
from typing import Any, Callable

from magic_storage._store_type import StoreType
from magic_storage._utils import compress, make_uid

__all__ = ["WriterBase"]


class WriterBase(ABC):
    def store_as(
        self,
        store_type: StoreType,
        /,
        uid: str,
        item: Any,
        **dump_kw: Any,
    ) -> str:
        """Dump object to cache in format selected by parameter store_as.

        Parameters
        ----------
        store_type : StoreType
            store type from enum
        uid : str
            object unique identifier.
        item : Any
            item to store, constraints depend on storage type.

        Returns
        -------
        str
            Identifier after cleanup and tagging (real used identifier).
        """
        return self._store_as(store_type, uid=uid, item=item, **dump_kw)

    def _store_as(
        self,
        store_type: StoreType,
        /,
        *,
        uid: str,
        item: Any,
        **dump_kw: Any,
    ) -> str:
        uid = make_uid(uid)
        assert isinstance(uid, str), uid
        logging.debug(f"Dumping '{uid}' as {store_type}.")

        retval = self._STORE_MAP[store_type](self, uid, item, **dump_kw)
        assert retval is None, retval

        logging.debug(f"Successfully dumped {uid} as {store_type}")
        return uid

    def _store_text(self, uid: str, item: Any, **str_kw: Any) -> None:
        raw_value = str(item, **str_kw)
        assert isinstance(raw_value, str), raw_value

        retval = self._write_text(uid, raw_value)
        assert retval is None, retval

        return retval

    @abstractmethod
    def _write_text(self, __uid: str, __item: str, /) -> None:
        ...

    def _store_json(self, uid: str, item: Any, **json_dumps_kw: Any) -> None:
        try:
            raw_value = json.dumps(item, **json_dumps_kw)
        except TypeError:
            if hasattr(item, "json") and callable(item.json):
                raw_value = json.dumps(item.json(), **json_dumps_kw)
            else:
                raise
        assert isinstance(raw_value, str), raw_value

        retval = self._write_text(uid, raw_value)
        assert retval is None, retval

        return retval

    def _store_bytes(self, uid: str, item: Any, **bytes_kw: Any) -> None:
        raw_value = bytes(item, **bytes_kw)
        assert isinstance(raw_value, bytes), raw_value

        retval = self._write_bytes(uid, raw_value)
        assert retval is None, retval

        logging.debug(f"Successfully dumped {uid} as BYTES")
        return retval

    @abstractmethod
    def _write_bytes(self, __uid: str, __item: bytes, /) -> None:
        ...

    def _store_pickle(
        self, uid: str, item: Any, **pickle_dump_kw: Any
    ) -> None:
        raw_value = pickle.dumps(item, **pickle_dump_kw)
        assert isinstance(raw_value, bytes)

        raw_value = compress(raw_value)
        assert isinstance(raw_value, bytes), raw_value

        retval = self._write_bytes(uid, raw_value)
        assert retval is None, retval

        logging.debug(f"Successfully dumped {uid} as PICKLE")
        return retval

    def store_str(self, uid: str, item: str, **str_kw: Any) -> str:
        """Dump object to cache in form of text.

        Parameters
        ----------
        uid : str
            object unique identifier.
        item : str
            item to store, str or str-like objects.

        Returns
        -------
        str
            Identifier after cleanup and tagging (real used identifier).
        """
        return self._store_as(StoreType.TEXT, uid=uid, item=item, **str_kw)

    def store_bytes(self, uid: str, item: bytes, **bytes_kw: Any) -> str:
        """Dump object to cache in form of binary.

        Parameters
        ----------
        uid : str
            object unique identifier.
        item : str
            item to store, bytes or bytes-like objects.

        Returns
        -------
        str
            Identifier after cleanup and tagging (real used identifier).
        """
        return self._store_as(StoreType.BINARY, uid=uid, item=item, **bytes_kw)

    def store_json(self, uid: str, item: Any, **json_dumps_kw: Any) -> str:
        """Dump object to cache in form of json encoded text.

        Parameters
        ----------
        uid : str
            object unique identifier.
        item : str
            item to store, any object which can be encoded with json.dumps().

        Returns
        -------
        str
            Identifier after cleanup and tagging (real used identifier).
        """
        return self._store_as(
            StoreType.JSON, uid=uid, item=item, **json_dumps_kw
        )

    def store_pickle(self, uid: str, item: Any, **pickle_dump_kw: Any) -> str:
        """Dump object to cache in form of pickled binary.

        Because pickle is a binary format, it is always compressed with lzma algorithm.

        Parameters
        ----------
        identifier : str
            object unique identifier.
        item : str
            item to store, any object which can be encoded with pickle.dumps().


        Returns
        -------
        str
            Identifier after cleanup and tagging (real used identifier).
        """
        return self._store_as(
            StoreType.PICKLE, uid=uid, item=item, **pickle_dump_kw
        )

    _STORE_MAP: dict[StoreType, Callable[[WriterBase, str, Any], None]] = {
        StoreType.TEXT: _store_text,
        StoreType.BINARY: _store_bytes,
        StoreType.JSON: _store_json,
        StoreType.PICKLE: _store_pickle,
    }
