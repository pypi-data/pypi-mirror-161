"""Declares :class:`Configurable`."""
import importlib
import types
from typing import Any


class Configurable:
    __module__: str = 'cbra.ext.oauth2.types'
    kwargs_name: str = 'clients'
    settings_key: str = 'OAUTH_CLIENTS'

    @classmethod
    def configure(cls, **attrs: Any) -> type['Configurable']:
        return type(cls.__name__, (cls,), attrs)

    @classmethod
    def fromsettings(cls, settings: types.ModuleType) -> type['Configurable']:
        params = getattr(settings, cls.settings_key)
        if isinstance(params, str):
            params = {'class': params}
        module, symbol = str.rsplit(params.pop('class'), '.', 1)
        Configurable = getattr(importlib.import_module(module), symbol)
        return Configurable.configure(**params)