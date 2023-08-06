"""Declares :class:`DependantRunner`."""
import typing

import fastapi
from fastapi.dependencies.utils import get_dependant
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.dependencies.utils import solve_dependencies

from .dependencyreceiver import DependencyReceiver


class DependantRunner:
    """Exposes a interface to run functions and methods that inject dependencies
    using :class:`cbra.Dependency`.
    """
    __module__: str = 'cbra'

    async def run_dependant(self,
        request: fastapi.Request,
        handle: typing.Callable,
        body: typing.Union[bytes, dict, list, str] = b'',
        path: str = '/',
        *args, **kwargs
    ):
        """Run dependant `handle` and return the result."""
        dependant = get_dependant(path=path, call=handle)
        dependant.dependencies.extend(self._get_dependants(path))
        if isinstance(handle, DependencyReceiver):
            dependant.dependencies.append(
                self._get_dependant(handle.inject, path)
            )
        values, errors, tasks, response, _ = await solve_dependencies(
            request=request,
            dependant=dependant,
            body=body,
            dependency_overrides_provider=None
        )
        if errors or tasks or response.status_code:
            raise NotImplementedError(errors, tasks, response)
        kwargs.update(values)
        return await dependant.call(*args, **kwargs)

    def get_dependants(self) -> typing.List[typing.Callable]:
        """Return the list of additional dependants that must be solved
        when invoking the callable.
        """
        return []

    def _get_dependants(self, path: str):
        return [
            get_parameterless_sub_dependant(
                depends=fastapi.Depends(x),
                path=path
            )
            for x in self.get_dependants()
        ]

    def _get_dependant(self, func, path):
        return get_parameterless_sub_dependant(
            depends=fastapi.Depends(func),
            path=path
        )
