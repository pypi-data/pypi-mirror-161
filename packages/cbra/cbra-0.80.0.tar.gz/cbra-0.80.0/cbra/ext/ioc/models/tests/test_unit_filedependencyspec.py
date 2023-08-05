# pylint: skip-file
import pytest

from ..filedependencyspec import FileDependencySpec


@pytest.mark.asyncio
async def test_resolve():
    spec = FileDependencySpec(
        name='ExampleDependency',
        path='VERSION'
    )
    with open(spec.path, 'rb') as f:
        assert await spec.resolve() == f.read()
