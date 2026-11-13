#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/cis-auditor")
BACKUPS = ROOT / "backups"
REPORTS = ROOT / "reportes"

baselines = sorted(
    p for p in BACKUPS.iterdir()
    if p.is_dir() and re.fullmatch(r"\d{8}T\d{6}Z", p.name)
)
if not baselines:
    raise RuntimeError("No se encontraron auditorias baseline")
latest = baselines[-1]
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
findings = []

def load(device, number):
    path = latest / f"{device}_{number:02d}.txt"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text.split("\n\n", 1)[-1]
    if re.search(
        r"% Invalid input|% Incomplete command|"
        r"% Ambiguous command|command parse error",
        body, re.I
    ):
        return ""
    return body

def has(pattern, text):
    return bool(re.search(pattern, text, re.I | re.M))

def add(device, control, status, source, detail):
    findings.append({
        "device": device,
        "control": control,
        "status": status,
        "evidence": source,
        "detail": detail
    })

for device in ("R1-CISCO", "SW1-CISCO"):
    config = load(device, 1)
    ssh = load(device, 2)
    http = load(device, 5)

    add(device, "AAA new-model",
        "CUMPLE" if has(r"^aaa new-model\s*$", config)
        else "REVISAR" if not config else "NO CUMPLE",
        f"{device}_01.txt", "Autenticacion AAA")

    add(device, "SSH version 2",
        "CUMPLE" if has(r"SSH Enabled - version 2\.0", ssh)
        else "REVISAR" if not ssh else "NO CUMPLE",
        f"{device}_02.txt", "SSH habilitado")

    vty = re.findall(
        r"(?m)^line vty \d+(?: \d+)?[ \t]*\n"
        r"((?:^[ \t][^\n]*\n?)*)",
        config
    )

    add(device, "VTY solo SSH",
        "CUMPLE" if vty and all(
            has(r"^\s*transport input ssh\s*$", b)
            for b in vty
        ) else "REVISAR" if not vty else "NO CUMPLE",
        f"{device}_01.txt", "Telnet deshabilitado")

    valid_timeout = bool(vty)
    for block in vty:
        matches = re.findall(
            r"^\s*exec-timeout\s+(\d+)\s+(\d+)\s*$",
            block, re.M
        )
        valid_timeout &= bool(matches) and all(
            int(minutes) * 60 + int(seconds) <= 600
            for minutes, seconds in matches
        )

    add(device, "Timeout VTY maximo 10 minutos",
        "CUMPLE" if valid_timeout
        else "REVISAR" if not vty else "NO CUMPLE",
        f"{device}_01.txt", "Tiempo de inactividad")

    for title, pattern in (
        ("HTTP deshabilitado",
         r"^HTTP server status:\s*(Enabled|Disabled)"),
        ("HTTPS deshabilitado",
         r"^HTTP secure server status:\s*(Enabled|Disabled)")
    ):
        match = re.search(pattern, http, re.I | re.M)
        status = (
            "CUMPLE" if match.group(1).lower() == "disabled"
            else "NO CUMPLE"
        ) if match else "REVISAR"

        add(device, title, status, f"{device}_05.txt",
            "Estado operativo del servidor web")

    if ssh and has(r"sha1|ssh-rsa", ssh):
        add(device, "Algoritmos SSH heredados",
            "RIESGO", f"{device}_02.txt",
            "Limitacion criptografica de IOSv")

interfaces = load("FGT-01", 2)
policies = load("FGT-01", 3)
system = load("FGT-01", 1)

for port in ("port1", "port2", "port3"):
    match = re.search(
        rf'(?ms)^\s*edit\s+["\']?{port}["\']?\s*$'
        rf'\n(.*?)(?=^\s*next\s*$)',
        interfaces
    )

    if not match:
        add("FGT-01", f"Acceso administrativo {port}",
            "REVISAR", "FGT-01_02.txt",
            "Interfaz no identificada")
        continue

    access = re.search(
        r"^\s*set allowaccess\s+(.+)$",
        match.group(1), re.M
    )
    services = set(
        access.group(1).lower().split()
    ) if access else set()

    if port == "port1":
        status = (
            "RIESGO" if services & {"http", "telnet"}
            else "CUMPLE" if access else "REVISAR"
        )
    else:
        status = (
            "NO CUMPLE" if services &
            {"http", "https", "ssh", "telnet"}
            else "CUMPLE" if access else "REVISAR"
        )

    add("FGT-01", f"Acceso administrativo {port}",
        status, "FGT-01_02.txt",
        "Protocolos: " + ", ".join(sorted(services)))

add("FGT-01", "Politicas con servicio ALL",
    "RIESGO" if has(
        r'^\s*set service\s+.*(?:"ALL"|\bALL\b)', policies
    ) else "REVISAR" if not policies else "CUMPLE",
    "FGT-01_03.txt",
    "Verificacion de servicios permisivos")

add("FGT-01", "Version antigua FortiOS",
    "RIESGO" if "v7.0.3" in system else "REVISAR",
    "FGT-01_01.txt",
    "Revisar ciclo de soporte y actualizaciones")

REPORTS.mkdir(parents=True, exist_ok=True)

report = {
    "timestamp": timestamp,
    "baseline": latest.name,
    "scope": "Controles seleccionados, no auditoria CIS completa",
    "findings": findings
}

json_file = REPORTS / f"cis_inicial_{timestamp}.json"
md_file = REPORTS / f"cis_inicial_{timestamp}.md"

json_file.write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n"
)

lines = [
    "# Informe inicial de controles de seguridad",
    "",
    f"Baseline: {latest.name}",
    "",
    "Evaluacion automatizada de controles seleccionados.",
    "No constituye certificacion CIS completa.",
    "",
    "| Dispositivo | Control | Resultado | Evidencia |",
    "|---|---|---|---|"
]

for item in findings:
    lines.append(
        f"| {item['device']} | {item['control']} | "
        f"{item['status']} | {item['evidence']} |"
    )

md_file.write_text("\n".join(lines) + "\n")

json_file.chmod(0o600)
md_file.chmod(0o600)

print("\n======================================")
print(" RESULTADO DE AUDITORIA INICIAL")
print("======================================")

for device in ("R1-CISCO", "SW1-CISCO", "FGT-01"):
    items = [x for x in findings if x["device"] == device]
    print(f"\n{device}")
    for state in ("CUMPLE", "NO CUMPLE", "RIESGO", "REVISAR"):
        count = sum(x["status"] == state for x in items)
        print(f"  {state}: {count}")

print("\nInforme MD:", md_file)
print("Informe JSON:", json_file)
print("\nNo se realizaron cambios en los dispositivos.")
