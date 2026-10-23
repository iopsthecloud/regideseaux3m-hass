"""Fixtures for integration tests against a real Home Assistant core.

Unlike tests/ (which mocks the homeassistant package entirely), these tests use
pytest-homeassistant-custom-component, so the real device/entity registries run.
They must be run in their own pytest session: see `make test-ha`.
"""

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.regiedeseauxmpl.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)

METERS = [
    {
        "id": "C0001",
        "name": "Eau potable – 1 RUE DU TEST 34000 MONTPELLIER",
        "serial_number": "I23IA727517",
        "unit": "m³",
        "contract_id": "C0001",
    }
]
INDEX = {"index": 123.456, "timestamp": "2026-10-20T00:00:00"}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ in every test."""
    return


@pytest.fixture
def mock_api():
    """Patch the API client so no network call is made."""
    with (
        patch(
            "custom_components.regiedeseauxmpl.api.RegieDesEauxAPI.async_get_meters",
            new=AsyncMock(return_value=METERS),
        ),
        patch(
            "custom_components.regiedeseauxmpl.api.RegieDesEauxAPI.async_get_meter_index",
            new=AsyncMock(return_value=INDEX),
        ),
    ):
        yield


@pytest.fixture
def config_entry():
    """Return a config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        version=1,
        title="test@example.com",
        data={CONF_USERNAME: "test@example.com", CONF_PASSWORD: "secret"},
    )
