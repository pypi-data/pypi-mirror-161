"""Declares :class:`IContentNegotiation`."""
import typing

import fastapi

from cbra.headers import ACCEPT
from cbra.headers import DIGEST_SCHEMA
from cbra.headers import HEADERS_RESPONSE_BODY
from cbra.headers import ACCEPT_LANGUAGE
from cbra.headers import CONTENT_ENCODING
from cbra.headers import CONTENT_LENGTH
from cbra.headers import CONTENT_TYPE
from cbra.headers import WANTS_DIGEST
from .iparser import IParser
from .irenderer import IRenderer
from .iresponsedigest import IResponseDigest


class IContentNegotiation:
    accept: typing.Optional[str]
    content_type: typing.Optional[str] = None
    content_encoding: typing.Optional[str] = None
    content_length: typing.Optional[int] = None
    wants_digest: typing.Optional[str] = None
    request: fastapi.Request

    @classmethod
    def get_response_headers(cls) -> dict[str, typing.Any]:
        return {**HEADERS_RESPONSE_BODY, 'Digest': DIGEST_SCHEMA}

    @classmethod
    def has_request_body(cls) -> bool:
        raise NotImplementedError
 
    @classmethod
    def has_response_body(cls) -> bool:
        raise NotImplementedError

    @classmethod
    def with_body(
        cls,
        request: fastapi.Request,
        accept: str = ACCEPT,
        accept_language: str | None = ACCEPT_LANGUAGE,
        content_encoding: str = CONTENT_ENCODING,
        content_length: int = CONTENT_LENGTH,
        content_type: str = CONTENT_TYPE,
        wants_digest: typing.Optional[str] = WANTS_DIGEST
    ) -> 'IContentNegotiation':
        instance = cls(
            request=request,
            accept=accept,
            wants_digest=wants_digest
        )
        instance.content_encoding = content_encoding
        instance.content_length = content_length
        instance.content_type = content_type
        return instance

    def __init__(
        self,
        *,
        request: fastapi.Request,
        accept: typing.Optional[str] = ACCEPT,
        accept_language: str | None = ACCEPT_LANGUAGE,
        wants_digest: str | None = WANTS_DIGEST
    ):
        if wants_digest is not None:
            wants_digest = str.lower(wants_digest)
        self.request = request
        self.accept = accept
        self.accept_language = accept_language
        self.wants_digest = wants_digest

    def select_digest(
        self,
        algorithms: typing.List[typing.Type[IResponseDigest]],
        default: typing.Optional[typing.Type[IResponseDigest]] = None
    ) -> typing.Optional[IResponseDigest]:
        raise NotImplementedError

    def select_parser(
        self,
        parsers: typing.List[typing.Type[IParser]]
    ) -> IParser:
        raise NotImplementedError

    def select_renderer(
        self,
        renderers: typing.List[typing.Type[IRenderer]],
        format_suffix: typing.Optional[str] = None,
        default: type[IRenderer] | None = None
    ) -> IRenderer:
        """Return the list of renderers in order of precedence."""
        raise NotImplementedError