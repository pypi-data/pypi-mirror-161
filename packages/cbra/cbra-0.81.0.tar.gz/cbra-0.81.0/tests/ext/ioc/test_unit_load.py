# pylint: skip-file
import pytest

from .. import __init__ as ioc
from ..models import DependencyList


@pytest.mark.asyncio
async def test_load(provider, package_name, symbol):
    dependencies = DependencyList(
        items=[
            {
                'spec': {
                    'type': 'file',
                    'name': 'ExampleDependency',
                    'path': 'VERSION'
                }
            },
            {
                'spec': {
                    'type': 'symbol',
                    'name': "SymbolDependency",
                    'qualname': f"{package_name}.conftest.SYMBOL"
                }
            },
        ]
    )

    await provider.load_many(dependencies)
    assert provider.is_satisfied('ExampleDependency')
    assert provider.is_satisfied('SymbolDependency')
    assert provider.resolve('SymbolDependency') == symbol
