# TP-Link M7200 — Home Assistant integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Add repo to HACS](https://img.shields.io/badge/HACS-Add%20repository-41BDF5.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rpodgorny&repository=hass-tplink-m7200&category=integration)

Basic local-polling integration for the TP-Link M7200 (and likely M7000/M7350)
4G LTE MiFi. Talks the device's own AES+RSA web API (`tplinkmifi.net`) — the
same one the phone app / web UI use. No cloud, no account.

**Entities** (all from one `status` poll, 30s)

- Signal strength, connection status, roaming, home operator, network type
- Total / today data, download / upload speed, WAN IP
- Connected devices, unread SMS, battery
- RSRP / RSRQ / SNR / band (diagnostic, disabled by default)
- Reboot button

## Install

### HACS (recommended)

1. Click the **Add repository** badge above, or in HACS go to *⋮ → Custom
   repositories*, add `https://github.com/rpodgorny/hass-tplink-m7200` with
   category **Integration**.
2. Search **TP-Link M7200** in HACS → *Download*.
3. Restart Home Assistant.

### Manual

Copy `custom_components/tplink_m7200/` into your HA `config/custom_components/`
and restart.

### Configure

*Settings → Devices & Services → Add Integration → TP-Link M7200*, enter host
(default `192.168.0.1`) and the modem admin password.

Field names are verified against M7200 HW v4.0 / FW 4.0.5. On other firmware
the `status` JSON may differ — dump it and adjust `SENSORS` in `sensor.py`:

```
python tools/dump.py --host 192.168.0.1 YOUR_PASSWORD
```

Missing keys just show as *unknown* — nothing breaks.

## Credits

Protocol ported from the PHP reference lib
[mt-ks/tp-link-m7200-api](https://github.com/mt-ks/tp-link-m7200-api).
