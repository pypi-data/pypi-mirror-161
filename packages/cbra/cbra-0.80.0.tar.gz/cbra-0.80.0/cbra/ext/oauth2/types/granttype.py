"""Declares :class:`GrantType`."""
import enum


__all__ = [
    'GrantType',
    'AssertedGrantType'
]


class GrantType(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    authorization_code = "authorization_code"
    client_credentials = "client_credentials"
    refresh_token = "refresh_token"
    jwt_bearer = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    saml_bearer = "urn:ietf:params:oauth:grant-type:saml2-bearer"


class AssertedGrantType(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    jwt_bearer = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    saml_bearer = "urn:ietf:params:oauth:grant-type:saml2-bearer"