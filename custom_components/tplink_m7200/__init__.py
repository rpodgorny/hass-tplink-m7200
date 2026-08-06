"""TP-Link M7200 integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .api import M7200Client
from .coordinator import M7200ConfigEntry, M7200Coordinator

PLATFORMS = [Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: M7200ConfigEntry) -> bool:
    client = M7200Client(entry.data[CONF_PASSWORD], entry.data[CONF_HOST])
    coordinator = M7200Coordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: M7200ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
