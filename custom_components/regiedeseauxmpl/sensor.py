"""Sensor platform for Régie des Eaux Montpellier."""
from __future__ import annotations

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ATTR_LAST_UPDATED,
    ATTR_LAST_READING,
    ATTR_CONTRACT_ID,
    ATTR_SERIAL_NUMBER,
    ATTR_UNIT,
)
from .coordinator import RegieDesEauxCoordinator
from .entity import RegieDesEauxEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: RegieDesEauxCoordinator = hass.data[DOMAIN][entry.entry_id]

    await async_add_entities(
        RegieDesEauxWaterSensor(coordinator, meter_id)
        for meter_id in coordinator.data["meters"]
    )


class RegieDesEauxWaterSensor(RegieDesEauxEntity, RestoreSensor):
    """Sensor for water meter index.

    Uses RestoreSensor so the last known value survives HA restarts even when
    the API is temporarily unreachable.
    """

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_translation_key = "water_index"

    async def async_added_to_hass(self) -> None:
        """Restore last known state on startup."""
        await super().async_added_to_hass()

        # Only restore if coordinator has no fresh value yet
        meter_data = self.coordinator.data.get("meters", {}).get(self._meter_id, {})
        if meter_data.get("index") is None:
            last_sensor_data = await self.async_get_last_sensor_data()
            if last_sensor_data is not None:
                self._attr_native_value = last_sensor_data.native_value
                LOGGER.debug(
                    "Restored %s state: %s",
                    self.entity_id,
                    self._attr_native_value,
                )

    @property
    def native_value(self) -> float | None:
        """Return the current meter index in m³."""
        return self.coordinator.data["meters"][self._meter_id].get("index")

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        meter_data = self.coordinator.data["meters"][self._meter_id]
        
        attributes = {
            ATTR_LAST_UPDATED: self.coordinator.data.get("last_updated"),
            ATTR_LAST_READING: meter_data.get("timestamp"),
            ATTR_CONTRACT_ID: meter_data.get("contract_id"),
            ATTR_SERIAL_NUMBER: meter_data.get("serial_number"),
            ATTR_UNIT: meter_data.get("unit", "m³"),
        }
        
        # Add friendly name as attribute
        if meter_data.get("name"):
            attributes["friendly_name"] = meter_data["name"]
        
        return attributes

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        return "mdi:water"

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested display precision."""
        # 3 decimal places for cubic meters (0.001 = 1 liter)
        return 3
