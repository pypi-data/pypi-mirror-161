# pylint: skip-file
import pytest_asyncio
from ckms.core import Keychain

from cbra import Application
from cbra.session.const import SESSION_ENCRYPTION_KEY
from cbra.session.const import SESSION_SIGNING_KEY


@pytest_asyncio.fixture(scope='session') # type: ignore
async def keychain() -> Keychain:
    keychain = Keychain()
    keychain.configure({
        SESSION_SIGNING_KEY: {
            'provider': 'local',
            'kty': 'OKP',
            'use': 'sig',
            'key': {'path': 'pki/session-signing.key'}
        },
        SESSION_ENCRYPTION_KEY: {
            'provider': 'local',
            'public_kid': SESSION_ENCRYPTION_KEY,
            'kty': 'oct',
            'algorithm': 'A256GCM',
            'use': 'enc',
            'key': {'cek': b'0' * 32},
            'key_ops': ['decrypt', 'encrypt']
        }
    })
    await keychain
    return keychain


@pytest_asyncio.fixture # type: ignore
async def app(keychain: Keychain) -> Application:
    application = Application(
        keychain=keychain
    )
    await application.on_startup()
    return application