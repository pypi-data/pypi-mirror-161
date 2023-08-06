"""Declares :class:`fastapi.params.Header` instances for
common HTTP headers.
"""
import typing

import fastapi
import fastapi.params


ACCEPT: str = fastapi.Header(
    default=None,
    title="Accept",
    alias="Accept",
    description=(
        "Indicates which content types, expressed as MIME "
        "types, the client is able to understand."
    )
)

CONTENT_ENCODING_SCHEMA: dict[str, typing.Any] = {
    'description': (
        "Lists any encodings that have been applied to the representation "
        "(message payload), and in what order. This lets the recipient "
        "know how to decode the representation in order to obtain the "
        "original payload format"
    ),
    'schema': {
        'type': 'string',
        'example': 'deflate, gzip'
    }
}

CONTENT_ENCODING: str = fastapi.Header(
    default=None,
    alias="Content-Encoding",
    title="Content-Encoding",
    description=CONTENT_ENCODING_SCHEMA['description']
)

CONTENT_LENGTH_SCHEMA: dict[str, typing.Any] = {
    'description': (
        "Indicates the size of the message body, in bytes, sent to the recipient."
    ),
    'schema': {
        'type': 'number',
        'example': 1
    }
}

CONTENT_LENGTH: int = fastapi.Header(
    default=None,
    alias="Content-Length",
    title="Content-Length",
    description=CONTENT_LENGTH_SCHEMA['description']
)

CONTENT_LOCATION_SCHEMA: dict[str, typing.Any] = {
    'description': (
        "Indicates an alternate location for the returned data. "
        "The principal use is to indicate the URL of a resource "
        "transmitted as the result of content negotiation. It "
        "may also be used to indicate the location of a resource "
        "resulting from its creation."
    ),
    'schema': {
        'type': 'string',
        'example': "https://api.example.com/1"
    }
}

CONTENT_TYPE_SCHEMA: dict[str, typing.Any] = {
    'description': (
        "Used to indicate the original media type of the resource "
        "(prior to any content encoding applied for sending)."
    ),
    'schema': {
        'type': 'string',
        'example': 'application/json'
    }
}

CONTENT_TYPE: str = fastapi.Header(
    default=None,
    alias="Content-Type",
    title="Content-Type",
    description=CONTENT_TYPE_SCHEMA['description']
)


ACCEPT_LANGUAGE_SCHEMA: dict[str, typing.Any] = {
    'description': (
        "Indicates the natural language and locale that the client prefers. "
        "The server uses content negotiation to select one of the proposals "
        "and informs the client of the choice with the `Content-Language` "
        "response header."
    ),
    'schema': {
        'type': 'string',
        'example': 'fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5'
    }
}

ACCEPT_LANGUAGE: str = fastapi.Header(
    default=None,
    title="Accept-Language",
    alias="Accept-Language",
    description=ACCEPT_LANGUAGE_SCHEMA['description']
)


ACCESS_CONTROL_ALLOW_CREDENTIALS_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Tells browsers whether to expose the response to the "
        "frontend JavaScript code when the request's credentials "
        "mode (`Request.credentials`) is `include`.\n\n"
        "Credentials are cookies, authorization headers, "
        "or TLS client certificates."
    ),
    'schema': {
        'type': 'boolean',
        'example': 'false'
    }
}

ACCESS_CONTROL_ALLOW_HEADERS_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Used in response to a preflight request which includes the "
        "`Access-Control-Request-Headers` to indicate which HTTP "
        "headers can be used during the actual request."
    ),
    'schema': {
        'type': 'string',
        'example': 'X-Custom-Header, X-Another-Custom-Header'
    }
}

ACCESS_CONTROL_ALLOW_METHODS_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Specifies one or more methods allowed when accessing a "
        "resource in response to a preflight request."
    ),
    'schema': {
        'type': 'string',
        'example': 'GET, OPTIONS'
    }
}

ACCESS_CONTROL_ALLOW_ORIGIN_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Indicates whether the response can be shared "
        "with requesting code from the origin specified "
        "in the `Origin` request header."
    ),
    'schema': {
        'type': 'string',
        'example': '*'
    }
}

