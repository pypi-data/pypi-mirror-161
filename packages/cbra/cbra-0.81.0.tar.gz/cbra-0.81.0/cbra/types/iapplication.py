"""Declares :class:`IApplication`."""
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet


class IApplication:
    codec: PayloadCodec

    def get_jwks(self) -> JSONWebKeySet:
        raise NotImplementedError