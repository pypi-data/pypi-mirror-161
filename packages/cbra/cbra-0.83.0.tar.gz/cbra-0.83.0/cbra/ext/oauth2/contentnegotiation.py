"""Declares :class:`ContentNegotiation`."""
import ckms.jose
import fastapi

import cbra
from cbra.headers import ACCEPT
#from cbra.headers import CONTENT_ENCODING
#from cbra.headers import CONTENT_LENGTH
from cbra.headers import CONTENT_TYPE
from cbra.headers import WANTS_DIGEST
from cbra.negotiation import DefaultContentNegotiation
from .params import ClientRepository
from .params import LocalIssuer
from .params import ServerCodec
from .types import IClientRepository


class ContentNegotiation(DefaultContentNegotiation):
    __module__: str = 'cbra.ext.oauth2'
    clients: IClientRepository
    codec: ckms.jose.PayloadCodec
    issuer: str

    @classmethod
    def with_body( # type: ignore
        cls,
        request: fastapi.Request,
        accept: str = ACCEPT,
        #content_encoding: str = CONTENT_ENCODING,
        #content_length: int = CONTENT_LENGTH,
        content_type: str = CONTENT_TYPE,
        wants_digest: str | None = WANTS_DIGEST,
        clients: IClientRepository = ClientRepository,
        codec: ckms.jose.PayloadCodec = ServerCodec,
        issuer: str = LocalIssuer
    ) -> cbra.types.IContentNegotiation:
        instance = cls(
            request=request,
            accept=accept,
            wants_digest=wants_digest
        )
        #instance.content_encoding = content_encoding
        #instance.content_length = content_length
        instance.content_type = content_type
        instance.clients = clients
        instance.codec = codec
        instance.issuer = issuer
        return instance

    def select_parser(
        self, parsers: list[type[cbra.types.IParser]]
    ) -> cbra.types.IParser:
        parser = super().select_parser(parsers)
        parser.server_codec = self.codec # type: ignore
        parser.clients = self.clients # type: ignore
        parser.issuer = self.issuer # type: ignore
        return parser