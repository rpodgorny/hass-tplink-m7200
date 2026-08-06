"""Reboot button."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import M7200ConfigEntry
from .entity import M7200Entity

# Entities are coordinator-driven and have no update() method, so Home
# Assistant would create no semaphore anyway; stated explicitly.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: M7200ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([M7200RebootButton(entry.runtime_data, entry.entry_id)])


class M7200RebootButton(M7200Entity, ButtonEntity):
    # Supplies both the name and the icon; no _attr_name/_attr_icon needed.
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id, "reboot")

    async def async_press(self) -> None:
        client = self.coordinator.client
        await self.hass.async_add_executor_job(lambda: (client.login(), client.reboot()))
