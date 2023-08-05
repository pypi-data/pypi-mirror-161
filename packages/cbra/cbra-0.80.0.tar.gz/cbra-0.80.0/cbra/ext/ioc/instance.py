"""Declares :class:`Instance`."""
import inspect
import typing
from inspect import Signature

from .dependency import Dependency
from .provider import _default as provider
from .provider import Provider


class Instance(Dependency):
    """A :class:`cbra.Dependency` implementation that returns a class instance,
    with the dependencies injected into its constructor.

    If the `dependency` argument is a callable, then invoke the callable when
    the :class:`Instance` is resolved at run time. Otherwise, it is assumed
    to be a string that points to a dependency that was injected at boot using
    :meth:`cbra.Application.inject()`.
    """
    __module__: str = 'cbra.ext.ioc'
    _dependency: typing.Union[str, typing.Type[typing.Any]]
    _factory: typing.Optional[typing.Type[typing.Any]]
    _provider: typing.Optional[Provider]

    @property
    def factory(self) -> typing.Callable[..., typing.Any]:
        """Return the factory callable that produces an instance."""
        if self._factory is None:
            if isinstance(self._dependency, str):
                self._dependency = self.provider.resolve(self._dependency)
            self._factory = self._dependency
        return self._factory

    @property
    def provider(self) -> Provider:
        return self.get_provider()

    @property
    def __signature__(self) -> Signature:
        return inspect.signature(self.factory)

    def __init__(self,
        dependency: typing.Union[str, typing.Type[typing.Any]],
        use_cache: bool = True,
        provider: typing.Optional[Provider] = None
    ):
        """Resolve an instance of `dependency` at runtime.

        If `dependency` is a string, then it is assumed to have been priorly
        injected through the :mod:`cbra.ext.ioc` framework. Else, it should be a
        class (instance of :class:`type`).
        """
        self._dependency = dependency
        self._factory = None
        self._provider = provider
        super().__init__(use_cache=use_cache)

    def get_provider(self) -> Provider:
        return self._provider or provider

    async def resolve(self, *args, **kwargs) -> typing.Any:
        """Return an instance of the class provided to the constructor."""
        return self.factory(*args, **kwargs) # pylint: disable=E1102

    async def __call__(self, *args, **kwargs) -> typing.Any:
        return await self.resolve(*args, **kwargs)
