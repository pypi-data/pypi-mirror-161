"""Declares :class:`Options`."""
import typing

import fastapi

from cbra.exceptions import EXCEPTION_RESPONSES
from cbra.headers import ACCESS_CONTROL_ALLOW_CREDENTIALS_SCHEMA
from cbra.headers import ACCESS_CONTROL_ALLOW_HEADERS_SCHEMA
from cbra.headers import ACCESS_CONTROL_ALLOW_METHODS_SCHEMA
from cbra.headers import ACCESS_CONTROL_ALLOW_ORIGIN_SCHEMA
from cbra.headers import ACCESS_CONTROL_MAX_AGE_SCHEMA
from cbra.negotiation import NullResponseContentNegotiation
from cbra.responses import OptionsResponse
from cbra.types import IContentNegotiation
from cbra.types import IRenderer
from cbra.utils import classproperty
from .endpoint import Endpoint


class Options(Endpoint):
    __module__: str = 'cbra'
    allowed_methods: typing.Set[str] = set()
    description: str = (
        "Responds with the permitted communication options for a given "
        "URL or server. A client can specify a URL with this method, or "
        "an asterisk (*) to refer to the entire server. The response may "
        "include the following headers:\n\n"
        "- The `Allow` header, that indicates the allowed HTTP methods, "
        "separated by a comma.\n"
        "\n"
        "**Preflighted requests in CORS**\n\n"
        "In CORS, a preflight request is sent with the OPTIONS method so "
        "that the server can respond if it is acceptable to send the "
        "request. Permissions can be requested using HTTP headers for "
        "the following parameters:\n\n"
        "- The `Access-Control-Request-Method` header sent in a preflight "
        "request tells the server that when the actual request is sent, "
        "it will have the method specified as the header value.\n"
        "- The `Access-Control-Request-Headers` header tells the server "
        "that when the actual request is sent, it include the given headers. "
        "Multiple headers are separated by a comma.\n\n"
        "Depending on the server policy, it may respond with the following "
        "response headers:\n\n"
        "- The `Access-Control-Allow-Credentials` tells browsers whether to "
        "expose the response to the frontend JavaScript code when the request's "
        "credentials mode (`Request.credentials`) is `include`.\n"
        "- The `Access-Control-Request-Headers` to indicate which HTTP headers "
        "can be used during the actual request.\n"
        "- The `Access-Control-Allow-Methods` response header specifies one or "
        "more request methods allowed.\n"
        "- The `Access-Control-Allow-Origin` response header indicates whether "
        "the response can be shared with requesting code from the given origin."
    )
    document: bool = True
    method: str = "OPTIONS"
    negotiation: type[IContentNegotiation] = NullResponseContentNegotiation
    renderers: list[type[IRenderer]] = []
    responses: dict[int | str, typing.Any] = {
        500: EXCEPTION_RESPONSES[500]
    }
    response_class: type[OptionsResponse] = OptionsResponse

    @classproperty
    def default_response(cls) -> typing.Dict[str, typing.Any]:
        return {
            'description': "Endpoint allowed methods and CORS privileges.",
            'headers': {
                'Access-Control-Allow-Credentials': ACCESS_CONTROL_ALLOW_CREDENTIALS_SCHEMA,
                'Access-Control-Allow-Headers': ACCESS_CONTROL_ALLOW_HEADERS_SCHEMA,
                'Access-Control-Allow-Methods': ACCESS_CONTROL_ALLOW_METHODS_SCHEMA,
                'Access-Control-Allow-Origin': ACCESS_CONTROL_ALLOW_ORIGIN_SCHEMA,
                'Access-Control-Max-Age': ACCESS_CONTROL_MAX_AGE_SCHEMA
            }
        }

    async def handle(self) -> fastapi.Response:
        response = fastapi.Response()
        response.headers['Allow'] = str.join(', ', sorted(set(self.allowed_methods)|{"OPTIONS"}))\
            or "OPTIONS"
        return response
