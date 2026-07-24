# TP-Link M7200 — Home Assistant integration

Basic local-polling integration for the TP-Link M7200 (and likely M7000/M7350)
4G LTE MiFi. Talks the device's own AES+RSA web API (`tplinkmifi.net`) — the
same one the phone app / web UI use. No cloud, no account.

**Entities** (all from one `status` poll, 30s)

- Signal strength, network type, connection status, operator
- Total / today data, download / upload speed
- Connected devices, unread SMS, battery
- RSRP / RSRQ / SNR / band (diagnostic, disabled by default)
- Reboot button

## Install

**HACS** → *Custom repositories* → add this repo (category *Integration*) →
install → restart HA.

**Manual** → copy `custom_components/tplink_m7200/` into your HA
`config/custom_components/` → restart.

Then *Settings → Devices & Services → Add Integration → TP-Link M7200*, enter
host (default `192.168.9.1`) and the modem admin password.

Field names are verified against M7200 HW v4.0 / FW 4.0.5. On other firmware
the `status` JSON may differ — dump it and adjust `SENSORS` in `sensor.py`:

```
python tools/dump.py --host 192.168.0.1 YOUR_PASSWORD
```

Missing keys just show as *unknown* — nothing breaks.

## Credits

Protocol ported from the PHP reference lib
[mt-ks/tp-link-m7200-api](https://github.com/mt-ks/tp-link-m7200-api).
