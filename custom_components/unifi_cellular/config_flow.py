"""Config flow for UniFi Cellular integration."""
from __future__ import annotations

import logging
import ssl
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_SITE,
    CONF_VERIFY_SSL,
    DEFAULT_HOST,
    DEFAULT_SITE,
    DEFAULT_VERIFY_SSL,
    DEVICE_TYPE_MBB,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_SITE, default=DEFAULT_SITE): str,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input and test the connection."""
    ssl_context: ssl.SSLContext | None = None
    if not data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    url = f"https://{data[CONF_HOST]}/proxy/network/api/s/{data[CONF_SITE]}/stat/device"
    headers = {"X-API-Key": data[CONF_API_KEY]}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers=headers,
            ssl=ssl_context,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status == 401:
                raise InvalidAuth
            if resp.status == 404:
                raise InvalidSite
            resp.raise_for_status()

            result = await resp.json()
            devices = result.get("data", [])
            device = next(
                (d for d in devices if d.get("type") == DEVICE_TYPE_MBB), None
            )

            if not device:
                raise NoDeviceFound

            return {
                "title": device.get("name", "UniFi Cellular"),
                "mac": device.get("mac", ""),
            }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UniFi Cellular."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except InvalidSite:
                errors[CONF_SITE] = "invalid_site"
            except NoDeviceFound:
                errors["base"] = "no_device"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid authentication."""


class InvalidSite(Exception):
    """Error to indicate invalid site name."""


class NoDeviceFound(Exception):
    """Error to indicate no MBB device found."""
