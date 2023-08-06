# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import aorta
import fastapi
import pytest
from httpx import AsyncClient


class FooCommand(aorta.Command):
    foo: str


class BarCommand(aorta.Command):
    bar: str


class BazCommand(aorta.Command):
    baz: str


class TazCommand(aorta.Command):
    taz: str


class ErrorCommand(aorta.Command):
    foo: str


class FooBarCommandHandler(aorta.CommandHandler):

    async def handle( # type: ignore
        self,
        command: FooCommand | BarCommand
    ) -> None:
        pass


class TazCommandHander(aorta.CommandHandler):

    async def handle(
        self,
        command: TazCommand
    ) -> None:
        raise Exception


class ErrorCommandHandler(aorta.CommandHandler):

    def __init__(self, foo: str = fastapi.Path(...)):
        self.path = foo

    async def handle(self, command: ErrorCommand):
        pass


aorta.register(FooBarCommandHandler)
aorta.register(TazCommandHander)
aorta.register(ErrorCommandHandler)

@pytest.mark.asyncio
async def test_authenticate_with_token(
    id_token: str,
    client: AsyncClient
):
    command = FooCommand(foo='Hello world!')
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
                'data': command.serialize()
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200
    assert not(response.text)


@pytest.mark.asyncio
async def test_failing_handler_returns_ok(
    id_token: str,
    client: AsyncClient
):
    command = TazCommand(taz='Hello world!')
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
                'data': command.serialize()
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200, response.status_code
    assert not(response.text)
    assert 'X-Error-Code' in response.headers, response.headers


@pytest.mark.asyncio
async def test_unknown_object_type_sets_header(
    id_token: str,
    client: AsyncClient
):
    command = BazCommand(baz='Hello world!')
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
                'data': command.serialize()
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200
    assert not(response.text)
    assert response.headers.get('Content-Length') in {'0', None}
    assert response.headers.get('X-Error-Code') == "UNKNOWN_MESSAGE_TYPE"


@pytest.mark.asyncio
async def test_malformed_object_type_sets_header(
    id_token: str,
    client: AsyncClient
):
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
                'data': 'foo'
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200
    assert not(response.text)
    assert response.headers.get('Content-Length') in {'0', None}
    assert response.headers.get('X-Error-Code') == "MALFORMED_OBJECT"


@pytest.mark.asyncio
async def test_malformed_message_returns_no_body(
    id_token: str,
    client: AsyncClient
):
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200
    assert not(response.text)
    assert response.headers.get('Content-Length') in {'0', None}


@pytest.mark.asyncio
async def test_improperly_configured_handler_is_suppressed(
    id_token: str,
    client: AsyncClient
):
    command = ErrorCommand(foo='Hello world!')
    response = await client.post( # type: ignore
        url='/aorta',
        json={
            'subscription': 'projects/foobar/subscriptions/baztaz',
            'message': {
                'messageId': "id",
                'publishTime': "2014-10-02T15:01:23.045123456Z",
                'data': command.serialize()
            }
        },
        headers={'Authorization': f'Bearer {id_token}'}
    )
    assert response.status_code == 200
    assert not(response.text)
    assert response.headers.get('Content-Length') in {'0', None}