"""Declares :class:`CodeChallengeMethod`."""
import enum


class CodeChallengeMethod(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    plain = "plain"
    s256 = "S256"