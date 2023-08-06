"""Declares :class:`OptionsResponse`."""
from typing import cast
from typing import Any

from starlette.background import BackgroundTask
from starlette.responses import Response


class OptionsResponse(Response):

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None
    ) -> None:
        super().__init__( # type: ignore
            content=b"",
            status_code=status_code,
            headers=headers or {},
            background=cast(BackgroundTask, background)
        )