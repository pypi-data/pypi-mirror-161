"""Declares :class:`DefaultContentNegotiation`."""
import itertools
import typing

from cbra.parsers import NullParser
from cbra.types import IContentNegotiation
from cbra.types import IParser
from cbra.types import IRenderer
from cbra.types import IResponseDigest
from ..exceptions import InvalidHeaderValue
from ..exceptions import MissingContentTypeHeader
from ..exceptions import MediaTypeNotAcceptable
from ..exceptions import UnsupportedMediaType
from ..exceptions import UnsupportedDigestAlgorithm
from ..utils import media_type_matches # type: ignore
from ..utils.mediatypes import order_by_precedence # type: ignore


class DefaultContentNegotiation(IContentNegotiation):
    __module__: str = 'cbra.negotiation'

    @classmethod
    def has_response_body(cls) -> bool:
        return True

    def select_digest(
        self,
        algorithms: typing.List[typing.Type[IResponseDigest]],
        default: typing.Optional[typing.Type[IResponseDigest]] = None
    ) -> typing.Optional[IResponseDigest]:
        # Use a default digest if the Wants-Digest header was not
        # provided by the client.
        if not self.wants_digest:
            digest = None
            if default is not None:
                digest = default()
            return digest

        digest_class = None
        available = {x.algorithm_name for x in algorithms}
        requested = self.get_digest_list()
        if not bool(available & set(requested)):
            raise UnsupportedDigestAlgorithm(available)
        for name, cls in itertools.product(requested, algorithms): 
            if cls.algorithm_name != name:
                continue
            digest_class = cls
            break

        assert digest_class is not None # nosec
        return digest_class()

    def select_parser(
        self,
        parsers: typing.List[typing.Type[IParser]]
    ) -> IParser:
        """Given a list of parsers and a media type, return the appropriate
        parser to handle the incoming request.
        """
        if self.request.method not in {"POST", "PUT", "PATCH"}\
        or not self.content_type:
            return NullParser()

        for parser in parsers:
            if media_type_matches(parser.media_type, self.content_type or ''):
                break
        else:
            if not self.content_type:
                raise MissingContentTypeHeader.fromparsers(parsers)
            raise UnsupportedMediaType.fromparsers(parsers)
        return parser(encoding=self.content_encoding)

    def select_renderer(
        self,
        renderers: typing.List[typing.Type[IRenderer]],
        format_suffix: typing.Optional[str] = None,
        default: typing.Type[IRenderer] | None = None
    ) -> IRenderer:
        """Return the list of renderers in order of precedence."""
        renderer = media_type = None
        accepts = self.get_accept_list()
        for media_types in accepts:
            for renderer, media_type in itertools.product(renderers, media_types):
                if not media_type_matches(renderer.media_type, media_type):
                    continue
                #if renderer.exact and not str.startswith(media_type, renderer.media_type):
                #    continue
                break
            else:
                renderer = None
        if not renderer:
            if (default is None) and accepts:
                raise MediaTypeNotAcceptable
            renderer = default
            media_type = renderer.media_type # type: ignore
        assert media_type is not None # nosec
        assert renderer is not None # nosec
        assert issubclass(renderer, IRenderer) # nosec
        return renderer(media_type)

    def get_accept_list(self) -> typing.List[str]:
        """Given the incoming request, return a tokenized list of media
        type strings.
        """
        if self.accept is None:
            return []
        return order_by_precedence(
            [str.strip(t) for t in str.split(self.accept, ',')]
        )

    def get_digest_list(self) -> typing.List[str]:
        """Given the incoming request, return a tokenized list of
        digest algorithms that the client requests.
        """
        if self.wants_digest is None:
            return []
        algorithms: typing.List[typing.Tuple[str, float]] = []
        for alg in [str.strip(t) for t in str.split(self.wants_digest, ',')]:
            name = quality = None
            try:
                if ';' in alg:
                    name, quality = [str.strip(x) for x in str.split(alg, ';')]
                    _, quality = [str.strip(x) for x in str.split(quality, '=')]
                else:
                    name = alg
                algorithms.append((name, float(quality or 0.0)))
            except ValueError:
                raise InvalidHeaderValue(
                    name='Wants-Digest',
                    value=alg
                )
        return [x[0] for x in sorted(algorithms, key=lambda a: -a[1])]
