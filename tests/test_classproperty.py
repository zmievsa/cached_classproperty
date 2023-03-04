from cached_classproperty import cached_classproperty


def test_cached_classproperty():
    class Foo:
        @cached_classproperty
        def bar(cls, times_called=[0]):
            times_called[0] += 1
            return times_called[0]

    assert Foo.bar == 1
    assert Foo.bar == 1
    assert Foo.bar == 1
