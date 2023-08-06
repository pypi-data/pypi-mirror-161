"""Declares :class:`Transaction`."""
import logging
import uuid
from typing import Any

import aorta

from .params import ServerPublisher


class Transaction:
    """Encapsulates a transaction for :mod:`cbra` components, such as
    HTTP request handlers, webhooks, event listeners and commands handlers. The
    :class:`Transaction` object ensures that either all commands, events or
    tasks are published, or none of them.
    """
    logger: logging.Logger = logging.getLogger('uvicorn')
    _correlation_id: str | uuid.UUID | None = None
    _transaction_id: str
    _commands: list[aorta.Command]
    _events: list[aorta.Event]
    _publisher: aorta.MessagePublisher

    @property
    def correlation_id(self) -> str:
        if self._correlation_id is None:
            self._correlation_id = uuid.uuid4()
        return str(self._correlation_id)

    @correlation_id.setter
    def correlation_id(self, value: str | uuid.UUID):
        self._correlation_id = value

    def __init__(self, publisher: aorta.MessagePublisher = ServerPublisher):
        self._commands = []
        self._events = []
        self._publisher = publisher
        self._transaction_id = str(uuid.uuid4())

    def abort(self):
        if self._commands or self._events:
            self.logger.info(
                "Abort messaging transaction (correlationId: %s)",
                self.correlation_id
            )
            self._commands = []
            self._events = []

    def set_correlation_id(self, correlation_id: str | uuid.UUID | None) -> None:
        """Sets the correlation identifier for this transaction."""
        self._correlation_id = correlation_id or uuid.uuid4()

    async def commit(self):
        """Submits pending commands and events."""
        if self._commands or self._events:
            await self._publisher.publish(
                objects=self._commands + self._events, # type: ignore
                correlation_id=self.correlation_id
            )
            self.logger.info(
                "Commit messaging transaction (correlationId: %s)",
                self.correlation_id
            )

    def issue(self, command: aorta.Command):
        """Issue a command using the default command issuer."""
        if not self._commands:
            self.logger.info(
                "Begin messaging transaction (correlationId: %s)",
                self.correlation_id
            )
        self._commands.append(command)

    def publish(self, event: aorta.Event):
        """Publish an event using the default event publisher."""
        if not self._events:
            self.logger.info(
                "Begin messaging transaction (correlationId: %s)",
                self.correlation_id
            )
        self._events.append(event)

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        cls: type[BaseException],
        exception: BaseException,
        traceback: Any
    ) -> bool:
        if exception is not None:
            self.abort()
            return False
        await self.commit()
        return False


class NullTransaction(Transaction):
    """A :class:`Transaction` implementation that does nothing."""

    def abort(self):
        pass

    async def commit(self):
        pass
