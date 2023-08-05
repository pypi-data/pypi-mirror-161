# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
"""Declares :class:`IPrincipal`."""
import typing

import cbra.types


class IPrincipal(cbra.types.IPrincipal):
    """A :class:`~cbra.types.IPrincipal` interface with additional
    methods.
    """
    __module__: str = 'cbra.ext.oauth2.types'

    #: The OAuth 2.0 client that identified this principal.
    client_id: str

    #: The scope that was granted to the principal.
    scope: typing.Set[str]

    def is_authenticated(self) -> bool:
        return True