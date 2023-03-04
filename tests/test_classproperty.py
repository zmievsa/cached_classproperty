from cached_classproperty import cached_classproperty


def test_cached_classproperty():
    class A:
        @cached_classproperty
        def foo(cls, times_called=[0]):
            times_called[0] += 1
            return times_called[0]

    assert A.foo == 1
    assert A.foo == 1
    assert A.foo == 1
