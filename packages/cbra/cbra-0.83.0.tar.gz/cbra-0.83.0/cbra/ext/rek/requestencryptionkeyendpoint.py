# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet
from unimatrix.exceptions import ImproperlyConfigured

from cbra import Endpoint
from cbra.cors import AnonymousReadCorsPolicy
from cbra.cors import CorsPolicyType
from cbra.params import CurrentServer
from .jsonwebsignature import JSONWebSignature


class RequestEncryptionKeyEndpoint(Endpoint):
    __module__: str = 'ckms.ext.rek'
    cors_policy: type[CorsPolicyType] = AnonymousReadCorsPolicy
    kid: str
    issuer: str = CurrentServer
    method: str = 'GET'
    mount_path: str = '.well-known/request-encryption-key'
    tags: list[str] = ['Server metadata']
    response_description: str = (
        "Request Encryption Key Set (REKS) wrapped in a JSON Web Signature (JWS)"
    )
    response_model: type[JSONWebSignature] = JSONWebSignature
    response_model_exclude: list[str] = []
    summary: str = "Response Encryption Key Set (REKS)"
    ttl: int = 300
    with_options: bool = True

    @property
    def codec(self) -> PayloadCodec:
        return PayloadCodec(signing_keys=[x for x in self.signers])

    @property
    def jwks(self) -> JSONWebKeySet:
        return self.keychain\
            .tagged('request-encryption-key')\
            .as_jwks()

    @property
    def keychain(self) -> Keychain:
        return self.request.app.keychain

    @property
    def signers(self) -> Keychain:
        return self.keychain\
            .tagged('reks-signer')\
            .private() # type: ignore

    async def handle(self) -> JSONWebSignature:
        """Returns a JSON Web Key Set (JWKS) that contains the public key,
        that a client can use to encrypt the body of an HTTP request,
        wrapped in a JSON Web Signature (JWS).
        """
        if not bool(self.signers):
            raise ImproperlyConfigured(
                "No signing keys for the Request Encryption Key Set (REKS) are "
                "configured. Tag keys with the 'reks-signer' tag to make "
                "them available for signing."
            )
        return JSONWebSignature.parse_raw(
            await self.codec.encode(
                payload={
                    'iss': self.issuer,
                    'iat': self.now,
                    'nbf': self.now,
                    'exp': self.now + self.ttl,
                    'jwks': self.jwks.dict()
                },
                content_type="jwt+reks"
            )
        )