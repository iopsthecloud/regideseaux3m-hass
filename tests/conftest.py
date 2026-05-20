"""Pytest fixtures for Régie des Eaux Montpellier integration.

This file provides fixtures and mocks for testing the integration
without requiring a running Home Assistant instance.

The mocks are set up BEFORE any imports from custom_components,
to ensure all Home Assistant dependencies are properly mocked.
"""

import sys
from typing import Generic, TypeVar, Any
from unittest.mock import MagicMock, AsyncMock

# =============================================================================
# MOCK ALL HOME ASSISTANT MODULES BEFORE ANY IMPORTS
# This is critical to prevent ImportError when importing custom_components
# =============================================================================

# List of ALL Home Assistant modules that might be imported
HA_MODULES = [
    # Base
    "homeassistant",
    
    # Exceptions
    "homeassistant.exceptions",
    
    # Core
    "homeassistant.core",
    "homeassistant.config_entries",
    "homeassistant.const",
    
    # Helpers
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.service",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity_registry",
    "homeassistant.helpers.config_entry_flow",
    "homeassistant.helpers.data_entry_flow",
    "homeassistant.helpers.selector",
    "homeassistant.helpers.template",
    "homeassistant.helpers.storage",
    "homeassistant.helpers.network",
    "homeassistant.helpers.json",
    "homeassistant.helpers.script",
    
    # Components
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.components.diagnostics",
    
    # Util
    "homeassistant.util",
    "homeassistant.util.dt",
    "homeassistant.util.yaml",
    "homeassistant.util.location",
    "homeassistant.util.color",
]


class MockModule:
    """Dynamic mock module that creates MagicMock attributes on access."""
    def __getattr__(self, name: str) -> Any:
        return MagicMock()


# Install mocks for all HA modules
for mod_name in HA_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MockModule()


T = TypeVar('T')


# =============================================================================
# DEFINE SPECIFIC CLASSES WITH PROPER TYPE HINTS SUPPORT
# =============================================================================

class HomeAssistantError(Exception):
    """Base Home Assistant error."""
    pass


# Mock ConfigEntry
class MockConfigEntry:
    """Mock ConfigEntry."""
    def __init__(self, entry_id: str = "test", title: str = "Test", data: dict = None, options: dict = None):
        self.entry_id = entry_id
        self.title = title
        self.data = data or {}
        self.options = options or {}
        self.domain = "regiedeseauxmpl"
        self.version = 1
        self.source = "user"


# Mock Platform constants
class MockPlatform:
    """Mock Platform constants."""
    SENSOR = "sensor"
    SWITCH = "switch"
    LIGHT = "light"
    BINARY_SENSOR = "binary_sensor"


# Mock DeviceInfo
class MockDeviceInfo:
    """Mock DeviceInfo."""
    def __init__(self, **kwargs):
        self.identifiers = kwargs.get("identifiers", {})
        self.name = kwargs.get("name", "")
        self.manufacturer = kwargs.get("manufacturer", "")
        self.model = kwargs.get("model", "")
        self.serial_number = kwargs.get("serial_number", "")


# Mock UpdateFailed exception
class MockUpdateFailed(Exception):
    """Mock UpdateFailed."""
    pass


