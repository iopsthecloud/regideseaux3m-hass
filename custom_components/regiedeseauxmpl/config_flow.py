"""Config flow for Régie des Eaux Montpellier integration."""
from __future__ import annotations

from datetime import timedelta

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RegieDesEauxAPI
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    LOGGER,
    MIN_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .exceptions import CannotConnect, InvalidAuth

# Scan interval options (in hours)
SCAN_INTERVAL_OPTIONS = [
    timedelta(hours=1),
    timedelta(hours=2),
    timedelta(hours=3),
    timedelta(hours=6),
    timedelta(hours=12),
    timedelta(hours=24),
]

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(
            CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL.total_seconds()
        ): vol.In([x.total_seconds() for x in SCAN_INTERVAL_OPTIONS]),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, str]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = RegieDesEauxAPI(session, data[CONF_USERNAME], data[CONF_PASSWORD])

    if not await api.async_authenticate():
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {
        "title": data[CONF_USERNAME],
        CONF_SCAN_INTERVAL: data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()),
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Régie des Eaux Montpellier."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=self._build_schema(),
            errors=errors,
        )

    def _build_schema(self) -> vol.Schema:
        """Build the schema with translated options."""
        # Get scan interval options with translations
        scan_interval_options = {
            str(int(x.total_seconds())): self._format_scan_interval(x)
            for x in SCAN_INTERVAL_OPTIONS
        }

        return vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=str(int(DEFAULT_SCAN_INTERVAL.total_seconds())),
                ): vol.In(scan_interval_options),
            }
        )

    def _format_scan_interval(self, interval: timedelta) -> str:
        """Format scan interval for display."""
        total_hours = int(interval.total_seconds() / 3600)
        if total_hours == 1:
            return "1 hour"
        return f"{total_hours} hours"

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow changes.

    Since HA 2024.11+, `self.config_entry` is injected by the framework;
    subclasses must not define __init__ or assign it (it's a read-only property).
    """

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            merged = {**dict(self.config_entry.options), **user_input}
            return self.async_create_entry(title="", data=merged)

        current = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current.get(
                            CONF_SCAN_INTERVAL,
                            str(int(DEFAULT_SCAN_INTERVAL.total_seconds())),
                        ),
                    ): vol.In(
                        {
                            str(int(x.total_seconds())): self._format_scan_interval(x)
                            for x in SCAN_INTERVAL_OPTIONS
                        }
                    ),
                }
            ),
        )

    @staticmethod
    def _format_scan_interval(interval: timedelta) -> str:
        """Format scan interval for display."""
        total_hours = int(interval.total_seconds() / 3600)
        if total_hours == 1:
            return "1 hour"
        return f"{total_hours} hours"
