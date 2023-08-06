"""Declares :class:`CodeChallenge`."""
import os

import typing

import pydantic

from .codechallengemethod import CodeChallengeMethod
from .dependantmodel import DependantModel


CodeChallengeType = pydantic.constr(min_length=43, max_length=128)


class CodeChallenge(DependantModel):
    __module__: str = 'cbra.ext.oauth2.types'

    challenge: CodeChallengeType = pydantic.Field(
        default=None,
        title="Code challenge",
        alias='code_challenge',
        description=(
            'A high-entropy cryptographic random string using the unreserved '
            'characters [A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~" from '
            'Section 2.3 of RFC 3986, with a minimum length of 43 characters '
            'and a maximum length of 128 characters.'
        ),
        example=bytes.hex(os.urandom(56))
    )

    method: typing.Optional[CodeChallengeMethod] = pydantic.Field(
        default=None,
        title="Code challenge method",
        alias="code_challenge_method",
        description=(
            "Specifies the method used to calculate and verify the code "
            "challenge. Defaults to `plain` if not present in the request."
        ),
        enum=["plain", "S256"],
        example="S256"
    )