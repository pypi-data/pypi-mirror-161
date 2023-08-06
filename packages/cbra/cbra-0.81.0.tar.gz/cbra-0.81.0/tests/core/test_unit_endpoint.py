# pylint: skip-file
# type: ignore
from cbra import Endpoint


def test_create_sets_attribute():
    cls = Endpoint.new(foo=1)
    assert hasattr(cls, 'foo')
    assert cls.foo == 1


def test_create_overrides_attribute():
    cls = Endpoint.new(principal=1)
    assert cls.principal == 1
