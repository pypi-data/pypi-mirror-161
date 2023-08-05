"""Declares :class:`DependantSignature`."""
import collections
import inspect
import typing

import fastapi.params
import pydantic

from cbra.ext.ioc import Parameterless


REQUEST_DEPENDENCIES = (
    fastapi.params.Cookie,
    fastapi.params.Header,
    fastapi.params.Path,
    fastapi.params.Query,
)

REQUEST_UNION = typing.Union[REQUEST_DEPENDENCIES]


class DependantSignature:
    """Represents the signature of a dependant."""
    _parameters: typing.Dict[str, inspect.Parameter]
    _returns: typing.Any
    _signature: inspect.Signature

    @property
    def parameters(self) -> typing.Dict[str, inspect.Parameter]:
        """Return the list of signature parameters represented as
        :class:`inspect.Parameter` instances.
        """
        return self._parameters

    @property
    def returns(self) -> typing.Any:
        """The return type of the callable."""
        return self._returns

    def __init__(self, dependant: typing.Callable):
        self._signature = inspect.signature(dependant)
        self._parameters = collections.OrderedDict([
            (x.name, x) for x in list(self._signature.parameters.values())
        ])
        self._returns = self._signature.return_annotation

    def get_request_dependencies(
        self,
        as_parameters: bool = False
    ) -> typing.List[typing.Union[inspect.Parameter, Parameterless]]:
        """Return the list of dependencies that are resolved from a
        :class:`fastapi.Request` instance.
        """
        dependencies: typing.List[typing.Union[inspect.Parameter, Parameterless]] = []
        for param in self.parameters.values():
            if isinstance(param.default, REQUEST_DEPENDENCIES)\
            or inspect.isclass(param.annotation)\
            and issubclass(param.annotation, pydantic.BaseModel):
                p =Parameterless(
                    param.name,
                    param.default,
                    param.annotation
                )
                dependencies.append(p if not as_parameters else p.as_parameter())
            elif hasattr(param.default, 'get_request_dependencies'):
                dependencies.extend(param.default.get_request_dependencies())
            else:
                continue
        return dependencies
