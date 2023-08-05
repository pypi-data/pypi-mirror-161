# type: ignore
"""Declares various utility functions."""
import functools
import typing


def dispatcher(
    func: typing.Callable[
        ...,
        typing.Coroutine[typing.Any, typing.Any, typing.Any]
    ]
) -> typing.Coroutine[typing.Any, typing.Any, typing.Any]:
    """Decorate a function to parse incoming requests and determine
    the appropriate event types.
    """
    handlers: dict[str, typing.Any] = {}

    @functools.wraps(func)
    async def dispatch(self, *args, **kwargs):
        event_name, params = await func(self, *args, **kwargs)
        handler =  handlers.get(event_name)
        if handler is None:
            raise AttributeError(f"No handler for {event_name}")
        return await handler(self, params)

    def register_handler(event_name):
        """Registers a handler with the given `event_name`."""
        def decorator_factory(func):
            handlers[event_name] = func
            return func
        return decorator_factory

    dispatch.on = register_handler
    dispatch.handlers = handlers
    return dispatch


class ClassPropertyDescriptor:

    @classmethod
    def new(cls, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        return cls(func)

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, cls=None) -> typing.Any:
        if cls is None:
            cls = type(obj)
        return self.fget.__get__(obj, cls)()

    def __set__(self, obj, value) -> typing.NoReturn:
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func) -> typing.Any:
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


classproperty = ClassPropertyDescriptor.new