"""Declares :class:`ClientAssertionType`."""
import enum


class ClientAssertionType(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    jwt_bearer = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'