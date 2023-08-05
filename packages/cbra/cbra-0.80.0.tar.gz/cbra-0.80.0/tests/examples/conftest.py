# pylint: skip-file
import httpx
import pytest_asyncio


@pytest_asyncio.fixture
async def client(app):
    params = {
        'base_url': "https://cbra.unimatrixone.localhost",
        'app': app
    }
    async with httpx.AsyncClient(**params) as client:
        yield client