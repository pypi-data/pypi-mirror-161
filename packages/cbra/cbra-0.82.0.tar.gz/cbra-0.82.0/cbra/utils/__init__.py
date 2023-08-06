# pylint: skip-file
import datetime
import functools
import inspect
import itertools
import typing
from inspect import Parameter

from .mediatypes import media_type_matches
from .mediatypes import parse_header


__all__ = [
	'media_type_matches',
    'normalize_signature',
    'parse_header',
]


class DeferredException:
    """Defer raising the exception until an attribute is accessed."""
    exc: BaseException

    def __init__(self, exc: BaseException):
        self.exc = exc

    def raise_exception(self) -> typing.NoReturn:
        raise self.exc

    def __getattr__(self, attname: str) -> typing.NoReturn:
        raise self.exc

    __bytes__ = raise_exception
    __str__ = raise_exception


def current_timestamp() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def docstring(cls: type[typing.Any]): # type: ignore
    def update_func(func):
        func.__doc__ = getattr(cls, func.__name__).__doc__
        return func
    return update_func


def order_parameters(params: typing.List[Parameter]) -> typing.List[Parameter]:
    """Take a list of parameters and ensure that they are ordered correctly i.e.
    positional arguments, keyword arguments, variable positional arguments and
    variable keyword arguments.
    """
    default = [x for x in params if x.default != Parameter.empty]
    nondefault = [x for x in params if x.default == Parameter.empty]
    result = itertools.chain(
        nondefault,
        [x for x in default if x .kind == Parameter.POSITIONAL_ONLY],
        [x for x in default if x .kind == Parameter.POSITIONAL_OR_KEYWORD],
        [x for x in default if x .kind == Parameter.VAR_POSITIONAL],
        [x for x in default if x .kind == Parameter.KEYWORD_ONLY],
        [x for x in default if x .kind == Parameter.VAR_KEYWORD],
    )
    return list(result)


def normalize_signature(func):
    """Normalize the signature of a function or method so that it
    can be used as a :mod:`fastapi` request handler.
    """
    sig = inspect.signature(func)
    func.__signature__ = sig.replace(
        parameters=[
            x for x in sig.parameters.values()
            if x.name != 'self'
        ]
    )
    return func


class PositionalArgument(inspect.Parameter):

    def __init__(self,
        name: str,
        annotation: type = None,
        **kwargs
    ):
        super().__init__(
            name=name,
            kind=Parameter.POSITIONAL_ONLY,
            annotation=annotation,
            **kwargs
        )


class ClassPropertyDescriptor:

    @classmethod
    def new(cls, func: typing.Callable[..., typing.Any]) -> typing.Any:
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