from ._atomic_file import AtomicFile
from ._magic import MagicStorage
from ._store_type import StoreType
from .impl import InMemoryStorage
from .impl._filesystem import FilesystemStorage

__all__ = [
    "MagicStorage",
    "StoreType",
    "FilesystemStorage",
    "InMemoryStorage",
    "AtomicFile",
]

__version__: str = "1.0.0"
