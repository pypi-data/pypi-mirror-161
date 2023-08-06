import typing

import cbra
import cbra.cors


class ExampleEndpoint(cbra.Endpoint):

    async def handle(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return {}


class ExampleCorsPolicy(cbra.cors.BaseCorsPolicy):
    allow_credentials: bool = True
    allowed_methods: typing.Set[str] = {"GET", "POST"}
    allowed_headers: typing.Set[str] = {"Authorization", "X-Custom-Header"}


def get_asgi_application() -> cbra.Application:
    app = cbra.Application()
    app.add(
        cbra.Options.new(
            allowed_methods={"GET", "POST", "OPTIONS"},
            cors_policy=ExampleCorsPolicy
        ),
        base_path='/'
    )
    app.add(
        ExampleEndpoint.new(cors_policy=ExampleCorsPolicy),
        base_path='/',
        method='GET'
    )
    app.add(
        ExampleEndpoint.new(cors_policy=ExampleCorsPolicy),
        base_path='/',
        method='POST'
    )
    return app


app = get_asgi_application()
if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)