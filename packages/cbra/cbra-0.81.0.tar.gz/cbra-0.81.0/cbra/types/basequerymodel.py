"""Declares :class:`BaseQueryModel`."""
import dataclasses


class BaseQueryModel:

    def dict(self):
        return dataclasses.asdict(self)