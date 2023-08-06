# pylint: skip-file
import typing

import fastapi
import pytest
import pytest_asyncio
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKey
from httpx import AsyncClient

import cbra
import cbra.auth
from cbra.ext.oauth2 import ref
from cbra.ext.oauth2 import AuthorizationEndpoint
from cbra.ext.oauth2 import AuthorizationServer
from cbra.ext.oauth2 import ConfigFileClientRepository
from cbra.ext.oauth2 import MemoryStorage
from cbra.ext.oauth2 import MemorySubjectRepository
from cbra.ext.oauth2 import RFC9068Principal
from cbra.ext.oauth2.types import IPrincipal
from cbra.ext.oauth2.types import ISubject
from cbra.ext.oauth2.types import ISubjectRepository


base_url: str = "https://cbra-oauth2.localhost"


@pytest.fixture
def alice() -> ISubject:
    return ref.subject.Subject(sub="alice@example.unimatrixone.io")


@pytest.fixture
def bob() -> ISubject:
    return ref.subject.Subject(sub="bob@example.unimatrixone.io")


@pytest.fixture
def trudy() -> ISubject:
    """An intruder."""
    return ref.subject.Subject(sub="trudy@example.unimatrixone.io")


@pytest.fixture
def current_subject(bob: ISubject) -> ISubject:
    return bob


@pytest.fixture
def users(alice: ISubject, bob: ISubject) -> dict[str, ISubject]:
    return {
        typing.cast(str, alice.sub): alice,
        typing.cast(str, bob.sub): bob
    }


@pytest_asyncio.fixture # type: ignore
async def keys() -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    return {
        ref.DEFAULT_ENCRYPTION_KEY: {
            'provider': 'local',
            'kty': "OKP",
            'alg': 'EdDSA',
            'crv': 'Ed448',
            'use': 'sig',
            'tags': ['oauth2', 'server']
        },
        ref.DEFAULT_SIGNING_KEY: {
            'provider': 'local',
            'kty': "OKP",
            'alg': 'EdDSA',
            'crv': 'Ed448',
            'use': 'sig',
            'tags': ['oauth2', 'server']
        },
    }


@pytest.fixture
def keychain(keys: dict[str, typing.Any]) -> Keychain:
    keychain = Keychain()
    keychain.configure(keys)
    return keychain


@pytest_asyncio.fixture # type: ignore
async def codec(current_subject: ISubject) -> PayloadCodec:
    return await get_subject_codec(current_subject)


@pytest.fixture
def subjects(
    users: typing.Dict[str, ISubject]
) -> typing.Generator[typing.Type[ISubjectRepository], None, None]:
    MemorySubjectRepository.configure(users)
    yield MemorySubjectRepository
    MemorySubjectRepository.clear()


@pytest.fixture
def handlers():
    return [handle_rfc9068_token]


@pytest.fixture
def server(
    keys: typing.Dict[str, typing.Dict[str, typing.Any]],
    subjects: typing.Type[ISubjectRepository]
) -> AuthorizationServer:
    server = AuthorizationServer(
        authorize=AuthorizationEndpoint.new(
        ),
        storage=MemoryStorage,
        clients=ConfigFileClientRepository,
        grant_types={
            "authorization_code",
            "client_credentials",
            "urn:ietf:params:oauth:grant-type:jwt-bearer"
        },
        signing_key=ref.DEFAULT_SIGNING_KEY,
        subjects=subjects,
        principal_factory=cbra.auth.DebugPrincipal
    )
    return server


@pytest.fixture
def server_codec(server: AuthorizationServer):
    return PayloadCodec(
        decrypter=server.keychain,
        signer=server.keychain
    )


@pytest_asyncio.fixture # type: ignore
async def client(app: cbra.Application):
    params = {
        'app': app,
        'base_url': base_url
    }
    async with AsyncClient(**params) as client:
        yield client


async def handle_rfc9068_token(
    principal: IPrincipal = fastapi.Depends(RFC9068Principal())
):
    assert principal.has_scope("read")
    return {"message": "Hello world!"}


async def get_subject_codec(subject: ISubject) -> PayloadCodec:
    keychain = Keychain()
    keychain.configure({
        'sig': {
            'provider': 'local',
            'kty': 'OKP',
            'alg': 'EdDSA',
            'use': 'sig',
            'crv': 'Ed25519'
        }
    })
    await keychain
    private = keychain.get('sig')
    jwk = private.as_jwk(private=False)
    subject.register_public_key(jwk)
    # TODO: End hack

    return PayloadCodec(signer=keychain)