"""Demonstrates basic usage of class-based views with FastAPI."""
import typing

import fastapi
import pydantic

import cbra


class ExampleResourceModel(pydantic.BaseModel):
    object_id: int


class ExampleSubresourceModel(pydantic.BaseModel):
    object_id: int
    child_id: int


class Subresource(cbra.PublicResource):
    path_parameter: int = 'child_id'
    name: str = 'sub'

    class Meta:
        name: str = 'subresource'
        path_parameter: int = 'child_id'

    async def list(self, object_id: str):
        return {'object_id': object_id}

    async def retrieve(self, object_id: str, child_id: int):
        return {'object_id': object_id, 'child_id': child_id}


class ExampleResource(cbra.PublicResource):
    name: str = 'example'
    path_parameter: str = 'object_id'
    subresources = [Subresource]
    resource_class = ExampleSubresourceModel

    class Meta:
        name: str = 'example'
        path_parameter: str = 'object_id'

    async def create(self, dto: ExampleSubresourceModel) -> typing.Union[ExampleResourceModel, ExampleSubresourceModel]:
        return dto

    async def list(self):
        return []

    async def destroy(self, object_id: str):
        return {'object_id': object_id}

    async def exists(self, object_id: str):
        return {'object_id': object_id}

    async def receive(self, object_id: str, dto: dict):
        return {'object_id': object_id, 'dto': dto}

    async def replace(self, object_id: str, dto: dict):
        return {'object_id': object_id, 'dto': dto}

    async def retrieve(self, object_id: str):
        return {'object_id': object_id}

    async def update(self, object_id: str, dto: dict):
        return {'object_id': object_id, 'dto': dto}


class ExampleProtectedResource(cbra.Resource):
    name: str = 'protected'
    path_parameter: str = 'object_id'

    class Meta:
        name: str = 'secret'
        path_parameter: str = 'object_id'

    async def retrieve(self, object_id: str):
        return {'object_id': object_id, 'principal': self.principal}


app = cbra.Application(
    docs_url='/ui',
    redoc_url='/docs'
)
ExampleResource.add_to_router(app)
ExampleProtectedResource.add_to_router(app)


if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)
