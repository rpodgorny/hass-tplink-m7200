"""Shared base: groups all entities under one device."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import M7200Coordinator


class M7200Entity(CoordinatorEntity[M7200Coordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: M7200Coordinator, entry_id: str, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{key}"
        info = (coordinator.data or {}).get("deviceInfo", {})
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="TP-Link",
            model=info.get("model", "M7200"),
            name="TP-Link M7200",
            sw_version=info.get("firmwareVer"),
            hw_version=info.get("hardwareVer"),
            serial_number=info.get("imei"),
            connections={(CONNECTION_NETWORK_MAC, info["mac"])} if info.get("mac") else set(),
        )
