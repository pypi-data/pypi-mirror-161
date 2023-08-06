# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet


class Request(fastapi.Request):

    @property
    def codec(self) -> PayloadCodec:
        """The :class:`~ckms.jose.PayloadCodec` instance used to
        decode JOSE objects.
        """
        return self.app.codec

    @property
    def keychain(self) -> Keychain:
        """The :class:`~ckms.core.Keychain` instance holding the
        signing and decryption keys used by the application.
        """
        return self.app.keychain

    @property
    def jwks(self) -> JSONWebKeySet:
        """A :class:`~ckms.types.JSONWebKeySet` holding the public keys intended
        for external consumers.
        """
        return self.keychain.tagged('unimatrixone.io/public-keys').as_jwks()