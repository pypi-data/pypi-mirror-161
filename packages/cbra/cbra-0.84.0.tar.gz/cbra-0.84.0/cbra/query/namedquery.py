"""Declates :class:`NamedQuery`."""
import inspect
import re
import typing

import pydantic

from cbra.ext.ioc import Dependency
from cbra.ext.ioc import Injected
from ..dependencywrapper import DependencyWrapper
from ..utils import PositionalArgument
from .namedqueryargs import NamedQueryArgs
from .namedquerymetaclass import NamedQueryMetaclass
from .queryrunner import QueryRunner


class NamedQuery(Dependency, metaclass=NamedQueryMetaclass):
    """A named query that is executed by a dynamically injected
    implementation of :class:`cbra.QueryRunner`.

    The `runner` arguments point to a dependency that is injected at runtime
    under the given key. It is expected to implement :class:`cbra.QueryRunner`
    interface. The default value is ``'QueryRunner'``.
    """
    __abstract__: bool = True
    __module__: str = 'cbra.query'
    default_runner: str = 'default'

    @classmethod
    def get_method_name(cls) -> str:
        """Convert class name `name` to underscored method name."""
        return str.lower(re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__))

    def __init__(self, using: typing.Optional[str] = None, run: bool = True):
        self.must_run = run
        self.using = using or self.default_runner
        self.resolve = DependencyWrapper(self._run, [
            PositionalArgument(
                name='runner',
                default=Injected(
                    f'cbra.runner.{self.using}',
                    invoke=True,
                    default=None
                ),
                annotation=QueryRunner
            )
        ] + list(inspect.signature(self.build).parameters.values()))
        super().__init__(use_cache=True)

    async def execute(self, runner: QueryRunner, query: NamedQueryArgs):
        """Invokes the appropriate method on the :class:`cbra.QueryRunner`
        `runner` instance.
        """
        return await getattr(runner, f'run_{self.get_method_name()}')(query)

    def build(self) -> pydantic.BaseModel:
        """Build the query model from the given parameters."""
        raise NotImplementedError

    async def _run(self, runner: QueryRunner, *args, **kwargs):
        query = self.build(*args, **kwargs)
        if not self.must_run:
            return query

        return await self.execute(runner, query)
