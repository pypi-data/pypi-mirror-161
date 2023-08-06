# pylint: skip-file
# type: ignore
import types

import pytest

from cbra.ext.oauth2.types import IClientRepository


@pytest.fixture
def settings():
    settings = types.ModuleType('settings')
    setattr(settings, 'OAUTH_CLIENTS', None)
    return settings


def test_configure_from_string(settings: types.ModuleType):
    settings.OAUTH_CLIENTS = 'cbra.ext.oauth2.SettingsClientRepository'
    ClientRepository = IClientRepository.fromsettings(settings)


def test_configure_from_string_with_attrs(settings: types.ModuleType):
    settings.OAUTH_CLIENTS = {
        'class': 'cbra.ext.oauth2.SettingsClientRepository',
        'foo': 'bar'
    }
    ClientRepository = IClientRepository.fromsettings(settings)
    assert hasattr(ClientRepository, 'foo')
    assert ClientRepository.foo == 'bar'