"""Declares :class:`RFC9068Token`."""
from ckms.types import AudienceType
from ckms.types import ClaimSet

from .spaceseparatedlist import SpaceSeparatedList


class RFC9068Token(ClaimSet):
    iss: str
    aud: AudienceType
    exp: int
    sub: int | str
    client_id: str
    iat: int
    jti: str
    auth_time: int | None = None
    acr: str | None = None
    amr: list[str] | None = []
    scope: SpaceSeparatedList = SpaceSeparatedList()

    class Config(ClaimSet.Config):
        json_encoders = {
            **ClaimSet.Config.json_encoders,
            SpaceSeparatedList: lambda v: str.join(' ', sorted(v))
        }