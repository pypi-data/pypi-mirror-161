# Copyright (C) 2022 Cochise Ruhulessin <cochiseruhulessin@gmail.com>
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
"""Declares :class:`SubjectPrincipal`."""
import dataclasses

from cbra.types import IPrincipal


@dataclasses.dataclass
class SubjectPrincipal(IPrincipal):
    """A :class:`~cbra.types.IPrincipal` implementation that simply
    references a subject by its identifier.
    """
    sub: int | str

    def is_authenticated(self) -> bool:
        return True