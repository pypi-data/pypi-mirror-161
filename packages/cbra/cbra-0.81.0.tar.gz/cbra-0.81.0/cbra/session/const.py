"""Declares constants used by the :mod:`cbra.session` module."""
from cbra.conf import settings # type: ignore


SESSION_COOKIE_AUDIENCE: str = (
    getattr(settings, 'SESSION_COOKIE_AUDIENCE', None) # type: ignore
)


SESSION_COOKIE_NAME: str = (
    getattr(settings, 'SESSION_COOKIE_NAME', None) # type: ignore
    or 'session-claims'
)

SESSION_SIGNING_KEYS: str = (
    getattr(settings, 'SESSION_SIGNING_KEY', None) # type: ignore
    or ['session-signer-1', 'session-signer-2']
)

SESSION_ENCRYPTION_KEYS: str = (
    getattr(settings, 'SESSION_ENCRYPTION_KEY', None) # type: ignore
    or ['session-encrypter-1']
)

SESSION_ENCRYPTION_ALG: str = (
    getattr(settings, 'SESSION_ENCRYPTION_ALG', None) # type: ignore
    or 'A256GCM'
)
