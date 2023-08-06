"""Declares :class:`AnonymousReadCorsPolicy`."""
from .basecorspolicy import BaseCorsPolicy


class AnonymousReadCorsPolicy(BaseCorsPolicy):
    __module__: str = 'cbra.cors'
    allowed_methods: set[str] = {"GET"}
    allowed_headers: set[str] = {"Wants-Digest"}
    allowed_response_headers: set[str] = {"Digest"}

    async def get_allowed_origins(self) -> set[str]:
        if not self.origin:
            return set()
        return {self.origin}