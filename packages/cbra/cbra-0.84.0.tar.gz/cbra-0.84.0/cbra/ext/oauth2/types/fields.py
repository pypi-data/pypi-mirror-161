"""Declares common fields used in OAuth 2.0."""
import typing

import pydantic


def ResourceField():
    return pydantic.Field(
        alias='resource',
        default=set(),
        title="Resource",
        description=(
            "Indicates the target service or resource to which access is "
            "being requested.  Its value MUST be an absolute URI, as "
            "specified by Section 4.3 of RFC 3986.  The URI MUST NOT "
            "include a fragment component. It SHOULD NOT include a query "
            "component, but it is recognized that there are cases that "
            "make a query component a useful and necessary part of the "
            "resource parameter, such as when one or more query parameters "
            "are used to scope requests to an application.  The `resource` "
            "parameter URI value is an identifier representing the identity "
            "of the resource, which MAY be a locator that corresponds to a "
            "network-addressable location where the target resource is "
            "hosted.  Multiple `resource` parameters MAY be used to indicate "
            "that the requested token is intended to be used at multiple "
            "resources."
        ),
        example="https://hello.unimatrixapis.com"
    )


def GrantTypeField(
    cls: typing.Callable[..., typing.Any] = pydantic.Field,
    default: typing.Any =...
) -> typing.Any:
    return cls(
        default=default,
        title="Grant type",
        description=(
            "Specifies the grant type that is requested by the client."
        ),
        example="authorization_code"
    )