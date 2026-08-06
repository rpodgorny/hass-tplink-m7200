"""Diagnostics for TP-Link M7200."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .coordinator import M7200ConfigEntry

# Deliberately broad. The `status` payload is dumped whole so unmapped fields
# are visible in bug reports, which means unknown keys may carry identifiers we
# have not seen. Redact anything that identifies the SIM, the subscriber, the
# hardware or the network, and loosen only against a real tools/dump.py output.
TO_REDACT = {
    CONF_HOST,
    CONF_PASSWORD,
    "title",
    "unique_id",
    # subscriber / SIM identity
    "imei",
    "imsi",
    "iccid",
    "msisdn",
    "simSerial",
    "phoneNumber",
    "spn",
    # hardware identity
    "mac",
    "macAddress",
    "sn",
    "serialNumber",
    "deviceId",
    # network addressing
    "ipv4",
    "ipv6",
    "gateway",
    "dns1",
    "dns2",
    "ssid",
    "wpaKey",
    # session
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: M7200ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "status": async_redact_data(entry.runtime_data.data or {}, TO_REDACT),
    }
