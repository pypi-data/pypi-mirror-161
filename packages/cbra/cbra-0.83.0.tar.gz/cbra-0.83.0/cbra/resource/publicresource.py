"""Declares :class:`PublicResource`."""
from .resource import Resource


class PublicResource(Resource):
    __abstract__: bool = True
    __module__: str = 'cbra.resource'
    require_authentication: bool = False