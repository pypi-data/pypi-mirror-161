"""Declares :class:`InjectedMessageHandler`."""
from typing import Any

import aorta


# These classes exist for legacy compatibility; cbra >-0.67.0 is
# fully compatible with Aorta.
class CommandHandler(aorta.CommandHandler):
    __abstract__: bool = True
    __module__: str = 'cbra'

    async def handle(self, command: Any) -> None: # type: ignore
        raise NotImplementedError


class EventListener(aorta.EventListener):
    __abstract__: bool = True
    __module__: str = 'cbra'

    async def handle(self, event: Any) -> None: # type: ignore
        raise NotImplementedError