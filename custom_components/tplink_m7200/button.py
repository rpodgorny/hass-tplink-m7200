"""Reboot button."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import M7200Entity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([M7200RebootButton(coordinator, entry.entry_id)])


class M7200RebootButton(M7200Entity, ButtonEntity):
    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id, "reboot")

    async def async_press(self) -> None:
        client = self.coordinator.client
        await self.hass.async_add_executor_job(lambda: (client.login(), client.reboot()))