ACCESS_CONTROL_EXPOSE_HEADERS_SCHEMA: typing.Dict[str, typing.Any] = {
    'description': (
        "Indicate which response headers should be made available to "
        "scripts running in the browser, in response to a cross-origin "
        "request.\n\n"
        "Only the CORS-safelisted response headers are exposed by "
        "default. Additional headers are listed by this header."
    ),
    'schema': {
        'type': 'string',
        'example': 'Content-Encoding, X-Custom-Header'
    }
}

ACCESS_CONTROL_MAX_AGE_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Indicates how long the results of a preflight request "
        "(that is the information contained in the "
        "`Access-Control-Allow-Methods` and "
        "`Access-Control-Allow-Headers` headers) can be cached."
    ),
    'schema': {
        'type': 'number',
        'example': '600'
    }
}

ACCESS_CONTROL_REQUEST_HEADERS: str = fastapi.Header(
    default=None,
    alias='Access-Control-Request-Headers',
    title="Access-Control-Request-Headers",
    description=(
        "Used by browsers when issuing a preflight request to let "
        "the server know which HTTP headers the client might send "
        "when the actual request is made. The complementary "
        "server-side header of `Access-Control-Allow-Headers` will "
        "answer this browser-side header."
    )
)

ACCESS_CONTROL_REQUEST_METHOD: str = fastapi.Header(
    default=None,
    alias='Access-Control-Request-Methods',
    title="Access-Control-Request-Methods",
    description=(
        "Used by browsers when issuing a preflight request, to let "
        "the server know which HTTP method will be used when the "
        "actual request is made. This header is necessary as the "
        "preflight request is always an `OPTIONS` and doesn't use "
        "the same method as the actual request."
    )
)

CORS_HEADERS: typing.Dict[str, typing.Any] = {
    'Access-Control-Allow-Credentials': ACCESS_CONTROL_ALLOW_CREDENTIALS_SCHEMA,
    'Access-Control-Allow-Origin': ACCESS_CONTROL_ALLOW_ORIGIN_SCHEMA,
    'Access-Control-Expose-Headers': ACCESS_CONTROL_EXPOSE_HEADERS_SCHEMA
}

DIGEST_SCHEMA: typing.Dict[
    str,
    typing.Union[str, typing.Dict[str, str]]
] = {
    'description': (
        "Provides a digest of the *selected representation* of the requested "
        "resource.\n\nRepresentations are different forms of a particular "
        "resource that might be returned from a request: for example, the "
        "same resource might be formatted in a particular media type such "
        "as XML or JSON, localized to a particular written language or "
        "geographical region, and/or compressed or otherwise encoded for "
        "transmission. The *selected representation* is the actual format of "
        "a resource that is returned following content negotiation, and can "
        "be determined from the response's Representation headers.\n\n"
        "The digest applies to the whole representation of a resource, not "
        "to a particular message. It can be used to verify that the "
        "representation data has not been modified during transmission."
    ),
    'schema': {
        'type': 'string'
    }
}

ORIGIN: str | None = fastapi.Header(
    default=None,
    alias='Origin',
    title="Origin",
    description=(
        "Indicates the origin (scheme, hostname, and port) that "
        "caused the request. For example, if a user agent needs "
        "to request resources included in a page, or fetched by "
        "scripts that it executes, then the origin of the page "
        "may be included in the request."
    )
)


WANTS_DIGEST: str = fastapi.Header(
    default=None,
    title="Wants digest",
    alias="Wants-Digest",
    description=(
        "Instructs the the server to provide a digest of the "
        "requested resource using the `Digest` response header."
    ),
    example="SHA-512;q=0.3, sha-256;q=1"
)


HEADERS_RESPONSE_BODY: dict[str, typing.Any] = {
    'Content-Encoding': CONTENT_ENCODING_SCHEMA,
    'Content-Length': CONTENT_LENGTH_SCHEMA,
    'Content-Location': CONTENT_LOCATION_SCHEMA,
    'Content-Type': CONTENT_TYPE_SCHEMA,
}