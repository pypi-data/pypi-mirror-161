import typing

import pydantic

import cbra
import cbra.resource


class FooExampleResourceModel(pydantic.BaseModel):
    foo: int


class BarExampleResourceModel(pydantic.BaseModel):
    bar: int


class ExampleActionModel(pydantic.BaseModel):
    baz: int


class ExampleResource(cbra.resource.Resource):
    name: str = 'resource'
    name_article: str = 'an'
    pluralname: str = 'resources'
    path_parameter: str = 'id:int'
    model: typing.Any = BarExampleResourceModel | FooExampleResourceModel
    require_authentication: bool = False
    verbose_name: str = 'Example'

    filter_options = [
        cbra.resource.FilterOption(
            alias='search-param1',
            annotation=int,
            description="An integer search parameter"
        )
    ]


    query_parameters = [
        cbra.Query(
            alias="foo",
            default=None,
            annotation=int,
            description="The value of foo"
        ),
        cbra.Query(
            alias="bar",
            default=None,
            annotation=str
        ),
        cbra.Query(
            alias="baz",
            default=[],
            annotation=typing.Optional[typing.List[str]]
        )
    ]

    @cbra.resource.Resource.action(name='example', summary="Perform example action")
    async def example_action(self, dto: ExampleActionModel | FooExampleResourceModel) -> BarExampleResourceModel:
        """Example action on ExampleResource"""
        return dto.dict()

    async def create(self, dto: model) -> FooExampleResourceModel:
        """Create a new resource."""
        return {
            'action': self.action,
            'path_params': self.get_path_params(),
            'dto': dto.dict()
        }

    async def list(self):
        return {
            'action': self.action,
            'path_params': self.get_path_params(),
            'query': self.get_query_parameters()
        }

    async def purge(self):
        return {'action': self.action, 'path_params': self.get_path_params()}

    async def retrieve(self, id: int):
        return {'action': self.action, 'id': id, 'path_params': self.get_path_params()}

    async def update(self, id: int):
        return {'action': self.action, 'id': id, 'path_params': self.get_path_params()}

    async def replace(self, id: int, dto: model):
        return {
            'action': self.action,
            'path_params': self.get_path_params(),
            'dto': dto.dict()
        }

    async def delete(self, id: int):
        return {'action': self.action, 'id': id, 'path_params': self.get_path_params()}


def get_asgi_application() -> cbra.Application:
    app = cbra.Application()
    app.add(ExampleResource, base_path='/')
    return app


app = get_asgi_application()
if __name__ == '__main__':
    cbra.run('__main__:app', reload=True, port=5000)
