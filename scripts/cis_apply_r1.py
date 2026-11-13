#!/usr/bin/env python3
"""Hardening automatizado de R1-CISCO."""

import getpass
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from netmiko import ConnectHandler

BASE = Path("/opt/cis-auditor")
IFACES = ["GigabitEthernet0/0", "GigabitEthernet0/1"]

def guardar(path, contenido):
    path.write_text(contenido, encoding="utf-8")
    path.chmod(0o600)

def revisar(conn):
    running = conn.send_command("show running-config")
    ssh = conn.send_command("show ip ssh")
    route = conn.send_command("show ip route 10.25.14.0")

    data = {
        "source_route_disabled": bool(re.search(
            r"(?m)^no ip source-route\s*$", running
        )),
        "interfaces": {}
    }

    for iface in IFACES:
        output = conn.send_command(f"show ip interface {iface}")

        proxy = re.search(
            r"Proxy ARP is (enabled|disabled)", output, re.I
        )
        redirects = re.search(
            r"ICMP redirects are (always|never) sent",
            output, re.I
        )

        if not proxy or not redirects:
            raise RuntimeError(
                f"No se pudo interpretar {iface}"
            )

        data["interfaces"][iface] = {
            "proxy_arp": proxy.group(1).lower(),
            "icmp_redirects": redirects.group(1).lower()
        }

    return data, running, ssh, route

def main():
    os.umask(0o077)
    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    backup = BASE / "backups" / f"hardening-r1-{stamp}"
    backup.mkdir(parents=True, mode=0o700)
    reportdir = BASE / "reportes"
    reportdir.mkdir(parents=True, exist_ok=True)

    print("=== CIS HARDENING R1-CISCO ===")
    password = getpass.getpass("Contrasena SSH R1: ")

    conn = ConnectHandler(
        device_type="cisco_ios",
        host="10.25.13.1",
        username="admin1331",
        password=password,
        ssh_strict=True,
        system_host_keys=True,
        allow_agent=False,
        use_keys=False,
        fast_cli=False
    )
    password = None
    before = None
    after = None
    commands = []
    status = "NO_APLICADO"
    error = None

    try:
        before, running, ssh, route = revisar(conn)
        guardar(backup / "running-before.txt", running)

        if "SSH Enabled - version 2.0" not in ssh:
            raise RuntimeError("SSH v2 no verificado")

        if "172.31.13.2" not in route:
            raise RuntimeError("Ruta FortiGate no verificada")

        if not before["source_route_disabled"]:
            commands.append("no ip source-route")

        for iface in IFACES:
            info = before["interfaces"][iface]
            needed = []

            if info["proxy_arp"] != "disabled":
                needed.append("no ip proxy-arp")
            if info["icmp_redirects"] != "never":
                needed.append("no ip redirects")

            if needed:
                commands += [f"interface {iface}", *needed, "exit"]

        print("\nESTADO INICIAL:")
        print(json.dumps(before, indent=2))
        print("\nCOMANDOS PROPUESTOS:")
        print("\n".join(commands) if commands else "Ninguno")

        if not commands:
            status = "SIN_CAMBIOS_NECESARIOS"
            return

        confirm = input(
            "\nEscribe APLICAR-R1 para autorizar: "
        ).strip()

        if confirm != "APLICAR-R1":
            status = "CANCELADO"
            print("Operacion cancelada.")
            return

        status = "CAMBIOS_INICIADOS"
        result = conn.send_config_set(
            commands,
            error_pattern=r"(?m)^%\s*(Invalid input|Error|Incomplete command)"
        )
        guardar(backup / "aplicacion.txt", result)

        after, running_after, ssh_after, route_after = revisar(conn)
        guardar(backup / "running-after.txt", running_after)

        for iface, info in after["interfaces"].items():
            if info["proxy_arp"] != "disabled":
                raise RuntimeError(f"Proxy ARP activo: {iface}")
            if info["icmp_redirects"] != "never":
                raise RuntimeError(f"Redirects activos: {iface}")

        if not after["source_route_disabled"]:
            raise RuntimeError("Source routing no verificado")

        if "SSH Enabled - version 2.0" not in ssh_after:
            raise RuntimeError("SSH v2 no verificado despues")

        if "172.31.13.2" not in route_after:
            raise RuntimeError("Ruta FortiGate no verificada despues")

        saved = conn.save_config()
        guardar(backup / "startup-save.txt", saved)

        status = "VERIFICADO_Y_GUARDADO"

        print("\n=== HARDENING VERIFICADO ===")
        print("Proxy ARP: deshabilitado")
        print("ICMP Redirects: deshabilitados")
        print("IP Source Routing: deshabilitado")
        print("SSH v2: conservado")
        print("Ruta FortiGate: conservada")
        print("Configuracion: guardada")

    except Exception as exc:
        error = str(exc)
        status = "ERROR"
        print("\nERROR:", error)
        print("Revisar configuracion activa antes de reintentar.")

    finally:
        conn.disconnect()
        report = {
            "device": "R1-CISCO",
            "date": stamp,
            "status": status,
            "before": before,
            "after": after,
            "commands": commands,
            "error": error
        }
        path = reportdir / f"hardening-r1-{stamp}.json"
        guardar(path, json.dumps(report, indent=2) + "\n")
        print("\nInforme:", path)
        print("Respaldo:", backup)

if __name__ == "__main__":
    main()
