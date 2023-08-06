# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from ckms.core import Keychain
from ckms.core.models import JSONWebSignature

import cbra
from cbra.parsers import IParser
from cbra.parsers import JWTParser
from cbra.ext.jwks import JWKSEndpoint
from cbra.ext.rek import RequestEncryptionKeyEndpoint


KEYCHAIN: dict[str, Any] = {
    'request-encryption-key': {
        'provider': 'local',
        'kty': 'RSA',
        'algorithm': 'RSA-OAEP-256',
        'key': {'path': 'pki/rsa-enc.key'},
        'tags': ['request-encryption-key']
    },
    'reks-signer-1': {
        'provider': 'local',
        'kty': 'OKP',
        'curve': 'Ed25519',
        'key': {'path': 'pki/ed25519.key'},
        'tags': ['reks-signer', 'unimatrixone.io/public-keys']
    },
    'reks-signer-2': {
        'provider': 'local',
        'kty': 'EC',
        'use': 'sig',
        'key': {'path': 'pki/p384.key'},
        'tags': ['reks-signer', 'unimatrixone.io/public-keys']
    },
}

keychain: Keychain = Keychain()
keychain.configure(KEYCHAIN)


class EncryptedBodyEndpoint(cbra.Endpoint):
    method: str = 'POST'
    parsers: list[type[IParser]] = [
        JWTParser
    ]

    async def handle( # type: ignore
        self,
        jws: JSONWebSignature
    ) -> dict[str, Any]:
        jwt = jws.claims({"jwt"})
        return jwt.dict()


def get_asgi_application() -> cbra.Application:
    app: cbra.Application = cbra.Application(keychain=keychain)
    app.add(RequestEncryptionKeyEndpoint)
    app.add(EncryptedBodyEndpoint, base_path='/')
    app.add(JWKSEndpoint, base_path='/')
    return app


app = get_asgi_application()


if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)