"""Declares :class:`IUserAgent`."""
import typing

import fastapi


class IUserAgent:
    __module__: str = 'cbra.types'

    def __init__(
        self,
        user_agent: typing.Optional[str] = fastapi.Header(
            default=None,
            title="User agent",
            alias="User-Agent",
            description=(
                "Identifies the application, operating system, vendor, "
                "and/or version of the requesting user agent."
            )
        )
    ):
        self.user_agent = user_agent
