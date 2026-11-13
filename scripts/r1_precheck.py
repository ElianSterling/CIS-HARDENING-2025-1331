#!/usr/bin/env python3
import getpass
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from netmiko import ConnectHandler

BASE = Path("/opt/cis-auditor")
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

password = getpass.getpass("Contrasena SSH de R1: ")

conn = ConnectHandler(
    device_type="cisco_ios",
    host="10.25.13.1",
    username="admin1331",
    password=password,
    ssh_strict=True,
    system_host_keys=True,
    allow_agent=False,
    use_keys=False,
    fast_cli=False,
)

password = None

try:
    running = conn.send_command("show running-config")
    interfaces = {}

    for name in ("GigabitEthernet0/0", "GigabitEthernet0/1"):
        output = conn.send_command(
            f"show ip interface {name}"
        )

        proxy = re.search(
            r"Proxy ARP is (enabled|disabled)",
            output, re.I
        )

        redirects = re.search(
            r"ICMP redirects are (always|never) sent",
            output, re.I
        )

        interfaces[name] = {
            "proxy_arp": proxy.group(1).lower()
                if proxy else "REVISAR",
            "icmp_redirects": redirects.group(1).lower()
                if redirects else "REVISAR",
        }

    source_route = bool(
        re.search(
            r"(?m)^no ip source-route\s*$",
            running
        )
    )

    report = {
        "device": "R1-CISCO",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_route_explicitly_disabled": source_route,
        "interfaces": interfaces,
        "mode": "solo lectura",
    }

    path = BASE / "reportes" / f"r1_precheck_{STAMP}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8"
    )
    path.chmod(0o600)

    print("\n=== ESTADO INICIAL R1-CISCO ===")
    print("IP source-route deshabilitado explicitamente:",
          source_route)

    for name, status in interfaces.items():
        print(f"\n{name}")
        print(" Proxy ARP:", status["proxy_arp"])
        print(" ICMP Redirects:", status["icmp_redirects"])

    print("\nInforme guardado:", path)

finally:
    conn.disconnect()
