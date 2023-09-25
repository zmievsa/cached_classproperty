import re

import pytest

from cached_classproperty import cached_classproperty, cached_staticproperty


@pytest.fixture(params=[cached_staticproperty, cached_classproperty])
def any_cached_property(request):
    return request.param


def test__cached_staticproperty__in_single_class__executes_exactly_once():
    class Foo:
        @cached_staticproperty
        def bar(times_called=[0]) -> int:
            times_called[0] += 1
            return times_called[0]

    assert Foo.bar == 1
    assert Foo().bar == 1
    assert Foo.bar == 1


def test__cached_classproperty__in_single_class__executes_exactly_once():
    class Foo:
        @cached_classproperty
        def bar(cls, times_called=[0]) -> int:
            times_called[0] += 1
            return times_called[0]

    assert Foo.bar == 1
    assert Foo().bar == 1
    assert Foo.bar == 1


def test__cached_property__defined_in_two_classes_at_once_with_different_names__should_raise_error(
    any_cached_property,
) -> None:
    @any_cached_property
    def bar(*args):
        raise NotImplementedError

    class Foo:
        foo = bar

    with pytest.raises(
        RuntimeError,
        match=re.escape(
            f"Error calling __set_name__ on '{any_cached_property.__name__}' instance 'boo' in 'Bar'"
        ),
    ):

        class Bar:
            boo = bar


def test__cached_classproperty__defined_in_two_classes_at_once_with_same_name__should_execute_once_for_each_class():
    @cached_classproperty
    def bar(cls, times_called=[0]) -> int:
        times_called[0] += 1
        return times_called[0]

    class Foo:
        foo = bar

    class Bar:
        foo = bar

    assert Foo.foo == 1
    assert Bar.foo == 2
    assert Foo.foo == 1
    assert Bar.foo == 2


def test__cached_staticproperty__defined_in_two_classes_at_once_with_same_name__should_execute_once_for_each_class():
    @cached_staticproperty
    def bar(times_called=[0]) -> int:
        times_called[0] += 1
        return times_called[0]

    class Foo:
        foo = bar

    class Bar:
        foo = bar

    assert Foo.foo == 1
    assert Bar.foo == 2
    assert Foo.foo == 1
    assert Bar.foo == 2


def test__cached_staticproperty__when_inherited__executes_exactly_once() -> None:
    class Foo:
        @cached_staticproperty
        def bar(times_called=[0]) -> int:
            times_called[0] += 1
            return times_called[0]

    class Baz(Foo):
        pass

    assert Foo.bar == 1
    assert Foo().bar == 1
    assert Foo.bar == 1

    assert Baz.bar == 1
    assert Baz().bar == 1
    assert Baz.bar == 1


def test__cached_classproperty__when_inherited__behaves_like_classmethod():
    class Superclass:
        @classmethod
        def my_classmethod(cls):
            return ("Superclass.x",)

        @cached_classproperty
        def my_cached_classproperty(cls):
            return cls.my_classmethod()

    class Subclass1(Superclass):
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Subclass1.x",
            )

    class Subclass2(Superclass):
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Subclass2.x",
            )

    class Finalclass(Subclass1, Subclass2):
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Finalclass.x",
            )

    assert Superclass.my_cached_classproperty == Superclass.my_classmethod()
    assert Subclass1.my_cached_classproperty == Subclass1.my_classmethod()
    assert Subclass2.my_cached_classproperty == Subclass2.my_classmethod()
    assert Finalclass.my_cached_classproperty == Finalclass.my_classmethod()


def test__cached_classproperty__super():
    class Superclass:
        @cached_classproperty
        def my_cached_classproperty(cls):
            return ("Superclass",)
        @classmethod
        def my_classmethod(cls):
            return ("Superclass",)


    class Subclass1(Superclass):
        @cached_classproperty
        def my_cached_classproperty(cls):
            return (
                *super().my_cached_classproperty,
                "Subclass1",
            )
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Subclass1",
            )

    class Subclass2(Superclass):
        @cached_classproperty
        def my_cached_classproperty(cls):
            return (
                *super().my_cached_classproperty,
                "Subclass2",
            )
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Subclass2",
            )

    class Finalclass(Subclass1, Subclass2):
        @cached_classproperty
        def my_cached_classproperty(cls):
            return (
                *super().my_cached_classproperty,
                "Finalclass",
            )
        @classmethod
        def my_classmethod(cls):
            return (
                *super().my_classmethod(),
                "Finalclass",
            )

    assert Superclass.my_cached_classproperty == Superclass.my_classmethod()
    assert Subclass1.my_cached_classproperty == Subclass1.my_classmethod()
    assert Finalclass.my_cached_classproperty == Finalclass.my_classmethod()
    assert Subclass2.my_cached_classproperty == Subclass2.my_classmethod()
