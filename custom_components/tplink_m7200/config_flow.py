"""Config flow — ask host + password, verify by logging in."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .api import M7200Client, M7200Error
from .const import DEFAULT_HOST, DOMAIN


class M7200ConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            client = M7200Client(user_input[CONF_PASSWORD], user_input[CONF_HOST])
            try:
                await self.hass.async_add_executor_job(client.login)
            except M7200Error:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="TP-Link M7200", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
