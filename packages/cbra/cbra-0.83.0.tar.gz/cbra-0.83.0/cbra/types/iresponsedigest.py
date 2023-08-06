"""Declares :class:`IResponseDigest`."""


class IResponseDigest:
    __module__: str = 'cbra.types'
    algorithm_name: str

    def calculate(self, message: bytes) -> str:
        raise NotImplementedError