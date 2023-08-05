# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets

import pytest

from cbra import Application


@pytest.fixture
def app():
    return Application()


def random_key_name() -> str:
    return f'key-{secrets.token_hex(4)}'


@pytest.mark.asyncio
async def test_add_encryption_key(app: Application):
    name = random_key_name()
    await app.add_encryption_key(name, {
        'provider': 'local',
        'kty': 'OKP',
        'crv': 'Ed448'
    })
    meta = app.keychain.get(name)
    assert meta.use == 'enc'


@pytest.mark.asyncio
async def test_add_encryption_key_with_tags(app: Application):
    name = random_key_name()
    await app.add_encryption_key(name, {
        'provider': 'local',
        'kty': 'OKP',
        'crv': 'Ed448',
        'tags': ['foo']
    })
    meta = app.keychain.get(name)
    assert meta.use == 'enc'
    assert meta.tags == {'foo'}


@pytest.mark.asyncio
async def test_add_signing_key(app: Application):
    name = random_key_name()
    await app.add_signing_key(name, {
        'provider': 'local',
        'kty': 'OKP',
        'crv': 'Ed448'
    })
    meta = app.keychain.get(name)
    assert meta.use == 'sig'


@pytest.mark.asyncio
async def test_add_signing_key_with_tags(app: Application):
    name = random_key_name()
    await app.add_signing_key(name, {
        'provider': 'local',
        'kty': 'OKP',
        'crv': 'Ed448',
        'tags': ['foo']
    })
    meta = app.keychain.get(name)
    assert meta.use == 'sig'
    assert meta.tags == {'foo'}