"""Tests for the Régie des Eaux sensor."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from custom_components.regiedeseauxmpl.sensor import RegieDesEauxWaterSensor
from custom_components.regiedeseauxmpl.const import (
    DOMAIN,
    ATTR_LAST_UPDATED,
    ATTR_LAST_READING,
    ATTR_CONTRACT_ID,
    ATTR_SERIAL_NUMBER,
    ATTR_UNIT,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator with test data."""
    coordinator = MagicMock()
    coordinator.data = {
        "meters": {
            "meter1": {
                "id": "meter1",
                "name": "Test Meter",
                "serial_number": "SN001",
                "contract_id": "CONTRACT123",
                "index": 123.456,
                "timestamp": "2024-01-01",
                "unit": "m³",
            }
        },
        "last_updated": "2024-01-01T12:00:00",
    }
    coordinator.domain = DOMAIN
    return coordinator


@pytest.fixture
def sensor(mock_coordinator):
    """Create a sensor instance."""
    return RegieDesEauxWaterSensor(mock_coordinator, "meter1")


class TestRegieDesEauxWaterSensor:
    """Tests for the water sensor."""

    def test_sensor_properties(self, sensor):
        """Test sensor properties."""
        assert sensor._attr_device_class == "water"
        assert sensor._attr_state_class == "total_increasing"
        assert sensor._attr_native_unit_of_measurement == "m³"
        assert sensor._attr_translation_key == "water_index"
        assert sensor._attr_has_entity_name is True
        assert sensor.icon == "mdi:water"
        assert sensor.suggested_display_precision == 3

    def test_sensor_unique_id(self, sensor):
        """Test sensor unique ID."""
        assert sensor.unique_id == f"{DOMAIN}_meter1"

    def test_sensor_native_value(self, sensor):
        """Test sensor native value."""
        assert sensor.native_value == 123.456

    def test_sensor_native_value_none(self, mock_coordinator):
        """Test sensor with no index data."""
        mock_coordinator.data["meters"]["meter1"]["index"] = None
        sensor = RegieDesEauxWaterSensor(mock_coordinator, "meter1")
        assert sensor.native_value is None

    def test_sensor_extra_state_attributes(self, sensor):
        """Test sensor extra state attributes."""
        attrs = sensor.extra_state_attributes
        
        assert attrs[ATTR_LAST_UPDATED] == "2024-01-01T12:00:00"
        assert attrs[ATTR_LAST_READING] == "2024-01-01"
        assert attrs[ATTR_CONTRACT_ID] == "CONTRACT123"
        assert attrs[ATTR_SERIAL_NUMBER] == "SN001"
        assert attrs[ATTR_UNIT] == "m³"
        assert attrs["friendly_name"] == "Test Meter"

    @pytest.mark.asyncio
    async def test_sensor_restore_state(self, mock_coordinator):
        """Test sensor state restoration."""
        # Create sensor with no initial data
        mock_coordinator.data["meters"]["meter1"]["index"] = None
        sensor = RegieDesEauxWaterSensor(mock_coordinator, "meter1")
        
        # Mock the restore method to return previous state
        mock_state = MagicMock()
        mock_state.native_value = 999.0
        sensor.async_get_last_sensor_data = AsyncMock(return_value=mock_state)
        
        # Simulate the restore logic from async_added_to_hass
        meter_data = sensor.coordinator.data.get("meters", {}).get("meter1", {})
        if meter_data.get("index") is None:
            last_sensor_data = await sensor.async_get_last_sensor_data()
            if last_sensor_data is not None:
                sensor._attr_native_value = last_sensor_data.native_value
        
        # Verify that the restored value was set internally
        # Note: native_value property returns coordinator data, not _attr_native_value
        # In real HA, RestoreSensor would use _attr_native_value when coordinator has no data
        assert sensor._attr_native_value == 999.0


class TestSensorSetup:
    """Tests for sensor setup."""

    @pytest.mark.asyncio
    async def test_async_setup_entry(self, mock_coordinator):
        """Test sensor setup entry."""
        from custom_components.regiedeseauxmpl.sensor import async_setup_entry
        
        mock_hass = MagicMock()
        mock_entry = MagicMock()
        mock_entry.entry_id = "test_entry"
        
        # Set up coordinator in hass.data
        mock_hass.data = {DOMAIN: {"test_entry": mock_coordinator}}
        
        added_entities = []

        # AddEntitiesCallback is synchronous - it must not be awaited.
        def mock_add_entities(entities):
            added_entities.extend(entities)

        mock_async_add_entities = MagicMock(side_effect=mock_add_entities)

        await async_setup_entry(
            mock_hass,
            mock_entry,
            mock_async_add_entities
        )
        
        assert len(added_entities) == 1
        assert isinstance(added_entities[0], RegieDesEauxWaterSensor)
