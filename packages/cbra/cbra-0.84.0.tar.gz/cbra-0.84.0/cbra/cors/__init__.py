# pylint: skip-file
from typing import TypeAlias

from .anonymousreadcorspolicy import AnonymousReadCorsPolicy
from .basecorspolicy import BaseCorsPolicy
from .defaultcorspolicy import DefaultPolicy
from .endpointcorspolicy import EndpointCorsPolicy
from .null import NullCorsPolicy


__all__ = [
    'AnonymousReadCorsPolicy',
    'BaseCorsPolicy',
    'CorsPolicyType',
    'DefaultPolicy',
    'EndpointCorsPolicy',
    'NullCorsPolicy'
]

CorsPolicyType: TypeAlias = BaseCorsPolicy