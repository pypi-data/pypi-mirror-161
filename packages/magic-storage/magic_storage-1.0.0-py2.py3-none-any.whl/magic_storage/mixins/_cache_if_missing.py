from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

from magic_storage._store_type import StoreType
from magic_storage._utils import make_uid

_R = TypeVar("_R")


class CacheIfMissingMixin(ABC):
    @abstractmethod
    def is_available(self, __uid: str, /) -> bool:
        ...

    @abstractmethod
    def load_as(  # noqa: FNE004
        self,
        store_type: StoreType,
        uid: str,
        **load_kw: Any,
    ) -> Any:
        ...

    @abstractmethod
    def store_as(
        self,
        store_type: StoreType,
        /,
        uid: str,
        item: Any,
        **dump_kw: Any,
    ) -> str:
        ...

    def cache_if_missing(
        self,
        uid: str,
        callback: Callable[[], _R],
        store_type: StoreType = StoreType.PICKLE,
    ) -> _R:
        """Store and return object if not present in cache, otherwise load from
        cache and return.

        In case of load failure object cache is recreated.

        Parameters
        ----------
        uid : str
            Object identifier used to find object in cache.
        callback : Callable[[], _R]
            Callback function which can create new object if object is not found in cache
        store_type : StoreType, optional
            Determines how object should be stored in cache, by default StoreType.PICKLE

        Returns
        -------
        _R
            Object loaded from cache OR object created with callback and stored to cache.
        """
        uid = make_uid(uid)

        if self.is_available(uid):
            logging.debug(f"'{uid}' is available and will be loaded.")
            try:
                return self.load_as(store_type, uid=uid)  # type: ignore
            except Exception as e:
                logging.exception(e)
            logging.warning(
                f"Failed to load '{uid}' due to loading error. Cache will be recreated."
            )

        else:
            logging.debug(
                f"Resource '{uid}' is NOT available thus will be created."
            )
        # If cache is not present OR if cache load failed
        item = callback()
        self.store_as(store_type, uid=uid, item=item)
        return item  # type: ignore
