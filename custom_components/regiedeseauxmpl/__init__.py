"""Integration Régie des Eaux Montpellier."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RegieDesEauxAPI
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    LOGGER,
    PLATFORMS,
)
from .coordinator import RegieDesEauxCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Régie des Eaux Montpellier from a config entry."""
    session = async_get_clientsession(hass)
    
    # Get scan interval from options or config, with fallback to default.
    # The config_flow stores it as a string (seconds) because vol.In keys are
    # strings; cast to int here so the coordinator sees a plain number.
    raw_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL),
    )
    scan_interval = int(raw_interval) if raw_interval is not None else None

    api = RegieDesEauxAPI(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    coordinator = RegieDesEauxCoordinator(hass, api, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_refresh(call):
        """Handle service call to refresh meters."""
        await coordinator.async_request_refresh()
    
    hass.services.async_register(DOMAIN, "refresh_meters", handle_refresh)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister services
        if hass.services.has_service(DOMAIN, "refresh_meters"):
            hass.services.async_remove(DOMAIN, "refresh_meters")

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry format to new one."""
    # Migration from version 0 (no scan_interval) to version 1 (with scan_interval)
    if entry.version < 1:
        LOGGER.debug("Migrating config entry from version %s to 1", entry.version)
        
        # No migration needed for now, just increment version
        hass.config_entries.async_update_entry(
            entry,
            version=1,
        )
    
    return True
