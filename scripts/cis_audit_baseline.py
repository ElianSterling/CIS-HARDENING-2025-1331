#!/usr/bin/env python3
"""Auditoria inicial CIS: recopilacion por SSH, solo lectura."""

import getpass
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import paramiko
from netmiko import ConnectHandler

ROOT = Path("/opt/cis-auditor")

DEVICES = [
    ("R1-CISCO", "10.25.13.1", "admin1331", "cisco"),
    ("SW1-CISCO", "10.25.13.2", "admin1331", "cisco"),
    ("FGT-01", "192.168.1.123", "admin", "fortinet"),
]

CISCO_COMMANDS = [
    "show running-config",
    "show ip ssh",
    "show ip interface brief",
    "show version",
    "show ip http server status",
]

FORTI_COMMANDS = [
    "get system status",
    "show system interface",
    "show firewall policy",
    "show router static",
    "show system global",
]

PROMPT = re.compile(r"(?m)^FGT-01\s*#\s*$")


def receive_prompt(channel, timeout=90):
    output = ""
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if channel.recv_ready():
            chunk = channel.recv(32768).decode(
                "utf-8", errors="replace"
            )
            if not chunk:
                break

            output += chunk

            if "--More--" in chunk:
                channel.send(" ")

            if PROMPT.search(output.rstrip()):
                return output

        elif channel.closed:
            break
        else:
            time.sleep(0.1)

    raise TimeoutError("Prompt FortiGate no detectado")


def audit_cisco(ip, username, password):
    connection = ConnectHandler(
        device_type="cisco_ios",
        host=ip,
        username=username,
        password=password,
        ssh_strict=True,
        system_host_keys=True,
        allow_agent=False,
        use_keys=False,
        conn_timeout=12,
        auth_timeout=30,
        banner_timeout=30,
        fast_cli=False,
    )

    try:
        results = {}

        for command in CISCO_COMMANDS:
            results[command] = connection.send_command(
                command, read_timeout=90
            )

        return results

    finally:
        connection.disconnect()


def audit_fortinet(ip, username, password):
    client = paramiko.SSHClient()
    client.load_host_keys("/root/.ssh/known_hosts")
    client.set_missing_host_key_policy(
        paramiko.RejectPolicy()
    )

    client.connect(
        ip,
        username=username,
        password=password,
        timeout=12,
        auth_timeout=30,
        banner_timeout=30,
        look_for_keys=False,
        allow_agent=False,
    )

    try:
        channel = client.invoke_shell(
            term="vt100",
            width=240,
            height=1000,
        )

        receive_prompt(channel, timeout=30)
        results = {}

        for command in FORTI_COMMANDS:
            channel.send(command + "\n")
            results[command] = receive_prompt(channel)

        return results

    finally:
        client.close()


def save_private(path, content):
    path.write_text(content, encoding="utf-8")
    path.chmod(0o600)


def main():
    os.umask(0o077)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    backup_dir = ROOT / "backups" / timestamp
    report_dir = ROOT / "reportes"

    backup_dir.mkdir(
        parents=True, exist_ok=False, mode=0o700
    )
    report_dir.mkdir(
        parents=True, exist_ok=True, mode=0o700
    )

    records = []

    print("=" * 55)
    print(" CIS AUDITOR - BASELINE INICIAL")
    print(" Modo: SOLO LECTURA")
    print("=" * 55)

    for name, ip, username, kind in DEVICES:
        print(f"\n[+] Conectando: {name} ({ip})")

        password = getpass.getpass(
            f"Contraseña SSH de {name}: "
        )

        record = {
            "device": name,
            "ip": ip,
            "status": "ERROR",
            "files": [],
        }

        try:
            if kind == "cisco":
                outputs = audit_cisco(
                    ip, username, password
                )
            else:
                outputs = audit_fortinet(
                    ip, username, password
                )

            for index, (command, output) in enumerate(
                outputs.items(), start=1
            ):
                if not output.strip():
                    raise ValueError(
                        f"Salida vacia: {command}"
                    )

                filename = f"{name}_{index:02d}.txt"
                path = backup_dir / filename

                content = (
                    f"# Equipo: {name}\n"
                    f"# Comando: {command}\n\n"
                    f"{output}\n"
                )

                save_private(path, content)

                checksum = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()

                record["files"].append({
                    "command": command,
                    "name": filename,
                    "sha256": checksum,
                })

            record["status"] = "OK"
            print(
                f"[OK] {len(record['files'])} "
                "evidencias guardadas"
            )

        except Exception as error:
            record["error"] = (
                f"{type(error).__name__}: {error}"
            )
            print(f"[ERROR] {record['error']}")

        finally:
            password = None

        records.append(record)

    manifest = {
        "date_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "type": "Baseline de solo lectura",
        "cis_compliance_certified": False,
        "results": records,
    }

    json_path = report_dir / (
        f"baseline_{timestamp}.json"
    )

    save_private(
        json_path,
        json.dumps(
            manifest, indent=2, ensure_ascii=False
        ) + "\n",
    )

    lines = [
        "# Informe inicial - CIS Hardening",
        "",
        f"Fecha UTC: {manifest['date_utc']}",
        "",
        "Recopilacion automatizada de evidencias.",
        "No se aplicaron cambios de configuracion.",
        "Este informe no certifica conformidad CIS.",
        "",
        "| Dispositivo | Estado | Evidencias |",
        "|---|---|---:|",
    ]

    for record in records:
        lines.append(
            f"| {record['device']} | "
            f"{record['status']} | "
            f"{len(record['files'])} |"
        )

    lines.extend([
        "",
        "Los respaldos pueden contener datos sensibles.",
        "No publicar backups/ ni config/ en GitHub.",
        "",
    ])

    markdown_path = report_dir / (
        f"baseline_{timestamp}.md"
    )

    save_private(
        markdown_path,
        "\n".join(lines),
    )

    print("\n" + "=" * 55)
    print(" RESULTADOS")
    print("=" * 55)
    print(f"Informe: {markdown_path}")
    print(f"JSON: {json_path}")
    print(f"Respaldos: {backup_dir}")
    print("Auditoria finalizada sin cambios intencionales.")


if __name__ == "__main__":
    main()
