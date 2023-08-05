# pylint: skip-file
import asyncio

import pytest
import pytest_asyncio
import ckms.core
from ckms.types import IKeySpecification


@pytest.fixture(scope='session')
def base_url() -> str:
    return "https://cbra.localhost"


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


@pytest_asyncio.fixture(scope='session') # type: ignore
async def jose_client_signer() -> IKeySpecification:
    return await ckms.core.parse_spec({
        'provider': 'local',
        'kty': 'oct',
        'algorithm': 'HS256',
        'key': {'length': 32}
    })