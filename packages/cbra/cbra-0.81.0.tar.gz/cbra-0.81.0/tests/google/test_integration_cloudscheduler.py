# pylint: skip-file
# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_authenticate_with_token(
    id_token: str,
    client: AsyncClient
):
    response = await client.post( # type: ignore
        url='/export',
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200