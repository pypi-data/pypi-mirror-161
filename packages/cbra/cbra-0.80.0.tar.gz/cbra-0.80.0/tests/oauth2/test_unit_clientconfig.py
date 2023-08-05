# pylint: skip-file
# type: ignore
import pytest
import pytest_asyncio
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKey
from ckms.types import JSONWebToken
from cryptography.hazmat.primitives.asymmetric import ed448

from cbra.ext import oauth2


@pytest.fixture(scope='session')
def keychain() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def private_key():
    return ed448.Ed448PrivateKey.generate()


@pytest_asyncio.fixture(scope='session')
async def jwk(keychain, private_key):
    keychain.configure({
        'sig': {
            'provider': "local",
            'key': {'content': private_key},
            'alg': "EdDSA",
            'kty': "OKP",
            'use': 'sig',
            'crv': 'Ed448'
        }
    })
    await keychain
    spec = keychain.get('sig')
    return spec.as_jwk()


@pytest.fixture
def codec(keychain):
    return PayloadCodec(
        verifier=keychain,
        signer=keychain
    )


def test_allowed_redirect_urls_are_parsed_from_strings():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.com"]
    )
    assert isinstance(config.redirect_uris, list)
    assert isinstance(config.redirect_uris[0], oauth2.types.RedirectURL)
    assert str(config.redirect_uris[0]) == "https://www.example.com"


def test_default_redirect_url_is_parsed_from_string():
    config = oauth2.ClientConfig(
        client_id="foo",
        default_redirect_url="https://www.example.com"
    )
    assert isinstance(config.default_redirect_url, oauth2.types.RedirectURL)


def test_can_redirect_accepts_only_whitelisted_urls():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.com"]
    )
    assert config.can_redirect("https://www.example.com")
    assert not config.can_redirect("https://www.example.net")


def test_can_redirect_accepts_default():
    config = oauth2.ClientConfig(
        client_id="foo",
        default_redirect_url="https://www.example.com"
    )
    assert config.can_redirect("https://www.example.com")
    assert not config.can_redirect("https://www.example.net")


def test_get_redirect_url_with_whitelisted_url():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.com"]
    )
    url = config.get_redirect_url("https://www.example.com")
    assert url == "https://www.example.com"


def test_get_redirect_url_with_non_whitelisted_url():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.com"]
    )
    with pytest.raises(oauth2.exceptions.RedirectForbidden):
        url = config.get_redirect_url("https://www.example.net")


def test_default_redirect_is_added_to_allowed_redirect_urls():
    config = oauth2.ClientConfig(
        client_id="foo",
        default_redirect_url="https://www.example.com"
    )
    assert "https://www.example.com" in config.redirect_uris


def test_get_redirect_url_with_none_returns_default():
    config = oauth2.ClientConfig(
        client_id="foo",
        default_redirect_url="https://www.example.com"
    )
    url = config.get_redirect_url(None)


def test_get_redirect_url_with_whitelisted_str_returns_redirect():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.net"],
        default_redirect_url="https://www.example.com"
    )
    url = config.get_redirect_url("https://www.example.net")
    assert url == "https://www.example.net"


def test_get_redirect_url_with_whitelisted_redirecturi_returns_redirect():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.net"],
        default_redirect_url="https://www.example.com"
    )
    url = config.get_redirect_url(oauth2.types.RedirectURL.validate("https://www.example.net"))
    assert url == "https://www.example.net"


def test_get_redirect_url_with_none_and_no_default():
    config = oauth2.ClientConfig(
        client_id="foo",
        redirect_uris=["https://www.example.com", "https://www.example.localhost"]
    )
    with pytest.raises(oauth2.exceptions.MissingRedirectURL):
        config.get_redirect_url(None)


@pytest.mark.asyncio
async def test_verify_valid_jwt_with_client(jwk, codec):
    config = oauth2.ClientConfig(
        client_id="foo",
        keys=[jwk]
    )
    jws = await codec.encode(
        JSONWebToken(foo=1),
        signers=['sig']
    )
    assert await config.verify_jwt(jws.encode(), None)


@pytest.mark.asyncio
async def test_verify_invalid_jwt_with_client_raises(jwk, codec):
    config = oauth2.ClientConfig(
        client_id="foo",
        keys=[jwk]
    )
    jws = await codec.encode(
        JSONWebToken(foo=1),
        signers=['sig']
    )
    with pytest.raises(ValueError):
        assert not await config.verify_jwt(jws + 'd', None)

