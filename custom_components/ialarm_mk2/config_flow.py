"""Config flow for iAlarm-MK Integration 2 integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from . import IAlarmMkHub, libpyialarmmk as ipyialarmmk
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=ipyialarmmk.iAlarmMkInterface.IALARMMK_P2P_DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=ipyialarmmk.iAlarmMkInterface.IALARMMK_P2P_DEFAULT_PORT): int,
        vol.Required(CONF_USERNAME, default="<CABxxxxxx>"): str,
        vol.Required(CONF_PASSWORD, default="<password>"): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    hub = IAlarmMkHub(hass, data[CONF_HOST], data[CONF_PORT], data[CONF_USERNAME], data[CONF_PASSWORD])

    if not await hub.validate():
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_USERNAME]}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iAlarm-MK Integration 2."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
