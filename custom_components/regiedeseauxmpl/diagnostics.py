"""Diagnostics for Régie des Eaux Montpellier integration."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {"password"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    data = {
        "entry": {
            "id": entry.entry_id,
            "title": entry.title,
            "username": entry.data.get("username"),
        },
        "meters": {},
    }
    
    # Get coordinator data
    if coordinator and coordinator.data:
        for meter_id, meter_data in coordinator.data.get("meters", {}).items():
            data["meters"][meter_id] = {
                "name": meter_data.get("name"),
                "serial_number": meter_data.get("serial_number"),
                "contract_id": meter_data.get("contract_id"),
                "index": meter_data.get("index"),
                "timestamp": meter_data.get("timestamp"),
            }
    
    # Get API connection status
    try:
        api = coordinator.api
        data["api"] = {
            "is_authenticated": api._is_authenticated,
            "has_app_token": api._app_token is not None,
            "has_auth_token": api._auth_token is not None,
        }
    except Exception:
        data["api"] = {"error": "Unable to get API status"}
    
    return async_redact_data(data, TO_REDACT)


async def async_get_config_entries_diagnostics(
    hass: HomeAssistant, entries: list[ConfigEntry]
) -> dict:
    """Return diagnostics for all config entries."""
    return {
        "entries": [
            await async_get_config_entry_diagnostics(hass, entry)
            for entry in entries
        ]
    }
