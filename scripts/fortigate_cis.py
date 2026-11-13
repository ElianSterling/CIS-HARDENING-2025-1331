#!/usr/bin/env python3
"""Auditoria y hardening administrativo de FortiGate."""

import getpass
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paramiko

BASE = Path("/opt/cis-auditor")
HOST = "192.168.1.123"

KEYS = (
    "admin-telnet",
    "admin-lockout-duration",
    "admin-lockout-threshold",
    "admin-ssh-grace-time",
    "admin-ssh-v1",
    "admintimeout",
)

TARGET = {
    "admin-telnet": "disable",
    "admin-lockout-duration": "900",
    "admin-ssh-grace-time": "30",
}

PROMPT = re.compile(
    r"(?m)^FGT-01(?: \([^)]+\))? #\s*$"
)


def wait_prompt(channel, seconds=40):
    output = ""
    deadline = time.monotonic() + seconds

    while time.monotonic() < deadline:
        if channel.recv_ready():
            chunk = channel.recv(65535).decode(
                "utf-8", "replace"
            ).replace("\r", "")

            output += chunk

            if PROMPT.search(output.rstrip()):
                return output

        elif channel.closed:
            break

        else:
            time.sleep(0.1)

    raise TimeoutError(
        "FortiGate no devolvio el prompt esperado"
    )


def run(channel, command):
    channel.send(command + "\n")
    output = wait_prompt(channel)

    if re.search(
        r"(?im)(command fail|parse error|"
        r"unknown action|^error:)",
        output
    ):
        raise RuntimeError(
            f"FortiGate rechazo {command}: {output[-350:]}"
        )

    return output


def get_values(channel):
    output = run(
        channel,
        "show full-configuration system global | grep admin"
    )

    values = {}

    for key in KEYS:
        match = re.search(
            rf"(?m)^\s*set {re.escape(key)}\s+(\S+)",
            output
        )

        if not match:
            raise RuntimeError(
                f"No se encontro evidencia para {key}"
            )

        values[key] = match.group(1)

    return values, output


def save_private(path, content):
    path.write_text(content, encoding="utf-8")
    path.chmod(0o600)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in (
        "audit", "apply", "verify"
    ):
        raise SystemExit(
            "Uso: python fortigate_cis.py audit|apply|verify"
        )

    action = sys.argv[1]
    os.umask(0o077)

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    backup = BASE / "backups" / f"fg-{action}-{stamp}"
    reports = BASE / "reportes"

    backup.mkdir(
        parents=True, exist_ok=False, mode=0o700
    )
    reports.mkdir(
        parents=True, exist_ok=True, mode=0o700
    )

    report = {
        "device": "FGT-01",
        "mode": action,
        "timestamp_utc": stamp,
        "status": "INICIADO",
        "applied": [],
        "before": None,
        "after": None,
    }

    client = paramiko.SSHClient()
    client.load_host_keys("/root/.ssh/known_hosts")
    client.set_missing_host_key_policy(
        paramiko.RejectPolicy()
    )

    try:
        password = getpass.getpass(
            "Contrasena SSH FortiGate: "
        )

        client.connect(
            HOST,
            username="admin",
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=15,
            auth_timeout=30,
            banner_timeout=30,
        )

        password = None

        channel = client.invoke_shell(
            term="vt100",
            width=240,
            height=1000,
        )

        wait_prompt(channel)

        system = run(channel, "get system status")

        if not re.search(
            r"(?m)^Hostname:\s+FGT-01\s*$",
            system
        ):
            raise RuntimeError(
                "El hostname no coincide con FGT-01"
            )

        before, raw = get_values(channel)
        report["before"] = before

        save_private(
            backup / "admin-before.txt", raw
        )

        print("\n=== ESTADO INICIAL ===")
        print(json.dumps(before, indent=2))

        changes = {
            key: value
            for key, value in TARGET.items()
            if before[key] != value
        }

        print("\n=== CAMBIOS PROPUESTOS ===")
        print(changes or "Ninguno")

        if action == "apply" and changes:
            confirmation = input(
                "\nEscribe APLICAR-FGT para autorizar: "
            ).strip()

            if confirmation != "APLICAR-FGT":
                report["status"] = "CANCELADO"
                print("Operacion cancelada.")
                return

            run(channel, "config system global")

            try:
                for key, value in changes.items():
                    command = f"set {key} {value}"
                    run(channel, command)
                    report["applied"].append(command)
            finally:
                run(channel, "end")

        after, raw_after = get_values(channel)
        report["after"] = after

        save_private(
            backup / "admin-after.txt", raw_after
        )

        if action in ("apply", "verify"):
            if any(
                after[key] != value
                for key, value in TARGET.items()
            ):
                raise RuntimeError(
                    "No se alcanzaron los valores deseados"
                )

            if any(
                after[key] != before[key]
                for key in KEYS
                if key not in TARGET
            ):
                raise RuntimeError(
                    "Cambio no autorizado detectado"
                )

        report["status"] = "VERIFICADO"

        print("\n=== RESULTADO ===")
        print(json.dumps(after, indent=2))
        print("Estado:", report["status"])

    except Exception as exc:
        report["status"] = "ERROR"
        report["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        print("\nERROR:", report["error"])
        print(
            "Si hubo cambios, revisar desde la "
            "consola de FortiGate."
        )

    finally:
        client.close()

        path = reports / (
            f"fortigate_{action}_{stamp}.json"
        )

        save_private(
            path,
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False
            ) + "\n"
        )

        print("\nInforme:", path)


if __name__ == "__main__":
    main()
