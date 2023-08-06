# pylint: skip-file
import typing

import pydantic

import cbra


class FooModel(pydantic.BaseModel):
    foo: int


class BarModel(pydantic.BaseModel):
    bar: int


BodyModel = typing.Union[
    FooModel,
    BarModel
]


class ContentNegotiationEndpoint(cbra.Endpoint):
    model = BodyModel

    async def handle(self, dto: BodyModel):
        return dto.dict()