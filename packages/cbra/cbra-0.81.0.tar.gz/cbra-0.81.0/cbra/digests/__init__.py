# pylint: skip-file
import base64
import hashlib
import typing

from ckms.utils import b64encode

from cbra.types import IResponseDigest


__all__ = [
    'SHA256Digest',
    'SHA512Digest',
]


class HaslibDigest(IResponseDigest):
    hashfunc: typing.Callable[[bytes], typing.Any]

    @classmethod
    def new(
        cls,
        name: str,
        func: typing.Callable[..., typing.Any] 
    ) -> typing.Type[IResponseDigest]:
        return type('HashlibDigest', (cls,), {
            'algorithm_name': name,
            'hashfunc': func
        })

    def calculate(self, message: bytes) -> str:
        digest = self.hashfunc(message).digest()
        return f'{self.algorithm_name}={bytes.decode(b64encode(digest), "ascii")}'


SHA256Digest = HaslibDigest.new('sha-256', hashlib.sha256)
SHA512Digest = HaslibDigest.new('sha-512', hashlib.sha512)