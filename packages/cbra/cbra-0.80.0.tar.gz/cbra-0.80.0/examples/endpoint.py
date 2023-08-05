import typing

import pydantic

import cbra


class GrandParent(pydantic.BaseModel):
    foo: str


class Parent(pydantic.BaseModel):
    parent: GrandParent


class Child(pydantic.BaseModel):
    parent: Parent



class ExampleEndpoint(cbra.Endpoint):
    require_authentication = False
    model=Child

    async def handle( # type: ignore
        self,
        dto: typing.Optional[typing.Dict[str, typing.Any]] = None
    ) -> typing.Dict[str, typing.Any]: # type: ignore
        """Example endpoint."""
        return {
            "message": "Hello world!",
            "body": dto if dto else None
        }


app = cbra.Application()
app.add(ExampleEndpoint, base_path='/get', method="GET")
app.add(ExampleEndpoint, base_path='/post', method="POST")


if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)
