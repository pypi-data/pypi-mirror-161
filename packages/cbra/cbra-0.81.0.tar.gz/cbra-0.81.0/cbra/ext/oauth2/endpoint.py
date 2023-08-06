"""Declares :class:`OptionsMixin`."""
from typing import Any
from typing import Callable

import fastapi

import cbra
from cbra.types import ICorsPolicy
from cbra.types import IEndpoint
from cbra.cors import EndpointCorsPolicy
from .exceptions import Error


class Endpoint(cbra.Endpoint):
    cors_policy: type[ICorsPolicy] = EndpointCorsPolicy
    disable_options: bool = False
    methods: set[str]
    name: str
    state: str | None = None
    summary: str
    options_description: str

    @classmethod
    def add_to_router(
        cls,
        *,
        app: IEndpoint.RouterType,
        base_path: str = '/',
        method: str | None = None,
        cors_policy: type[ICorsPolicy] | None = None,
        request_handler: Callable[..., IEndpoint.ResponseTypes] | None = None,
        **kwargs: Any
    ) -> None:
        name = kwargs.pop('name', None) or cls.name
        cors_policy = cls.cors_policy.configure(
            allowed_methods=cls.methods | {"OPTIONS"},
            allowed_headers={
                "Content-Type"
            }
        )
        for method in cls.methods:
            super().add_to_router(
                app=app,
                base_path=base_path,
                cors_policy=cors_policy,
                method=method,
                request_handler=request_handler,
                name=name,
                **kwargs
            )

        if not cls.disable_options:
            Options = cbra.Endpoint.new(
                handle=cls.options
            )
            Options.add_to_router(
                app=app,
                base_path=base_path,
                cors_policy=cors_policy,
                request_handler=cls.options,
                method="OPTIONS",
                name=f'{name}.options',
                summary=cls.summary,
                description=cls.options_description,
                response_description="Allowed methods and CORS policy.",
                **kwargs
            )

    async def options(self) -> fastapi.Response:
        return fastapi.Response(
            headers={
                'Allow': str.join(',', sorted(self.cors_policy.allowed_methods))
             },
            status_code=200
        )

    @cbra.Endpoint.on_exception.register # type: ignore
    async def on_auth2_exception(
        self,
        exception: Error
    ) -> fastapi.Response:
        return await exception.as_response(
            request=self.request,
            state=self.state
        )

    @classmethod
    def exception_handler(cls, exception_class: type[Exception]):
        def decorator_factory(func: Callable[..., Any]):
            cbra.Endpoint.on_exception.register # type: ignore
            return func
        return decorator_factory