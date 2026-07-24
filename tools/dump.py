#!/usr/bin/env python3
"""Dump raw status + flowstat JSON from a real M7200 so sensor field names can
be locked in. Run once against the device, paste the output.

    python tools/dump.py --host 192.168.0.1 PASSWORD
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "custom_components" / "tplink_m7200"))
from api import M7200Client, M7200Error  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("password")
    p.add_argument("--host", default="192.168.0.1")
    args = p.parse_args()

    c = M7200Client(args.password, args.host)
    try:
        c.login()
        print("token:", c.token)
        print("\n== status ==")
        print(json.dumps(c.get_status(), indent=2))
        print("\n== flowstat ==")
        print(json.dumps(c.get_flowstat(), indent=2))
    except M7200Error as err:
        print("ERROR:", err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
