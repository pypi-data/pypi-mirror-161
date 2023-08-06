# pylint: disable=E0202,W0212
"""Declares :class:`Dependency`."""
import asyncio
import inspect
import typing

import fastapi.params


class Dependency(fastapi.params.Depends):
    """Like :class:`fastapi.Depends`, but exposes a method to get
    the dependency. This allows the subclassing of :class:`Dependency` for
    specific use cases and dependency injection strategies.

    .. literalinclude:: ../../../examples/dependency-injection-dependency.py
      :language: python

    The `dependency` argument is used to inject the function that resolves
    the dependency. If it is omitted, then :meth:`get_resolver()` is invoked
    when the :class:`Dependency` is being called.

    Subclasses may override the :meth:`get_resolver()` method to implement
    additional logic when resolving the callable that is injected.

    .. automethod:: resolve()

    .. automethod:: get_resolver()
    """
    __module__: str = 'cbra.ext.ioc'
    _is_coroutine = asyncio.coroutines._is_coroutine

    @property
    def __signature__(self) -> inspect.Signature:
        return self.get_signature()

    def __init__(self,
        dependency: typing.Optional[typing.Callable[..., typing.Any]] = None,
        use_cache: bool = True
    ):
        # Check if the asyncio.iscoroutinefunction() call returns
        # True for this object, since it depends on a private
        # symbol.
        assert asyncio.iscoroutinefunction(self) # nosec
        if dependency is not None:
            self.resolve = dependency
        super().__init__(
            dependency=self,
            use_cache=use_cache
        )

    def get_resolver(self) -> typing.Callable:
        """Return the callable that is used to resolve the dependency."""
        return self.resolve

    def get_signature(self) -> inspect.Signature:
        """Return a :class:`inspect.Signature` instance representing the
        call sigature of the dependency resolver.
        """
        return inspect.signature(self.get_resolver())

    async def resolve(self):
        """Resolve the dependency. The default implementation always raises
        :exc:`NotImplementedError`.
        """
        raise NotImplementedError

    async def __call__(self, *args, **kwargs) -> typing.Any:
        resolver = self.get_resolver()
        if inspect.isasyncgenfunction(resolver)\
        or inspect.isgeneratorfunction(resolver):
            raise ValueError(
                "Dependencies must not be (async) generators."
            )
        return await resolver(*args, **kwargs)
