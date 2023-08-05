"""Declares :class:`DependencyReceiver`."""


class DependencyReceiver:
    """A mixin class that exposes a method to declare and receive dependencies
    injected through the :mod:`fastapi` dependency injection framework.
    """
    __module__: str = 'cbra'

    def inject(self) -> None:
        """Inject dependencies into the instance. To implement this feature,
        subclasses must override :meth:`inject()` and update the instance
        state accordingly. The default implementation does nothing.
        """
        pass
