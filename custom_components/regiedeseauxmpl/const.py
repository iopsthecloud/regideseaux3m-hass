"""Constants for the Régie des Eaux Montpellier integration."""
import logging
from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "regiedeseauxmpl"
LOGGER = logging.getLogger(__package__)

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_METERS = "meters"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_SCAN_INTERVAL = timedelta(hours=6)
DEFAULT_NAME = "Régie des Eaux Montpellier"

# Minimum and maximum scan intervals
MIN_SCAN_INTERVAL = timedelta(minutes=30)
MAX_SCAN_INTERVAL = timedelta(hours=24)

# Platforms
PLATFORMS = [Platform.SENSOR]

# API Endpoints
BASE_URL = "https://ael.regiedeseaux3m.fr"
API_ROOT_URL = f"{BASE_URL}/webapi"
LOGIN_URL = f"{API_ROOT_URL}/Utilisateur/authentification"
GENERATE_TOKEN_URL = f"{API_ROOT_URL}/Acces/generateToken"
API_URL = f"{API_ROOT_URL}"

# App credentials (extracted from app.js)
WS_APPLICATION_LOGIN = "AEL-TOKEN-R3M-PRD"
WS_APPLICATION_PWD = "XX_fr-5DjklsdMM-R3M-PRD"

# Attributes
ATTR_LAST_UPDATED = "last_updated"
ATTR_LAST_READING = "last_reading"
ATTR_CONTRACT_ID = "contract_id"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_UNIT = "unit"

# Entity names
ENTITY_WATER_SENSOR = "water_index"
