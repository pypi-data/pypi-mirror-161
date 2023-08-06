# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest
import pytest_asyncio
from ckms.core import Keychain
from ckms.jose import PayloadCodec

from cbra import Application
from examples import rek


@pytest_asyncio.fixture(scope='session') # type: ignore
async def app() -> Application:
    app = rek.get_asgi_application()
    await app.on_startup()
    return app


@pytest.fixture
def keychain() -> Keychain:
    return rek.keychain


@pytest.fixture
def codec(keychain: Keychain) -> PayloadCodec:
    verifier = keychain.tagged('reks-signer')
    return PayloadCodec(verifier=verifier)

@pytest.fixture
def reks_url() -> str:
    return '/.well-known/request-encryption-key'