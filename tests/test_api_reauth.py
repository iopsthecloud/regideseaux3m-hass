"""Tests for token-expiry handling in the API client.

The server-side ``tokenAuthentique`` expires within the polling interval.
These tests verify the API re-authenticates and retries instead of failing
permanently with a 401.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.regiedeseauxmpl.api import RegieDesEauxAPI
from custom_components.regiedeseauxmpl.exceptions import InvalidAuth


class _Resp:
    """Minimal stand-in for a curl_cffi response."""

    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.content = b"{}"
        self.text = ""

    def json(self):
        return self._payload


def _make_api():
    """Build an API client that already holds a (now stale) auth token."""
    api = RegieDesEauxAPI(MagicMock(), "user@example.com", "pwd")
    api._is_authenticated = True
    api._auth_token = "stale-token"
    return api


async def test_get_meters_reauthenticates_on_401():
    """A 401 on the data call triggers exactly one re-auth + retry, then succeeds."""
    api = _make_api()

    contracts = {"resultats": [
        {"numeroContrat": "C1", "numeroPhysiqueAppareil": "SN1", "libelle": "Eau potable"}
    ]}
    session = MagicMock()
    session.get = AsyncMock(side_effect=[_Resp(401), _Resp(200, contracts)])
    api._curl_session = session

    auth_calls = []

    async def fake_auth():
        auth_calls.append(1)
        api._is_authenticated = True
        api._auth_token = "fresh-token"
        return True

    api.async_authenticate = fake_auth

    meters = await api.async_get_meters()

    assert len(auth_calls) == 1, "expected exactly one re-authentication"
    assert session.get.call_count == 2, "expected the data call to be retried once"
    assert meters[0]["id"] == "C1"


async def test_get_meters_raises_invalid_auth_when_token_still_rejected():
    """If the token is still rejected after re-auth, surface InvalidAuth."""
    api = _make_api()

    session = MagicMock()
    session.get = AsyncMock(side_effect=[_Resp(401), _Resp(401)])
    api._curl_session = session

    async def fake_auth():
        api._is_authenticated = True
        api._auth_token = "fresh-but-rejected"
        return True

    api.async_authenticate = fake_auth

    with pytest.raises(InvalidAuth):
        await api.async_get_meters()


async def test_get_meter_index_reauthenticates_on_401():
    """The index endpoint also re-authenticates on a stale token."""
    api = _make_api()

    chart = {"consommations": [
        {"typeAgregat": "Réel", "valeurIndex": 25834, "dateReleve": "2026-05-21"}
    ]}
    session = MagicMock()
    session.get = AsyncMock(side_effect=[_Resp(401), _Resp(200, chart)])
    api._curl_session = session

    async def fake_auth():
        api._is_authenticated = True
        api._auth_token = "fresh-token"
        return True

    api.async_authenticate = fake_auth

    result = await api.async_get_meter_index("C1")

    assert session.get.call_count == 2
    assert result["index"] == 25.834
