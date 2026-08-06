# TP-Link M7200 — Home Assistant integration

[![HACS: custom](https://img.shields.io/badge/HACS-custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Validate](https://github.com/rpodgorny/hass-tplink-m7200/actions/workflows/validate.yml/badge.svg)](https://github.com/rpodgorny/hass-tplink-m7200/actions/workflows/validate.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

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

### HACS (custom repository)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rpodgorny&repository=hass-tplink-m7200&category=integration)

Or manually:

1. HACS → ⋮ → **Custom repositories**
2. Add `https://github.com/rpodgorny/hass-tplink-m7200`, category **Integration**
3. Search **TP-Link M7200** in HACS → *Download*
4. Restart Home Assistant

### Icon

The integration ships its own artwork in `custom_components/tplink_m7200/brand/`
(`icon.png` 256×256, `icon@2x.png` 512×512, plus light/dark logos). It is
original work for this repository — a generic router glyph, no TP-Link logo;
see [`brand/ATTRIBUTION.md`](custom_components/tplink_m7200/brand/ATTRIBUTION.md).
Since [Home Assistant 2026.3](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/)
these are served straight from the integration through HA's brands proxy — no
submission to [home-assistant/brands](https://github.com/home-assistant/brands)
and no manifest entry required. On older Home Assistant the UI falls back to a
default icon.

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

## Disclaimer

Unofficial, not affiliated with TP-Link. Uses the device's own private local
web API, which may change between firmware versions.

## License

[GNU GPL v3](LICENSE) — you may use, modify and redistribute it, but
distributed modifications must also be released under the GPL.
