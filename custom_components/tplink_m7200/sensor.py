"""Sensors — all read from the single `status` payload (nested under `wan`
etc.). Field names verified against M7200 HW v4.0 / FW 4.0.5.

`connectStatus`/`networkType` ints are mapped to labels from the firmware's
own enum tables.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfDataRate,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import M7200Entity

_bytes = dict(
    device_class=SensorDeviceClass.DATA_SIZE,
    native_unit_of_measurement=UnitOfInformation.BYTES,
    state_class=SensorStateClass.TOTAL_INCREASING,
    suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
)
_speed = dict(
    device_class=SensorDeviceClass.DATA_RATE,
    native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
    state_class=SensorStateClass.MEASUREMENT,
)


@dataclass(frozen=True, kw_only=True)
class M7SensorDesc(SensorEntityDescription):
    path: tuple[str, ...] = ()  # nested lookup into the status dict
    convert: Callable[[Any], Any] | None = None


def _num(v: Any) -> float:
    return int(float(v))  # counters/speeds arrive as float-strings


# Firmware enums (from the M7200 web UI login.min.js).
_NETWORK_TYPE = {
    0: "No service", 1: "2G (GSM)", 2: "3G (WCDMA)", 3: "4G (LTE)",
    4: "TD-SCDMA", 5: "CDMA 1x", 6: "CDMA EVDO", 7: "4G+ (LTE+)",
}
_CONNECT_STATUS = {
    0: "Disabled", 1: "Disconnected", 2: "Connecting", 3: "Disconnecting", 4: "Connected",
}
_YESNO = {0: "No", 1: "Yes"}


def _mapper(table: dict[int, str]) -> Callable[[Any], str]:
    return lambda v: table.get(int(v), f"unknown ({v})")


SENSORS: tuple[M7SensorDesc, ...] = (
    M7SensorDesc(key="signal", name="Signal strength", path=("wan", "signalStrength"), icon="mdi:signal"),
    M7SensorDesc(key="network_type", name="Network type", path=("wan", "networkType"), convert=_mapper(_NETWORK_TYPE), icon="mdi:antenna"),
    M7SensorDesc(key="connect_status", name="Connection status", path=("wan", "connectStatus"), convert=_mapper(_CONNECT_STATUS), icon="mdi:wan"),
    M7SensorDesc(key="roaming", name="Roaming", path=("wan", "roaming"), convert=_mapper(_YESNO), icon="mdi:earth"),
    M7SensorDesc(key="operator", name="Home operator", path=("wan", "operatorName"), icon="mdi:sim"),
    M7SensorDesc(key="wan_ip", name="WAN IP", path=("wan", "ipv4"), icon="mdi:ip"),
    M7SensorDesc(key="total_data", name="Total data", path=("wan", "totalStatistics"), convert=_num, **_bytes),
    M7SensorDesc(key="today_data", name="Today data", path=("wan", "dailyStatistics"), convert=_num, **_bytes),
    M7SensorDesc(key="rx_speed", name="Download speed", path=("wan", "rxSpeed"), convert=_num, icon="mdi:download-network", **_speed),
    M7SensorDesc(key="tx_speed", name="Upload speed", path=("wan", "txSpeed"), convert=_num, icon="mdi:upload-network", **_speed),
    M7SensorDesc(key="connected_devices", name="Connected devices", path=("connectedDevices", "number"), icon="mdi:devices"),
    M7SensorDesc(key="unread_sms", name="Unread SMS", path=("message", "unreadMessages"), icon="mdi:message-text"),
    M7SensorDesc(key="battery", name="Battery", path=("battery", "voltage"), native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY),
    # radio quality — diagnostic
    M7SensorDesc(key="rsrp", name="RSRP", path=("wan", "rsrp"), native_unit_of_measurement="dBm", device_class=SensorDeviceClass.SIGNAL_STRENGTH, entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False),
    M7SensorDesc(key="rsrq", name="RSRQ", path=("wan", "rsrq"), native_unit_of_measurement="dB", entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False),
    M7SensorDesc(key="snr", name="SNR", path=("wan", "snr"), native_unit_of_measurement="dB", entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False),
    M7SensorDesc(key="band", name="LTE band", path=("wan", "band"), entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(M7200Sensor(coordinator, entry.entry_id, d) for d in SENSORS)


class M7200Sensor(M7200Entity, SensorEntity):
    entity_description: M7SensorDesc

    def __init__(self, coordinator, entry_id: str, desc: M7SensorDesc) -> None:
        super().__init__(coordinator, entry_id, desc.key)
        self.entity_description = desc

    @property
    def native_value(self):
        node: Any = self.coordinator.data or {}
        for k in self.entity_description.path:
            if not isinstance(node, dict):
                return None
            node = node.get(k)
        if node is None:
            return None
        conv = self.entity_description.convert
        try:
            return conv(node) if conv else node
        except (ValueError, TypeError):
            return None
