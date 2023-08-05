# pylint: skip-file
# type: ignore
import pytest

from cbra.ext import oauth2


def test_redirect_uri_must_be_https():
    with pytest.raises(oauth2.exceptions.RedirectForbidden):
        oauth2.types.RedirectURL.validate("http://example.com")


def test_redirect_uri_must_have_netloc():
    with pytest.raises(oauth2.exceptions.RedirectForbidden):
        oauth2.types.RedirectURL.validate("http:///foo")


def test_redirect_uri_can_be_none():
    url = oauth2.types.RedirectURL.validate(None)
    assert not url


def test_redirect_uri_is_none_is_casted_to_empty_string():
    url = oauth2.types.RedirectURL.validate(None)
    assert str(url) == ''


def test_redirect_uri_is_none_raises_missing_redirect_wtihout_default():
    url = oauth2.types.RedirectURL.validate(None)
    with pytest.raises(oauth2.exceptions.MissingRedirectURL):
        url.authorize()


def test_redirect_uri_discovers_params():
    url = oauth2.types.RedirectURL.validate("https://example.com?foo=baz")
    assert url.params


def test_redirect_uri_authorize_adds_param():
    url = oauth2.types.RedirectURL.validate("https://example.com")
    assert url.authorize(foo=1) == "https://example.com?foo=1"


def test_redirect_uri_authorize_adds_param_array():
    url = oauth2.types.RedirectURL.validate("https://example.com")
    assert url.authorize(foo=[1,2]) == "https://example.com?foo=1&foo=2"


def test_redirect_uri_authorize_retains_param():
    url = oauth2.types.RedirectURL.validate("https://example.com?bar=1")
    assert url.authorize() == "https://example.com?bar=1"


def test_redirect_uri_authorize_retains_param():
    url = oauth2.types.RedirectURL.validate("https://example.com?bar=1&bar=2")
    assert url.authorize() == "https://example.com?bar=1&bar=2"


def test_redirect_uri_authorize_overwrites_param():
    url = oauth2.types.RedirectURL.validate("https://example.com?bar=1")
    assert url.authorize(bar=2) == "https://example.com?bar=2"


def test_redirect_uri_valid():
    url = oauth2.types.RedirectURL.validate("https://example.com")
    assert url


def test_redirect_uri_valid_to_string():
    url = oauth2.types.RedirectURL.validate("https://example.com")
    assert str(url) == "https://example.com"


def test_redirect_uri_raises_redirectforbidden_with_no_netloc():
    with pytest.raises(oauth2.exceptions.RedirectForbidden):
        url = oauth2.types.RedirectURL.validate("https:/example.com")