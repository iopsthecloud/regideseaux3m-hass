"""DataUpdateCoordinator for Régie des Eaux Montpellier."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
)
from .api import RegieDesEauxAPI
from .exceptions import RegieDesEauxError


class RegieDesEauxCoordinator(DataUpdateCoordinator[dict]):
    """Data update coordinator for Régie des Eaux Montpellier."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: RegieDesEauxAPI,
        update_interval: int | float | timedelta | None = None,
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: HomeAssistant instance
            api: API client instance
            update_interval: Update interval in seconds, or timedelta object.
                            If None, uses DEFAULT_SCAN_INTERVAL.
        """
        # Accept seconds as int/float/str (str comes from config_flow vol.In keys).
        if update_interval is None:
            update_interval = DEFAULT_SCAN_INTERVAL
        elif isinstance(update_interval, str):
            update_interval = timedelta(seconds=int(update_interval))
        elif isinstance(update_interval, (int, float)):
            update_interval = timedelta(seconds=update_interval)
        
        # Enforce min/max limits
        if update_interval < MIN_SCAN_INTERVAL:
            update_interval = MIN_SCAN_INTERVAL
            LOGGER.warning(
                "Update interval %s is less than minimum (%s), using minimum",
                update_interval,
                MIN_SCAN_INTERVAL
            )
        elif update_interval > MAX_SCAN_INTERVAL:
            update_interval = MAX_SCAN_INTERVAL
            LOGGER.warning(
                "Update interval %s exceeds maximum (%s), using maximum",
                update_interval,
                MAX_SCAN_INTERVAL
            )
        
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        try:
            meters = await self.api.async_get_meters()
            data = {"meters": {}, "last_updated": None}
            
            for meter in meters:
                meter_id = meter["id"]
                index_info = await self.api.async_get_meter_index(meter_id)
                data["meters"][meter_id] = {
                    **meter,
                    **index_info,
                }
            
            data["last_updated"] = dt_util.now().isoformat()
            return data
            
        except RegieDesEauxError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
