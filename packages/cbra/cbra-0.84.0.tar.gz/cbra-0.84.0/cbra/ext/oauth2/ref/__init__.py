# pylint: skip-file
"""
.. _ref-oauth2-reference-server

==================================
OAuth 2.0 reference implementation
==================================
"""
import collections
import pathlib
from typing import Any

from ckms.core import Keychain

from .. import types
from ..authorizationserver import AuthorizationServer
from ..configfileclientrepository import ConfigFileClientRepository
from ..memorystorage import MemoryStorage
from ..staticsubjectepository import StaticSubjectRepository
from ..tokenissuer import TokenIssuer
from . import clients
from . import keys
from . import subject


__all__ = [
    'DEFAULT_ENCRYPTION_KEY',
    'DEFAULT_SIGNING_KEY',
    'alice',
    'bob',
    'clients',
    'keys',
    'keychain',
    'subject'
]

CLIENTS_DIR = pathlib.Path(__file__).parent.joinpath('etc/clients')

DEFAULT_ENCRYPTION_KEY = 'enc'

DEFAULT_SIGNING_KEY = 'sig'

alice = subject.Subject(
    sub="alice@example.unimatrixone.io",
    client_scope=collections.defaultdict(set, {
        'jwt': {"read", "write", 'openid', 'profile'}
    }),
    keys=[keys.alice]
)

bob = subject.Subject(
    sub="bob@example.unimatrixone.io",
    client_scope=collections.defaultdict(set, {
        'jwt': {"read", "write", "openid", "profile"},
        'confidential': {"read"}
    }),
    keys=[keys.bob]
)

trudy = subject.Subject(
    sub="trudy@example.unimatrixone.io",
    client_scope=collections.defaultdict(set, {
        'jwt': {"read", "write", "openid", "profile"},
        'confidential': {"read"}
    }),
    keys=[keys.trudy]
)

keychain: Keychain = Keychain()
keychain.configure({
    DEFAULT_ENCRYPTION_KEY: {
        'provider': 'local',
        'kty': "OKP",
        'alg': "EdDSA",
        'crv': 'Ed448',
        'tags': ['oauth2'],
        'use': 'enc',
    },
    DEFAULT_SIGNING_KEY: {
        'provider': 'local',
        'kty': "OKP",
        'alg': "EdDSA",
        'crv': 'Ed448',
        'tags': ['oauth2'],
        'use': 'sig',
    },
})

external_keychain: Keychain = Keychain()
external_keychain.configure({
    DEFAULT_ENCRYPTION_KEY: {
        'provider': 'local',
        'kty': "OKP",
        'crv': 'Ed448',
        'tags': ['oauth2'],
        'use': 'enc',
    },
    DEFAULT_SIGNING_KEY: {
        'provider': 'local',
        'kty': "OKP",
        'crv': 'Ed448',
        'tags': ['oauth2'],
        'use': 'sig',
    },
})

ClientRepository: type[types.IClientRepository] = ConfigFileClientRepository.new(
    base_path=CLIENTS_DIR
)

SubjectRepository: type[types.ISubjectRepository] = StaticSubjectRepository.new(
    model=subject.Subject,
    subjects={
        bob.sub: bob.dict(),
        alice.sub: alice.dict(),
        trudy.sub: trudy.dict()
    }
)


def get_oauth2_server(**kwargs: Any) -> AuthorizationServer:
    kwargs.setdefault('clients', ClientRepository)
    kwargs.setdefault('issuer', TokenIssuer)
    kwargs.setdefault('storage', MemoryStorage)
    kwargs.setdefault('subjects', SubjectRepository)
    return AuthorizationServer(**kwargs)