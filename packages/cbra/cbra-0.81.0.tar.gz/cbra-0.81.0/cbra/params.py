# pylint: skip-file
import typing

import aorta
import fastapi
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet

from .types import IApplication


__all__ = [
    'ApplicationJWKS',
    'CurrentHost',
    'CurrentServer',
    'ServerCodec',
    'ServerKeychain',
    'ServerPublisher',
]


def get_client_host(request: fastapi.Request) -> str:
    host = '0.0.0.0'
    if request.client:
        host = request.client.host
    return host


def get_current_application(request: fastapi.Request) -> IApplication:
    return typing.cast(IApplication, request.app)


def get_current_host(request: fastapi.Request) -> str:
    return request.url.netloc


def get_current_server(request: fastapi.Request) -> str:
    return f'{request.url.scheme}://{request.url.netloc}'


def get_publisher(request: fastapi.Request) -> aorta.MessagePublisher:
    return request.app.publisher


def get_server_codec(request: fastapi.Request) -> PayloadCodec:
    return request.app.codec


def get_server_jwks(
    request: fastapi.Request
) -> JSONWebKeySet:
    return request.app.get_jwks()


def get_server_keychain(request: fastapi.Request) -> Keychain:
    return request.app.keychain


ClientHost: str = fastapi.Depends(get_client_host)

CurrentApplication: IApplication = fastapi.Depends(get_current_application)

CurrentHost: str = fastapi.Depends(get_current_host)

CurrentServer: str = fastapi.Depends(get_current_server)

ServerPublisher: aorta.MessagePublisher = fastapi.Depends(get_publisher)

ServerCodec: PayloadCodec = fastapi.Depends(get_server_codec)

ServerKeychain: Keychain = fastapi.Depends(get_server_keychain)

ApplicationJWKS: JSONWebKeySet = fastapi.Depends(get_server_jwks)
