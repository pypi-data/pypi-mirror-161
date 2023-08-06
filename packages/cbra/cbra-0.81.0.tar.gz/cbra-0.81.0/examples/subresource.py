import cbra
import cbra.resource


class GrandChildResource(cbra.resource.PublicResource):
    path_parameter: str = 'grandchild_id'

    async def list(self, parent_id: int, child_id: int):
        return {'parent_id': parent_id, 'child_id': child_id}

    async def retrieve(
        self,
        parent_id: int,
        child_id: int,
        grandchild_id: int
    ):
        return {
            'parent_id': parent_id,
            'child_id': child_id,
            'grandchild_id': grandchild_id
        }


class ChildResource(cbra.resource.PublicResource):
    path_parameter: str = 'child_id:int'
    subresources = [GrandChildResource]

    async def list(self, parent_id: int):
        return {'parent_id': parent_id}

    async def retrieve(self, parent_id: int, child_id: int):
        return {'parent_id': parent_id, 'child_id': child_id}


class ParentResource(cbra.resource.PublicResource):
    subresources: list[type[cbra.resource.Resource]] = [
        ChildResource
    ]
    path_parameter: str = 'parent_id'

    async def list(self):
        pass


app = cbra.Application()
app.add(ParentResource)


if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)