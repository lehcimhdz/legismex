"""Unit tests for ``legismex.exceptions.wrap_httpx_errors``."""

import httpx
import pytest

from legismex import (
    APIResponseError,
    LegismexConnectionError,
    LegismexError,
    wrap_httpx_errors,
)


def _fake_request(url: str = "https://example.gob.mx/x") -> httpx.Request:
    return httpx.Request("GET", url)


def test_passthrough_on_success():
    with wrap_httpx_errors():
        result = 42
    assert result == 42


def test_http_status_error_becomes_api_response_error():
    req = _fake_request()
    resp = httpx.Response(500, request=req)
    with pytest.raises(APIResponseError) as exc_info:
        with wrap_httpx_errors():
            raise httpx.HTTPStatusError("boom", request=req, response=resp)

    assert "HTTP 500" in str(exc_info.value)
    assert isinstance(exc_info.value, LegismexError)
    assert isinstance(exc_info.value.__cause__, httpx.HTTPStatusError)


def test_connect_timeout_becomes_connection_error():
    req = _fake_request("https://example.gob.mx/slow")
    with pytest.raises(LegismexConnectionError) as exc_info:
        with wrap_httpx_errors():
            raise httpx.ConnectTimeout("timed out", request=req)

    assert "ConnectTimeout" in str(exc_info.value)
    assert isinstance(exc_info.value, LegismexError)
    assert isinstance(exc_info.value.__cause__, httpx.ConnectTimeout)


def test_explicit_url_override_is_used_in_message():
    req = _fake_request("https://leaked.internal/secret")
    resp = httpx.Response(404, request=req)
    override = "https://public.gob.mx/path"
    with pytest.raises(APIResponseError) as exc_info:
        with wrap_httpx_errors(override):
            raise httpx.HTTPStatusError("not found", request=req, response=resp)

    assert override in str(exc_info.value)
    assert "leaked.internal" not in str(exc_info.value)


def test_unrelated_exception_is_not_swallowed():
    with pytest.raises(ValueError):
        with wrap_httpx_errors():
            raise ValueError("unrelated")
