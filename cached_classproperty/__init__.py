import importlib.metadata
from typing import TYPE_CHECKING

__version__ = importlib.metadata.version("cached_classproperty")

from functools import cached_property

_NOT_FOUND = object()

if TYPE_CHECKING:
    from typing import Any, Callable, ParamSpec, TypeVar

    from typing_extensions import Concatenate

    T = TypeVar("T")
    P = ParamSpec("P")

    def cached_classproperty(func: Callable[Concatenate[Any, P], T]) -> T:
        ...

else:

    class cached_classproperty(cached_property):
        def __get__(self, instance, owner=None):
            if owner is None:
                raise TypeError("Cannot use cached_classproperty without an owner class.")
            if self.attrname is None:
                raise TypeError("Cannot use cached_classproperty instance without calling __set_name__ on it.")
            try:
                cache = owner.__dict__
            except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
                msg = f"No '__dict__' attribute on {owner.__name__!r} " f"to cache {self.attrname!r} property."
                raise TypeError(msg) from None
            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND or val is self:
                with self.lock:  # type: ignore
                    # check if another thread filled cache while we awaited lock
                    val = cache.get(self.attrname, _NOT_FOUND)
                    if val is _NOT_FOUND or val is self:
                        val = self.func(owner)
                        setattr(owner, self.attrname, val)
            return val
