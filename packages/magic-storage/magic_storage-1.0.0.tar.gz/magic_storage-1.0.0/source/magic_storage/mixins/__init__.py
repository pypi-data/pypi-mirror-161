from ._cache_if_missing import CacheIfMissingMixin

__all__ = ["FullyFeaturedMixin", "CacheIfMissingMixin"]


class FullyFeaturedMixin(CacheIfMissingMixin):
    """Mixin class which aggregates all mixins from magic_storage.mixins
    submodule."""
