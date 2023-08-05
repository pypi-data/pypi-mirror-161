"""Declares :class:`MessagePublisher`."""
from cbra.ext.ioc import Dependency
from .transaction import Transaction


class MessagePublisher(Dependency):
    """A :class:`cbra.Dependency` implementation that provides a transactional
    message publisher.
    """
    __module__: str = 'cbra'

    def __init__(self):
        Dependency.__init__(self, use_cache=True)

    async def resolve(self): # pragma: no cover
        async with Transaction() as tx:
            yield tx


_default: MessagePublisher = MessagePublisher()
