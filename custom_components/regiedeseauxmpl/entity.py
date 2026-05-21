"""Base entity for Régie des Eaux Montpellier."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import RegieDesEauxCoordinator


def _short_name(full_name: str) -> str:
    """Extract the meter's short name from the API label.

    Example: "Eau potable – 15 RUE DES POMMETIERS 34670 SAINT BRES" → "Eau potable".
    Falls back to the full string if no separator is found.
    """
    for sep in (" – ", " - "):
        if sep in full_name:
            return full_name.split(sep, 1)[0].strip()
    return full_name.strip()


class RegieDesEauxEntity(CoordinatorEntity[RegieDesEauxCoordinator]):
    """Base entity for Régie des Eaux Montpellier."""

    # has_entity_name=True + _attr_name=None → friendly_name = device.name.
    # We put the short label on the device and the address in `model`, so the
    # entity reads "Eau potable" while the device page still shows the address.
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: RegieDesEauxCoordinator, meter_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._meter_id = meter_id
        meter_data = coordinator.data["meters"][meter_id]

        short = _short_name(meter_data["name"])
        serial = meter_data.get("serial_number") or meter_id

        self._attr_unique_id = f"{DOMAIN}_{meter_id}"
        # Drives the default entity_id on first creation: e.g. "sensor.regiedeseauxmpl_eau_potable_i23ia727517"
        self._attr_suggested_object_id = f"{DOMAIN}_{slugify(short)}_{serial.lower()}"
        self._attr_entity_category = None  # Ensure entities are not diagnostic/config

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, meter_id)},
            name=short,
            manufacturer="Régie des Eaux Montpellier 3M",
            model=f"Compteur {meter_data.get('contract_id', 'N/A')}",
            serial_number=serial,
            via_device=(DOMAIN, coordinator.config_entry.entry_id),
        )
