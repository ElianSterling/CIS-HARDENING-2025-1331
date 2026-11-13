#!/usr/bin/env python3
"""Hardening de HTTP/HTTPS en SW1-CISCO."""

import getpass
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from netmiko import ConnectHandler

BASE = Path("/opt/cis-auditor")
HOST = "10.25.13.2"


def http_status(output):
    values = {}
    patterns = {
        "HTTP": r"^HTTP server status:\s*(Enabled|Disabled)\b",
        "HTTPS": r"^HTTP secure server status:\s*(Enabled|Disabled)\b",
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, output, flags=re.I | re.M)
        if not match:
            raise RuntimeError(
                f"No se pudo verificar {name}. Revisar la salida del equipo."
            )
        values[name] = match.group(1).lower()
    return values


def private_save(path, data):
    path.write_text(data, encoding="utf-8")
    path.chmod(0o600)


def main():
    os.umask(0o077)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = BASE / "backups" / f"pre-hardening-sw1-{stamp}"
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    (BASE / "reportes").mkdir(
        parents=True, exist_ok=True, mode=0o700
    )

    print("=== HARDENING SW1-CISCO ===")
    print("Se deshabilitaran HTTP y HTTPS.")
    print("SSH no se modificara.")

    password = getpass.getpass("Contrasena SSH de SW1: ")

    session = ConnectHandler(
        device_type="cisco_ios",
        host=HOST,
        username="admin1331",
        password=password,
        ssh_strict=True,
        system_host_keys=True,
        allow_agent=False,
        use_keys=False,
        conn_timeout=15,
        auth_timeout=30,
        fast_cli=False,
    )
    password = None

    try:
        config = session.send_command(
            "show running-config", read_timeout=90
        )
        before_text = session.send_command(
            "show ip http server status"
        )
        before = http_status(before_text)

        private_save(
            directory / "running-config-before.txt", config
        )
        private_save(
            directory / "http-before.txt", before_text
        )

        print("Estado inicial:", before)

        commands = []

        if before["HTTP"] == "enabled":
            commands.append("no ip http server")

        if before["HTTPS"] == "enabled":
            commands.append("no ip http secure-server")

        if not commands:
            print("Ambos servicios ya estan deshabilitados.")
            print("No se requieren cambios.")
            return

        print("Comandos propuestos:")
        for command in commands:
            print(" ", command)

        confirmation = input(
            "Escribe APLICAR-SW1 para autorizar: "
        ).strip()

        if confirmation != "APLICAR-SW1":
            print("Operacion cancelada. Sin cambios.")
            return

        output = session.send_config_set(
            commands,
            error_pattern=(
                r"(?m)^%\s*(Invalid input|Error|Incomplete command)"
            ),
        )

        private_save(
            directory / "comandos-aplicados.txt", output
        )

        after_text = session.send_command(
            "show ip http server status"
        )
        after = http_status(after_text)

        private_save(
            directory / "http-after.txt", after_text
        )

        ssh_text = session.send_command("show ip ssh")
        private_save(
            directory / "ssh-after.txt", ssh_text
        )

        if after != {
            "HTTP": "disabled",
            "HTTPS": "disabled"
        }:
            raise RuntimeError(
                f"Verificacion HTTP/HTTPS fallida: {after}. "
                "No se guardo startup-config."
            )

        if not re.search(
            r"SSH Enabled - version 2\.0", ssh_text, re.I
        ):
            raise RuntimeError(
                "No se pudo confirmar SSH v2. "
                "No se guardo startup-config."
            )

        save_result = session.save_config()
        private_save(
            directory / "guardar-startup.txt", save_result
        )

        report = {
            "device": "SW1-CISCO",
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "before": before,
            "after": after,
            "commands": commands,
            "ssh_v2_verified": True,
            "startup_saved": True,
        }

        result_path = (
            BASE / "reportes" / f"hardening-sw1-{stamp}.json"
        )

        private_save(
            result_path,
            json.dumps(report, indent=2) + "\n"
        )

        print("=== CAMBIO VERIFICADO ===")
        print("HTTP: disabled")
        print("HTTPS: disabled")
        print("SSH v2: enabled")
        print("Configuracion guardada.")
        print("Informe:", result_path)
        print("Respaldo:", directory)

    finally:
        session.disconnect()


if __name__ == "__main__":
    main()
