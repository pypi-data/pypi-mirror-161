# pylint: skip-file
import typing


__all__ = [
    'REQUEST_METHODS'
]


REQUEST_METHODS: typing.Set[str] = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "OPTIONS",
    "DELETE",
    "TRACE",
    "HEAD"
}