import importlib.metadata
from _thread import RLock  # type: ignore
from typing import TYPE_CHECKING, Optional

__version__ = importlib.metadata.version("cached_classproperty")

from weakref import WeakKeyDictionary

_NOT_FOUND = object()

if TYPE_CHECKING:
    from typing import Any, Callable, ParamSpec, TypeVar

    from typing_extensions import Concatenate

    T = TypeVar("T")
    P = ParamSpec("P")

    def cached_staticproperty(
        func: Callable[Concatenate[P], T], attrname: Optional[str] = None
    ) -> T:
        ...

    def cached_classproperty(
        func: Callable[Concatenate[Any, P], T], attrname: Optional[str] = None
    ) -> T:
        ...

else:

    class cached_staticproperty:
        __slots__ = ("func", "attrname", "lock")

        def __init__(self, func, attrname: Optional[str] = None):
            self.func = func
            self.attrname = attrname
            self.lock = RLock()

        def __set_name__(self, owner, name):
            # Note that this is called at the creation of the class that has cached_staticproperty in its body
            # but it is not called during inheritance.
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_staticproperty to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

        def __get__(self, instance, owner=None):
            if owner is None:
                raise TypeError(
                    "Cannot use cached_staticproperty without an owner class."
                )
            if self.attrname is None:
                raise TypeError(
                    "Cannot use cached_staticproperty instance without calling __set_name__ on it."
                )
            # Classes always have __dict__ and metaclasses cannot define __slots__
            # https://utcc.utoronto.ca/~cks/space/blog/python/HowSlotsWorkI
            cache = owner.__dict__
            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND or val is self:
                with self.lock:
                    # check if another thread filled cache while we awaited lock
                    val = cache.get(self.attrname, _NOT_FOUND)
                    if val is _NOT_FOUND or val is self:
                        val = self.func()
                        setattr(owner, self.attrname, val)
            return val

    class cached_classproperty:
        __slots__ = ("func", "attrname", "lock", "owner", "_cached_value", "_weak_dict")

        def __init__(self, func, attrname: Optional[str] = None):
            self.func = func
            self.attrname = attrname
            self.lock = RLock()
            self.owner = None
            self._cached_value = _NOT_FOUND
            self._weak_dict = WeakKeyDictionary()

        def __set_name__(self, owner, name):
            # Note that this is called at the creation of the class that has cached_staticproperty in its body
            # but it is not called during inheritance.
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_classproperty to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

            # Store the owner class to enable fast path
            self.owner = owner

        def __get__(self, instance, owner=None):
            if owner is None:
                raise TypeError(
                    "Cannot use cached_classproperty without an owner class."
                )
            if self.owner is owner:
                # Fast path: use self._cached_value to take advantage of __slots__
                val = self._cached_value
                if val is _NOT_FOUND:
                    with self.lock:
                        # check if another thread filled cache while we awaited lock
                        val = self._cached_value
                        if val is _NOT_FOUND:
                            val = self.func(owner)
                            self._cached_value = val
            else:
                # Slow path: use self._weak_dict to avoid memory leaks
                val = self._weak_dict.get(owner, _NOT_FOUND)
                if val is _NOT_FOUND:
                    with self.lock:
                        # check if another thread filled cache while we awaited lock
                        val = self._weak_dict.get(owner, _NOT_FOUND)
                        if val is _NOT_FOUND:
                            val = self.func(owner)
                            self._weak_dict[owner] = val
            return val
