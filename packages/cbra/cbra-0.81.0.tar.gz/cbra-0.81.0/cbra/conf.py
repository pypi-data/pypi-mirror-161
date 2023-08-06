# pylint: disable=W0611
"""This module is just a proxy to :mod:`unimatrix.conf`."""
from typing import cast
from typing import Any

from unimatrix.conf import settings # type: ignore


__all__: list[str] = ['settings']

settings: Any = cast(Any, settings)