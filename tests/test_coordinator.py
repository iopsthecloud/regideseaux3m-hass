"""Tests for the Régie des Eaux coordinator."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta

from custom_components.regiedeseauxmpl.coordinator import RegieDesEauxCoordinator
from custom_components.regiedeseauxmpl.const import DOMAIN, DEFAULT_SCAN_INTERVAL


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.helpers = MagicMock()
    hass.helpers.now = MagicMock(return_value=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")))
    return hass


@pytest.fixture
def mock_api():
    """Create a mock API with test data."""
    api = MagicMock()
    api.async_get_meters = AsyncMock(return_value=[
        {"id": "meter1", "name": "Compteur 1", "serial_number": "SN001"},
        {"id": "meter2", "name": "Compteur 2", "serial_number": "SN002"},
    ])
    api.async_get_meter_index = AsyncMock(return_value={"index": 123.456, "timestamp": "2024-01-01"})
    return api


@pytest.mark.asyncio
async def test_coordinator_init_default_interval(mock_hass, mock_api):
    """Test coordinator initialization with default interval."""
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api)
    
    assert coordinator.name == DOMAIN
    assert coordinator.update_interval == DEFAULT_SCAN_INTERVAL
    assert coordinator.api == mock_api


@pytest.mark.asyncio
async def test_coordinator_init_custom_interval(mock_hass, mock_api):
    """Test coordinator initialization with custom interval."""
    custom_interval = timedelta(hours=1)
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api, custom_interval)
    
    assert coordinator.update_interval == custom_interval


@pytest.mark.asyncio
async def test_coordinator_init_numeric_interval(mock_hass, mock_api):
    """Test coordinator initialization with numeric interval (seconds)."""
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api, 3600)  # 1 hour in seconds
    
    assert coordinator.update_interval == timedelta(seconds=3600)


@pytest.mark.asyncio
async def test_coordinator_min_interval(mock_hass, mock_api):
    """Test that coordinator respects minimum interval."""
    # Try to set interval below minimum (30 minutes)
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api, timedelta(minutes=10))
    
    # Should be clamped to minimum (30 minutes)
    from custom_components.regiedeseauxmpl.const import MIN_SCAN_INTERVAL
    assert coordinator.update_interval == MIN_SCAN_INTERVAL


@pytest.mark.asyncio
async def test_coordinator_max_interval(mock_hass, mock_api):
    """Test that coordinator respects maximum interval."""
    # Try to set interval above maximum (24 hours)
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api, timedelta(hours=48))
    
    # Should be clamped to maximum (24 hours)
    from custom_components.regiedeseauxmpl.const import MAX_SCAN_INTERVAL
    assert coordinator.update_interval == MAX_SCAN_INTERVAL


@pytest.mark.asyncio
async def test_coordinator_update_data_success(mock_hass, mock_api):
    """Test successful data update."""
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api)
    
    # Mock the data
    mock_api.async_get_meters = AsyncMock(return_value=[
        {"id": "meter1", "name": "Test Meter"},
    ])
    mock_api.async_get_meter_index = AsyncMock(return_value={"index": 100.5, "timestamp": "2024-01-01"})
    
    data = await coordinator._async_update_data()
    
    assert "meters" in data
    assert "meter1" in data["meters"]
    assert data["meters"]["meter1"]["index"] == 100.5
    assert data["meters"]["meter1"]["timestamp"] == "2024-01-01"
    assert "last_updated" in data


@pytest.mark.asyncio
async def test_coordinator_update_data_with_error(mock_hass):
    """Test data update with API error."""
    from custom_components.regiedeseauxmpl.exceptions import RegieDesEauxError
    
    mock_api = MagicMock()
    mock_api.async_get_meters = AsyncMock(side_effect=RegieDesEauxError("API Error"))
    
    coordinator = RegieDesEauxCoordinator(mock_hass, mock_api)
    
    with pytest.raises(Exception) as exc_info:
        await coordinator._async_update_data()
    
    assert "API Error" in str(exc_info.value)
