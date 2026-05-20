"""Exceptions for the Régie des Eaux Montpellier integration."""
from homeassistant.exceptions import HomeAssistantError

class RegieDesEauxError(HomeAssistantError):
    """Base error for Régie des Eaux Montpellier integration."""

class CannotConnect(RegieDesEauxError):
    """Error to indicate we cannot connect."""

class InvalidAuth(RegieDesEauxError):
    """Error to indicate there is invalid auth."""

class APIError(RegieDesEauxError):
    """Error to indicate there is an API error."""