# Mock DataUpdateCoordinator with Generic support
class MockDataUpdateCoordinator(Generic[T]):
    """Mock DataUpdateCoordinator with Generic support."""
    
    def __init__(self, hass, logger, name, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data: dict = {}
        self._update_method = None
    
    async def async_config_entry_first_refresh(self):
        """First refresh."""
        if self._update_method:
            self.data = await self._update_method()
    
    async def async_request_refresh(self):
        """Request refresh."""
        if self._update_method:
            self.data = await self._update_method()
    
    async def _async_update_data(self) -> dict:
        """Update data (to be overridden)."""
        return {}


# Mock CoordinatorEntity with Generic support
class MockCoordinatorEntity(Generic[T]):
    """Mock CoordinatorEntity with Generic support."""
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_has_entity_name = True
        self._attr_unique_id = "test_entity"
    
    async def async_added_to_hass(self):
        """Entity added to HA."""
        pass
    
    async def async_update(self):
        """Update entity."""
        pass
    
    @property
    def should_poll(self):
        return False
    
    @property
    def is_on(self):
        return False
    
    async def async_turn_on(self, **kwargs):
        pass
    
    async def async_turn_off(self, **kwargs):
        pass


# Mock dt_util
class MockDtUtil:
    """Mock for homeassistant.util.dt."""
    @staticmethod
    def now():
        """Return current datetime in UTC."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)
    
    @staticmethod
    def as_utc(*args, **kwargs):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)
    
    @staticmethod
    def as_local(*args, **kwargs):
        from datetime import datetime
        return datetime.now()
    
    @staticmethod
    def parse_datetime(*args, **kwargs):
        from datetime import datetime
        if args and isinstance(args[0], str):
            return datetime.fromisoformat(args[0].replace('Z', '+00:00'))
        return datetime.now()
    
    @staticmethod
    def parse_date(*args, **kwargs):
        from datetime import date
        return date.today()


# Mock async_get_clientsession
async def mock_async_get_clientsession(hass):
    """Mock async_get_clientsession."""
    import aiohttp
    return aiohttp.ClientSession()


# Mock CONN_CLASS
class MockCONNCLASS:
    CLOUD_POLL = "cloud_polling"
    LOCAL_POLL = "local_polling"


# Sensor classes
class MockSensorDeviceClass:
    WATER = "water"
    ENERGY = "energy"


class MockSensorStateClass:
    TOTAL_INCREASING = "total_increasing"
    TOTAL = "total"


class MockUnitOfVolume:
    CUBIC_METERS = "m³"
    LITERS = "L"


class MockRestoreSensor:
    """Mock RestoreSensor."""
    _attr_translation_key = None
    
    @property
    def unique_id(self):
        """Return unique ID."""
        return getattr(self, '_attr_unique_id', None)
    
    @property
    def translation_key(self):
        """Return translation key."""
        return getattr(self, '_attr_translation_key', None)
    
    async def async_get_last_sensor_data(self):
        """Get last sensor data."""
        return None


# =============================================================================
# SET UP ALL MOCKS IN sys.modules
# First ensure all parent modules exist
# =============================================================================

# Ensure all parent paths exist
parent_modules = [
    "homeassistant",
    "homeassistant.exceptions",
    "homeassistant.core",
    "homeassistant.config_entries",
    "homeassistant.const",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity_registry",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.components.diagnostics",
    "homeassistant.util",
    "homeassistant.util.dt",
]

for mod_name in parent_modules:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MockModule()


# HomeAssistantError
sys.modules["homeassistant"].exceptions = MockModule()
sys.modules["homeassistant"].exceptions.HomeAssistantError = HomeAssistantError
sys.modules["homeassistant.exceptions"].HomeAssistantError = HomeAssistantError

# ConfigEntry
sys.modules["homeassistant.config_entries"].ConfigEntry = MockConfigEntry

# Platform
sys.modules["homeassistant.const"].Platform = MockPlatform

# DeviceInfo (in both locations it might be imported from)
sys.modules["homeassistant.helpers.device_registry"] = MockModule()
sys.modules["homeassistant.helpers.device_registry"].DeviceInfo = MockDeviceInfo
sys.modules["homeassistant.helpers.entity"].DeviceInfo = MockDeviceInfo

# dt_util
sys.modules["homeassistant.util"].dt = MockDtUtil
sys.modules["homeassistant.util.dt"] = MockDtUtil

# DataUpdateCoordinator (with Generic support)
sys.modules["homeassistant.helpers.update_coordinator"].DataUpdateCoordinator = MockDataUpdateCoordinator

# UpdateFailed
sys.modules["homeassistant.helpers.update_coordinator"].UpdateFailed = MockUpdateFailed

# CoordinatorEntity
sys.modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = MockCoordinatorEntity

# async_get_clientsession
sys.modules["homeassistant.helpers.aiohttp_client"].async_get_clientsession = mock_async_get_clientsession

# CONN_CLASS
sys.modules["homeassistant.config_entries"].CONN_CLASS = MockCONNCLASS
sys.modules["homeassistant.config_entries"].CONN_CLASS_CLOUD_POLL = "cloud_polling"

# Sensor classes
sys.modules["homeassistant.components.sensor"].SensorDeviceClass = MockSensorDeviceClass
sys.modules["homeassistant.components.sensor"].SensorStateClass = MockSensorStateClass
sys.modules["homeassistant.const"].UnitOfVolume = MockUnitOfVolume
sys.modules["homeassistant.components.sensor"].RestoreSensor = MockRestoreSensor


# =============================================================================
# NOW IMPORT THE ACTUAL INTEGRATION MODULES
# (All HA dependencies are now properly mocked)
# =============================================================================

import pytest
from custom_components.regiedeseauxmpl.api import RegieDesEauxAPI
from custom_components.regiedeseauxmpl.coordinator import RegieDesEauxCoordinator
from custom_components.regiedeseauxmpl.sensor import RegieDesEauxWaterSensor
from custom_components.regiedeseauxmpl.entity import RegieDesEauxEntity
from custom_components.regiedeseauxmpl.exceptions import (
    CannotConnect,
    InvalidAuth,
    APIError,
    RegieDesEauxError
)
from custom_components.regiedeseauxmpl.const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
)


# =============================================================================
# FIXTURES FOR TESTING
# =============================================================================

@pytest.fixture
def mock_aiohttp_session():
    """Create a mock aiohttp session."""
    mock_session = MagicMock()
    mock_session.get = AsyncMock()
    mock_session.post = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.services = MagicMock()
    hass.helpers = MagicMock()
    
    # Mock now() method
    from datetime import datetime
    mock_now = MagicMock()
    mock_now.isoformat = MagicMock(return_value="2024-01-01T00:00:00+00:00")
    hass.helpers.now = MagicMock(return_value=mock_now)
    
    hass.loop = MagicMock()
    return hass


@pytest.fixture
def mock_entry():
    """Create a mock ConfigEntry."""
    return MockConfigEntry(
        entry_id="test_entry",
        title="Test Entry",
        data={
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "test_password",
            CONF_SCAN_INTERVAL: str(int(DEFAULT_SCAN_INTERVAL.total_seconds()))
        }
    )


@pytest.fixture
def mock_api(mock_aiohttp_session):
    """Create a mock API instance."""
    return RegieDesEauxAPI(mock_aiohttp_session, "test@example.com", "test_password")


@pytest.fixture
def mock_coordinator(mock_hass, mock_api):
    """Create a mock coordinator."""
    return RegieDesEauxCoordinator(mock_hass, mock_api)
