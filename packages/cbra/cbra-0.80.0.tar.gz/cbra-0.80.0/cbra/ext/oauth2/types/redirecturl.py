"""Declares :class:`RedirectURL`."""
import operator
import urllib.parse
from typing import Any
from typing import Generator

from ..exceptions import MissingRedirectURL
from ..exceptions import RedirectForbidden


class RedirectURL:
    """Represents the redirect URI for the **Authorization Endpoint**."""
    __module__: str = 'cbra.ext.oauth2.types'
    params: dict[str, Any]
    url: urllib.parse.ParseResult

    @classmethod
    def __get_validators__(cls) -> Generator[Any, None, None]:
        yield cls.validate

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None: # pragma: no cover
        field_schema.update({
            "type": "str"
        })

    @classmethod
    def validate(
        cls,
        value: str | None
    ) -> "RedirectURL":
        """Parse `value` into a :class:`urllib.parse.ParseResult`
        instance and verify that the URL is served over HTTPS and
        is redirectable.
        """
        if not value:
            return cls(None)
        if isinstance(value, cls):
            return value
        assert isinstance(value, str) # nosec
        p = urllib.parse.urlparse(value)
        if p.scheme != "https" and p.hostname != '127.0.0.1':
            raise RedirectForbidden(
                error_description="Redirect URL must serve over HTTPS."
            )
        if p.fragment:
            raise RedirectForbidden(
                error_description="Redirect URL must not contain a fragment."
            )
        if not p.netloc:
            raise RedirectForbidden(
                error_description=f"Unable to redirect to {value}."
            )
        return cls(p)

    def __init__(self, url: urllib.parse.ParseResult | None = None):
        self.url = url
        self.params = {}
        if self.url is not None and self.url.query:
            self.params = urllib.parse.parse_qs(self.url.query)

    def authorize(self, **params: str | None) -> str:
        """Authorize the redirect to the URL specified by the :class:`RedirectURI`
        and return a new instance with the query parameters.
        """
        if self.url is None:
            raise MissingRedirectURL
        params = {
            **self.params,
            **{k: v for k, v in params.items() if v is not None}
        }
        parts = list(self.url)
        parts[4] = urllib.parse.urlencode(params, True)
        return urllib.parse.urlunparse(parts)

    def is_loopback(self) -> bool:
        """Return a boolean indicating if the URL is the loopback
        interface.
        """
        return self.url.hostname == "127.0.0.1"

    def __bool__(self) -> bool:
        return self.url is not None

    def __str__(self) -> str:
        return urllib.parse.urlunparse(self.url) if self.url else ''

    def __eq__(self, url: object) -> bool:
        x = urllib.parse.urlparse(str(self))
        y = urllib.parse.urlparse(str(url))
        if "127.0.0.1" in {x.hostname, y.hostname}:
            is_equal = operator.eq(
                (x.scheme, x.hostname, x.path, x.query),
                (y.scheme, y.hostname, y.path, y.query),
            )
        else:
            is_equal = operator.eq(
                (x.scheme, x.netloc, x.path, x.query),
                (y.scheme, y.netloc, y.path, y.query),
            )
        return is_equal

    def __repr__(self) -> str:
        return f"<RedirectURI: {self}>"