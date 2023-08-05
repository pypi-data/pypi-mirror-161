# pragma: no cover
"""Declares :class:`DependencyWrapper`."""
import asyncio
import collections
import inspect
import typing
from inspect import Parameter
from inspect import Signature


class DependencyWrapper:
    """Wraps a :class:`cbra.Dependency` or other other that supports
    :term:`Injected Parameters` and allows the dynamic configuration of its
    parameters.
    """
    _is_coroutine = asyncio.coroutines._is_coroutine

    @property
    def __signature__(self) -> Signature: # pragma: no cover
        return Signature(self.get_signature_parameters())

    def __init__(self, func: typing.Callable, args: typing.List[Parameter]):
        """The default behavior when constructing a :class:`DependencyWrapper`
        instance, is to prepend the items in `args` to the signature of
        `func`. If other behavior is required, then the subclass must
        override :meth:`get_signature_parameters()`.
        """
        # Check if the asyncio.iscoroutinefunction() call returns
        # True for this object, since it depends on a private
        # symbol.
        assert asyncio.iscoroutinefunction(self) # nosec
        self.func = func
        self.call_args = collections.OrderedDict([(x.name, x) for x in args])

    def get_signature_parameters(self) -> typing.List[Signature]: # pragma: no cover
        """Get the list of :class:`inspect.Parameter` instances specifying
        the callables' signature.
        """
        sig = inspect.signature(self.func)
        return list(self.call_args.values()) + [
            x for x in sig.parameters.values()
            if x.name not in self.call_args
            and x.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
        ]

    async def __call__(self, *args, **kwargs):
        return await self.func(*args, **kwargs)
