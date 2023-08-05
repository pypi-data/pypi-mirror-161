# pylint: skip-file
import pytest

from ..symboldependencyspec import SymbolDependencySpec


@pytest.mark.asyncio
async def test_resolve_builtin():
    spec = SymbolDependencySpec(
        name='ExampleDependency',
        qualname='int'
    )
    assert await spec.resolve() == int


@pytest.mark.asyncio
async def test_resolve_symbol(symbol, package_name):
    spec = SymbolDependencySpec(
        name='ExampleDependency',
        qualname=f'{package_name}.conftest.SYMBOL'
    )
    assert await spec.resolve() == symbol
