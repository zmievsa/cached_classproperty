# cached_classproperty

cached_property for class properties instead of instance properties

---

<p align="center">
<a href="https://github.com/zmievsa/cached_classproperty/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/zmievsa/cached_classproperty/actions/workflows/test.yaml/badge.svg?branch=main&event=push" alt="Test">
</a>
<a href="https://codecov.io/gh/ovsyanka83/cached_classproperty" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/ovsyanka83/cached_classproperty?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/cached_classproperty/" target="_blank">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/cached_classproperty?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/cached_classproperty/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/cached_classproperty?color=%2334D058" alt="Supported Python versions">
</a>
</p>

## Installation

```bash
pip install cached_classproperty
```

## Usage

Similarly to `functools.cached_property`, these properties get executed exactly once on access.

```python
from cached_classproperty import cached_staticproperty, cached_classproperty

class Foo:
    @cached_staticproperty
    def my_staticproperty():
        ...

    @cached_classproperty
    def my_classproperty(cls):
        ...
```

`cached_classproperty` can be inherited and can re-execute for every inherited class just like `cached_property`. `cached_staticproperty`, on the other hand, executes exactly once even if inherited. It is also lighter and faster than `cached_classproperty`.
