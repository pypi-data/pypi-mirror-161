# pylint: skip-file
import asyncio
import functools

import fastapi
import pytest
import pytest_asyncio
from fastapi.concurrency import AsyncExitStack
from httpx import AsyncClient
from ioc.provider import Provider as DependencyContainer
from unimatrix.ext.kms import Keychain

import cbra


TEST_HMAC_KEY: str = '8a983a3d5282c751feadbdd1ad23398f882f65046df4b0ac5a96c93a50669ff7'

TEST_DEPENDENCY = "Foo"


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope='session')
async def keychain():
    keychain = Keychain()
    await keychain.register('hmac', [f"literal+hmac:{TEST_HMAC_KEY}?keyid=hmac"])
    await keychain.register('rsa', ['file+pem:pki/rsa.key'])
    await keychain.register('p256', ['file+pem:pki/p256.key'])
    await keychain.register('p384', ['file+pem:pki/p384.key'])
    await keychain.register('p521', ['file+pem:pki/p521.key'])

    return keychain


@pytest_asyncio.fixture
async def run_dependant(app):
    runner = cbra.DependantRunner()
    async with AsyncExitStack() as stack:
        request = fastapi.Request(
            scope={
                'app': app,
                'type': "http",
                'query_string': '',
                'headers': [
                    (b'host', b'foo.bar.baz')
                ],
                'fastapi_astack': stack
            }
        )
        yield functools.partial(runner.run_dependant, request)


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def container():
    return DependencyContainer()


@pytest.fixture
def test_dependency():
    return TEST_DEPENDENCY
