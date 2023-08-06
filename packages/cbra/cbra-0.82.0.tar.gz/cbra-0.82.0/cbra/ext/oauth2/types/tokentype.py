"""Declares :class:`TokenType`."""
import enum


class TokenType(str, enum.Enum):
    access_token = "urn:ietf:params:oauth:token-type:access_token"
    refresh_token = "urn:ietf:params:oauth:token-type:refresh_token"
    id_token = "urn:ietf:params:oauth:token-type:id_token"
    saml1 = "urn:ietf:params:oauth:token-type:saml1"
    saml2 = "urn:ietf:params:oauth:token-type:saml2"
    jwt = "urn:ietf:params:oauth:token-type:jwt"