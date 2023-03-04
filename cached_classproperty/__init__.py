import importlib.metadata
from _thread import RLock  # type: ignore
from typing import TYPE_CHECKING

__version__ = importlib.metadata.version("cached_classproperty")

from functools import cached_property

_NOT_FOUND = object()

if TYPE_CHECKING:
    from typing import Any, Callable, ParamSpec, TypeVar

    from typing_extensions import Concatenate

    T = TypeVar("T")
    P = ParamSpec("P")

    def cached_classproperty(func: Callable[Concatenate[Any, P], T], attrname: str | None = None) -> T:
        ...

else:

    class cached_classproperty(cached_property):
        __slots__ = ("func", "attrname", "__doc__", "lock")

        def __init__(self, func, attrname: str | None = None):
            self.func = func
            self.attrname = attrname
            self.__doc__ = func.__doc__
            self.lock = RLock()

        def __set_name__(self, owner, name):
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

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
