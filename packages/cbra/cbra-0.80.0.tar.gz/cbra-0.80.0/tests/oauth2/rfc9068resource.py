# pylint: skip-file
import typing

import cbra
import cbra.exceptions
from cbra.ext.oauth2 import RFC9068Principal


class RFC9068Resource(cbra.Resource):
    name: str = 'resource'
    pluralname: str = 'resources'
    path_parameter: str = 'id:int'
    principal_factory = RFC9068Principal()

    async def authorize(self):
        if not self.principal.has_scope("read"):
            raise cbra.exceptions.NotAuthorized

    async def retrieve(self) -> typing.Dict[str, str]:
        return {
            "message": "Hello world!"
        }