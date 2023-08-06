# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`EndpointResolver`."""
from collections import OrderedDict
from inspect import getmembers
from inspect import Parameter
from inspect import Signature
from typing import get_type_hints
from typing import Any

import fastapi.params


class EndpointResolver:
    """Inspect the attributes of a class that are :mod:`fastapi.params.Depends`
    instances and ensure that they are resolved prior to invoking the request
    handler.
    """
    endpoint: Any
    params: OrderedDict[str, Parameter]

    @property
    def __signature__(self) -> Signature:
        return Signature(
            parameters=list(self.params.values()),
            return_annotation=None
        )

    def __init__(self, endpoint: Any):
        self.endpoint = endpoint
        self.params = OrderedDict()
        self.hints = get_type_hints(self.endpoint)
        for attname, value in getmembers(self.endpoint):
            if not isinstance(value, fastapi.params.Depends):
                continue
            self.params[attname] = Parameter(
                kind=Parameter.POSITIONAL_ONLY,
                name=attname,
                default=value,
                annotation=self.hints.get(attname)
            )

    def __call__(self, **kwargs: Any) -> None:
        for attname, value in kwargs.items():
            assert attname in self.params # nosec
            setattr(self.endpoint, attname, value)