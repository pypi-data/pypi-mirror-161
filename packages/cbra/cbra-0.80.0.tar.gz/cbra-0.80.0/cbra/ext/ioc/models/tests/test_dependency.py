# pylint: skip-file
import pytest

from ..dependency import Dependency


@pytest.mark.asyncio
async def test_polymorphic_symbol(symbol, package_name):
    spec = Dependency(
        spec={
            'type': 'symbol',
            'name': "SymbolDependency",
            'qualname': f"{package_name}.conftest.SYMBOL"
        }
    )
    assert await spec.resolve() == symbol


@pytest.mark.asyncio
async def test_polymorphic_file():
    spec = Dependency(
        spec={
            'type': 'file',
            'name': 'ExampleDependency',
            'path': 'VERSION'
        }
    )
    with open('VERSION', 'rb') as f:
        assert await spec.resolve() == f.read()
