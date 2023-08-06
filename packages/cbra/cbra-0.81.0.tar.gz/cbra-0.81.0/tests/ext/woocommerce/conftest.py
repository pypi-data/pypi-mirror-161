# pylint: skip-file
# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from cbra import Application
from examples.woocommerce import get_asgi_application


@pytest_asyncio.fixture # type: ignore
async def app() -> Application:
    app = get_asgi_application()
    await app.on_startup()
    return app


@pytest_asyncio.fixture # type: ignore
async def client(
    app: Application,
    base_url: str
) -> AsyncGenerator[AsyncClient, None]:
    params = {
        'app': app,
        'base_url': base_url
    }
    async with AsyncClient(**params) as client:
        yield client