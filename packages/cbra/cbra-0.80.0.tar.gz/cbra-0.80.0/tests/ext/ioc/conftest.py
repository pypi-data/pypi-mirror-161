# pylint: skip-file
import pytest

from .provider import Provider


SYMBOL = "Hello world!"


@pytest.fixture
def symbol():
    return SYMBOL


@pytest.fixture
def package_name():
    return str.replace(__name__, '.conftest', '')


@pytest.fixture
def provider():
    return Provider()
