"""Integration tests: config entry setup on a real Home Assistant core."""

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from custom_components.regiedeseauxmpl.const import DOMAIN


async def test_setup_creates_device_and_sensor(hass, mock_api, config_entry):
    """The entry loads and registers one device + one water sensor per meter."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED

    devices = dr.async_entries_for_config_entry(
        dr.async_get(hass), config_entry.entry_id
    )
    assert len(devices) == 1
    device = devices[0]
    assert (DOMAIN, "C0001") in device.identifiers
    assert device.name == "Eau potable"
    assert device.serial_number == "I23IA727517"
    assert device.via_device_id is None

    entities = er.async_entries_for_config_entry(
        er.async_get(hass), config_entry.entry_id
    )
    assert len(entities) == 1
    state = hass.states.get(entities[0].entity_id)
    assert state is not None
    assert float(state.state) == 123.456


async def test_setup_does_not_use_deprecated_device_info(
    hass, mock_api, config_entry, caplog
):
    """No deprecated DeviceInfo parameter is passed to the device registry.

    `via_device` is deprecated since HA 2026.8 (removed in 2027.8). When HA
    attributes the call to a core integration (e.g. setup triggered from the UI
    config flow, reported as integration 'config' in issue #1) it raises a
    RuntimeError and the sensors are never created.
    """
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert "deprecated" not in caplog.text
    assert "via_device" not in caplog.text


async def test_setup_from_ui_config_flow(hass, hass_client, mock_api):
    """Adding the integration from the UI creates the sensor (issue #1).

    Goes through the HTTP config-flow API like the frontend does, so the setup
    runs under the core `config` integration's request handler.
    """
    assert await async_setup_component(hass, "config", {})
    client = await hass_client()

    with patch(
        "custom_components.regiedeseauxmpl.api.RegieDesEauxAPI.async_authenticate",
        new=AsyncMock(return_value=True),
    ):
        resp = await client.post(
            "/api/config/config_entries/flow", json={"handler": DOMAIN}
        )
        assert resp.status == 200
        flow = await resp.json()
        resp = await client.post(
            f"/api/config/config_entries/flow/{flow['flow_id']}",
            json={"username": "test@example.com", "password": "secret"},
        )
        assert resp.status == 200, await resp.text()
        result = await resp.json()
    await hass.async_block_till_done()

    assert result["type"] == "create_entry"
    entry = hass.config_entries.async_get_entry(result["result"]["entry_id"])
    assert entry.state is ConfigEntryState.LOADED
    assert len(er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)) == 1
