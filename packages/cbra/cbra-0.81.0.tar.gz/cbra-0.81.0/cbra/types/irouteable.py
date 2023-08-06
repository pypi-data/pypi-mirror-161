"""Declares :class:`IRequestHandler`."""
import typing

import fastapi


class IRouteable:
    """The interface for objects that add routes to an ASGI
    application.
    """
    __module__: str = 'cbra.types'
    RouterType: typing.TypeAlias = typing.Union[
        fastapi.FastAPI,
        fastapi.APIRouter
    ]

    @classmethod
    def add_to_router(
        cls,
        *,
        app: RouterType,
        base_path: str,
        default_error_responses: bool = True,
        **kwargs: typing.Any
    ) -> None:
        raise NotImplementedError