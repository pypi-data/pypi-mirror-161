"""Declares :class:`BaseEnvelope`."""
import typing

import fastapi
import pydantic


class BaseEnvelope(pydantic.BaseModel):
    __module__: str = 'cbra.models'

    @classmethod
    def fromresult(cls,
        request: fastapi.Request,
        result: typing.Union[dict, list],
        params: dict
    ):
        """Instantiate a new envelope from the return value of a request
        handler.
        """
        if not isinstance(result, (dict, list)): # pragma: no cover
            raise TypeError("Return value must be a dictionary or list.")
        if isinstance(result, dict):
            params['spec'] = result
        if isinstance(result, list):
            params['items'] = [cls._envelope_factory(x) for x in result]
        return cls(**params)

    def get_path_parameter(self, request: fastapi.Request) -> typing.Union[int, str]:
        """Return the path parameter from this object."""
        return getattr(self.spec, self.Config.path_parameter)

    def is_list(self) -> bool:
        """Return a boolean indicating if the envelope contains a list."""
        return self._is_list

    def is_resource(self) -> bool:
        """Return a boolean indicating if the envelope contains a resource."""
        return self._is_resource

    def set_link(self, name: str, url: str):
        """Update the links attribute of the metadata."""
        self.metadata.links[name] = url
