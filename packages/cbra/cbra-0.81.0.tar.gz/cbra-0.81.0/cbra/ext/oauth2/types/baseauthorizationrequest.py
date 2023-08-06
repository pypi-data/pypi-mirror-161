"""Declares :class:`AuthorizationRequest`."""
import dataclasses
import functools
import json
import os
import secrets
import typing

import fastapi
import fastapi.params
import pydantic
from fastapi.params import Query
from pydantic.fields import FieldInfo

from cbra.types import JSONQueryParameter
from .iprincipal import IPrincipal
from .redirecturl import RedirectURL
from .responsetype import ResponseType


class BaseAuthorizationRequest:
    client_id: str
    response_type: ResponseType
    redirect_uri: str | None
    scope: str | None
    state: str | None
    response_mode: str | None
    resource: str | None
    nonce: str | None
    display: str | None
    prompt: str | None
    max_age: int | None
    ui_locales: str | None
    claims_locales: str | None
    id_token_hint: str | None
    login_hint: str | None
    acr_values: str | None
    registration: str | None
    claims: JSONQueryParameter

    @staticmethod
    def get_fields(
        field_factory: typing.Callable[..., FieldInfo | Query],
        private_field: typing.Callable[..., dataclasses.Field[typing.Any] | pydantic.BaseModel],
        exclude: list[str] | None = None
    ) -> dict[str, typing.Any]:
        """Return the authorization request parameters."""
        exclude = exclude or []
        annotations = {
            'client_id': str,
            'response_type': ResponseType,
            'redirect_uri': str | None,
            'scope': str | None,
            'state': str | None,
            'response_mode': str | None,
            'resource': str | None,
            'nonce': str | None,
            'display': str | None,
            'prompt': str | None,
            'max_age': int | None,
            'ui_locales': str | None,
            'claims_locales': str | None,
            'id_token_hint': str | None,
            'login_hint': str | None,
            'acr_values': str | None,
            'registration': str | None,
            'claims': JSONQueryParameter,
            'request_uri': str,
            'request': str
        }
        fields = {
            'client_id': field_factory(
                default=None,
                title="Client identifier",
                description="Identifies the client that is requesting authorization."
            ),
            'response_type': field_factory(
                default=None,
                title="Response type",
                description=(
                    "Informs the authorization server of the desired grant type"
                ),
                example="code",
                enum=[
                    "code",
                    "code id_token",
                    "code id_token token",
                    "code token",
                    "id_token",
                    "id_token token",
                    "none",
                    "token"
                ]
            ),
            'redirect_uri': field_factory(
                default=None,
                title="Redirect URI",
                description=(
                    "The URL to redirect the client to after completing the "
                    "flow. Must be an absolute URI that is served over https.\n\n"
                    "If `redirect_uri` is omitted, the default redirect URI for "
                    "the client specified by `client_id` is used. For clients that "
                    "do not have a redirect URI specified, this produces an error "
                    "state."
                )
            ),
            'scope': field_factory(
                default=None,
                title="Scope",
                description=(
                    "A space-delimited list specifying the requested access scope."
                ),
                example="hello.world"
            ),
            'state': field_factory(
                default=None,
                title="State",
                description=(
                    "An opaque value used by the client to maintain state between "
                    "the request and callback. The authorization server includes "
                    "this value when redirecting the user-agent back to the client."
                ),
                example=bytes.hex(os.urandom(8))
            ),
            'response_mode': field_factory(
                default=None,
                title="Response mode",
                enum=["query", "fragment"],
                description=(
                    "Informs the authorization server of the mechanism to be used "
                    "for returning authorization response parameters."
                ),
                example="query"
            ),
            'resource': field_factory(
                alias='resource',
                default=None,
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
            ),
            'nonce': field_factory(
                default=None,
                title="Nonce",
                description=(
                    "String value used to associate a Client session with an ID "
                    "Token, and to mitigate replay attacks. The value is passed "
                    "through unmodified from the Authentication Request to the "
                    "ID Token. Sufficient entropy MUST be present in the `nonce` "
                    "values used to prevent attackers from guessing values."
                ),
                example=bytes.hex(os.urandom(4))
            ),
            'display': field_factory(
                default=None,
                title="Display",
                description=(
                    "ASCII string value that specifies how the Authorization Server "
                    "displays the authentication and consent user interface pages "
                    "to the End-User. The defined values are:\n\n"
                    "- `page` - The Authorization Server SHOULD display the "
                    "authentication and consent UI consistent with a full User "
                    "Agent page view. If the display parameter is not specified, "
                    "this is the default display mode.\n"
                    "- `popup` - The Authorization Server SHOULD display the "
                    "authentication and consent UI consistent with a popup User "
                    "Agent window. The popup User Agent window should be of an "
                    "appropriate size for a login-focused dialog and should not "
                    "obscure the entire window that it is popping up over.\n"
                    "- `touch` - The Authorization Server SHOULD display the "
                    "authentication and consent UI consistent with a device "
                    "that leverages a touch interface.\n"
                    "- `wap` - The Authorization Server SHOULD display the "
                    "authentication and consent UI consistent with a \"feature "
                    "phone\" type display.\n\n"
                    "If there is no `display` parameter provided, then an attempt "
                    "is made to detect the agent based on the request headers."
                ),
                example="page"
            ),
            'prompt': field_factory(
                default=None,
                title="Prompt",
                description=(
                    "Space delimited, case sensitive list of ASCII string values "
                    "that specifies whether the Authorization Server prompts the "
                    "End-User for reauthentication and consent. The defined values "
                    "are:\n"
                    "\n- `none` - The Authorization Server does not display any "
                    "authentication or consent user interface pages. An error is "
                    "returned if an End-User is not already authenticated or the "
                    "Client does not have pre-configured consent for the requested "
                    "Claims or does not fulfill other conditions for processing "
                    "the request. The error code will typically be `login_required`, "
                    "`interaction_required`, or another code defined in Section "
                    "3.1.2.6 of the OpenID Connect Core 1.0 specification. This "
                    "can be used as a method to check for existing authentication "
                    "and/or consent."
                    "\n- `login` - The Authorization Server prompts the End-User "
                    "for reauthentication. If it cannot reauthenticate the End-User, "
                    "it returns an error, typically `login_required`."
                    "\n- `consent` - The Authorization Server prompts the End-User "
                    "for consent before returning information to the Client. If it "
                    "cannot obtain consent, it returns an error, typically "
                    "`consent_required`."
                    "\n- `select_account` - The Authorization Server prompts "
                    "the End-User to select a user account. This enables an "
                    "End-User who has multiple accounts at the Authorization Server "
                    "to select amongst the multiple accounts that they might have "
                    "current sessions for. If it cannot obtain an account selection "
                    "choice made by the End-User, it return an error, typically "
                    "`account_selection_required`."
                ),
                example="prompt"
            ),
            'max_age': field_factory(
                default=None,
                title="Maximum authentication age",
                description=(
                    "Maximum Authentication Age. Specifies the allowable elapsed time in "
                    "seconds since the last time the End-User was actively authenticated. "
                    "If `max_age` is expired, then the client must re-authenticate."
                )
            ),
            'ui_locales': field_factory(
                default=None,
                title="Preferred locales",
                description=(
                    "End-User's preferred languages and scripts for the user interface, "
                    "represented as a space-separated list of BCP47 language tag values, "
                    "ordered by preference."
                ),
                example="nl-NL be"
            ),
            'claims_locales': field_factory(
                default=None,
                title="Preferred locales for claims",
                description=(
                    "End-User's preferred languages and scripts for returned Claims, "
                    "represented as a space-separated list of BCP47 language tag values, "
                    "ordered by preference."
                ),
                example="nl-NL be"
            ),
            'id_token_hint': field_factory(
                default=None,
                title="ID Token hint",
                description=(
                    "Token previously issued by the Authorization Server being passed as "
                    "a hint about the End-User's current or past authenticated session with "
                    "the Client. If the End-User identified by the ID Token is logged in "
                    "or is logged in by the request, then the Authorization Server returns "
                    "a positive response; otherwise, it return an error, such as "
                    "`login_required`. When possible, an `id_token_hint` should be present "
                    "when `prompt=none` is used and an `invalid_request` error is returned "
                    "if it is not; however, the server attempts to respond successfully "
                    "when possible, even if it is not present. The Authorization Server "
                    "need not be listed as an audience of the ID Token when it is used "
                    "as an `id_token_hint` value."
                )
            ),
            'login_hint': field_factory(
                default=None,
                title="Login hint",
                description=(
                    "Hint to the Authorization Server about the login identifier the End-User "
                    "might use to log in (if necessary). This hint can be used by an RP if it "
                    "first asks the End-User for their e-mail address (or other identifier) "
                    "and then wants to pass that value as a hint to the discovered "
                    "authorization service. It is recommended that the hint value match the "
                    "value used for discovery. This value may also be a phone number in the "
                    "format specified for the `phone_number` Claim."
                ),
                example="hello@unimatrixone.io"
            ),
            'acr_values': field_factory(
                default=None,
                title="ACR values",
                description=(
                    "Requested **Authentication Context Class Reference** values. Space-separated "
                    "string that specifies the `acr` values that the Authorization Server is "
                    "being requested to use for processing this Authentication Request, with the "
                    "values appearing in order of preference. The **Authentication Context Class** "
                    "satisfied by the authentication performed is returned as the `acr` Claim Value. "
                    "The `acr` Claim is requested as a *Voluntary Claim* by this parameter."
                )
            ),
            'registration': field_factory(
                default=None,
                title="Registration",
                description=(
                    "This parameter is used by the Client to provide information about itself to a "
                    "Self-Issued OP that would normally be provided to an OP during Dynamic Client "
                    "Registration. The value is a JSON object containing Client metadata values, as "
                    "defined in Section 2.1 of the OpenID Connect Dynamic Client Registration 1.0 "
                    "specification. The registration parameter must not be used when the OP is not "
                    "a Self-Issued OP."
                )
            ),
            'claims': field_factory(
                default='{}',
                title="Claims",
                description=(
                    "This parameter is used to request that specific Claims be returned. The value is "
                    "a JSON object listing the requested Claims.\n\n"
                    "The claims Authentication Request parameter requests that specific Claims be "
                    "returned from the UserInfo Endpoint and/or in the ID Token. It is represented "
                    "as a JSON object containing lists of Claims being requested from these "
                    "locations. Properties of the Claims being requested MAY also be specified.\n\n"
                    "The claims parameter value is represented in an OAuth 2.0 request as UTF-8 "
                    "encoded JSON (which ends up being form-urlencoded when passed as an OAuth "
                    "parameter). When used in a **Request Object** value, the JSON is used as "
                    "the value of the `claims` member.\n\n"
                    "The top-level members of the Claims request JSON object are:\n\n"
                    "- `userinfo` - (Optional) Requests that the listed individual Claims be "
                    "returned from the UserInfo Endpoint. If present, the listed Claims are "
                    "being requested to be added to any Claims that are being requested using "
                    "scope values. If not present, the Claims being requested from the UserInfo "
                    "Endpoint are only those requested using `scope` values."
                    "\n- `id_token` - (Optional) Requests that the listed individual Claims be "
                    "returned in the ID Token. If present, the listed Claims are being requested "
                    "to be added to the default Claims in the ID Token. If not present, the default "
                    "ID Token Claims are requested.\n\n"
                    "Other members may be present. Any members used that are not understood "
                    "must be ignored."
                )
            ),
            'request': field_factory(
                default=None,
                title="Request",
                description=(
                    "A JSON Web Token (JWT) whose JWT Claims Set holds the "
                    "JSON-encoded OAuth 2.0 authorization request parameters. "
                    "Must not be used in combination with the `request_uri` "
                    "parameter, and all other parameters except `client_id` "
                    "must be absent.\n\n"
                    "Confidential and credentialed clients must first sign "
                    "the claims using their private key, and then encrypt the "
                    "result with the public keys that are provided by the "
                    "authorization server through the `jwks_uri` specified "
                    "in its metadata.\n\n"
                    "A non-standard extension used by this authorization server "
                    "is the ability for public clients to use the `request` "
                    "parameter. In that case, the JWT must be encrypted using "
                    "the method described above, and not signed as a public "
                    "client does not have a key."
                )
            ),
            'request_uri':  field_factory(
                default=None,
                title="Request URI",
                description=(
                    "References a Pushed Authorization Request (PAR) or a remote "
                    "object containing the authorization request.\n\n"
                    "If the authorization request was pushed to this authorization "
                    "server, then the format of the `request_uri` parameter is "
                    "`urn:ietf:params:oauth:request_uri:<reference-value>`. "
                    "Otherwise, it is an URI using the `https` scheme. If the "
                    "`request_uri` parameter is a remote object, then the external "
                    "domain must have been priorly whitelisted by the client."
                )
            )
        }
        for name in exclude:
            if name in fields:
                del fields[name]
            if name in annotations:
                del annotations[name]
        return {
            **fields,
            '__annotations__': annotations
        }

    @classmethod
    def create_model(
        cls,
        location: str,
        exclude: list[str] | None = None
    ) -> type['BaseAuthorizationRequest']:
        """Create a new :class:`BaseAuthorizationRequest` implementation
        configured with the given field type.
        """
        bases: list[typing.Any] = [cls]
        Field = fastapi.Query
        PrivateField = functools.partial(dataclasses.field, init=False)
        if location == 'body':
            Field = pydantic.Field
            PrivateField = pydantic.PrivateAttr
            bases.insert(0, pydantic.BaseModel)
        new_class = type(
            cls.__name__,
            tuple(bases),
            cls.get_fields(
                field_factory=Field,
                private_field=PrivateField,
                exclude=exclude
            )
        )
        if location == 'query':
            new_class = dataclasses.dataclass(new_class)
        return new_class

    @classmethod
    def body(
        cls,
        exclude: list[str] | None = None
    ) -> type['BaseAuthorizationRequest']:
        return cls.create_model('body', exclude=exclude or [])

    @classmethod
    def query(cls) -> type['BaseAuthorizationRequest']:
        return cls.create_model('query')

    @staticmethod
    def space_separated(
        value: str | set[str] | None,
        ordered: bool = False
    ) -> set[str] | list[str]:
        if isinstance(value, (set, list)):
            return value
        if value is None:
            return set()
        values = [x.strip() for x in str.split(value, ' ')]
        if not ordered:
            values = set(values)
        return values

    @property
    def authorization_code(self) -> str | None:
        return self._authorization_code

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if self.needs_authorization_code(): # type: ignore
            self._authorization_code = secrets.token_urlsafe(24)

    def get_acr_values(self) -> set[str]:
        return typing.cast(set[str], self.space_separated(self.acr_values))

    def get_claims(self) -> dict[str, typing.Any]:
        return json.loads(self.claims)

    def get_claims_locales(self) -> list[str]:
        return typing.cast(list[str], self.space_separated(self.claims_locales, True))

    def get_redirect_url(self) -> RedirectURL:
        return RedirectURL.validate(self.redirect_uri)

    def get_resources(self) -> set[str]:
        return typing.cast(set[str], self.space_separated(self.resource))

    def get_scope(self) -> set[str]:
        return typing.cast(set[str], self.space_separated(self.scope))

    def get_principal(self) -> IPrincipal | None:
        """Return the principal specified by the request parameters. For
        requests to the authorization endpoint, this method always returns
        ``None``.
        """
        return None

    def get_ui_locales(self) -> list[str]:
        return typing.cast(list[str], self.space_separated(self.ui_locales, True))

    def is_external(self) -> bool:
        """If the request is a reference, return a boolean indicating if the
        request is made available at an external source.
        """
        return False

    def is_reference(self) -> bool:
        """Return a boolean indicating if the authorization request is a
        reference.
        """
        return False

    class Config:
        check_fields = False
        exclude_defaults = True