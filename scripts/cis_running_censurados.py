#!/usr/bin/env python3
"""Genera candidatos ampliados y censurados de running-config.

SOLO LECTURA. Nunca publica automaticamente. Los archivos necesitan
revision visual del estudiante ANTES de subirlos a un repositorio publico.
"""
import json
import os
import re
from pathlib import Path

ROOT = Path("/opt/cis-auditor")
B = ROOT / "backups"
CISCO = {
    "R1-CISCO": ("GigabitEthernet0/0", "GigabitEthernet0/1"),
    "SW1-CISCO": ("Vlan1",),
}
SAFE_GLOBAL = [
    r"hostname (?:R1-CISCO|SW1-CISCO)",
    r"version [0-9.]+",
    r"aaa new-model", r"ip cef", r"ipv6 cef",
    r"no ip domain-lookup", r"no ip source-route",
    r"no ip http server", r"no ip http secure-server",
    r"ip ssh version 2", r"ip routing",
    r"spanning-tree mode (?:pvst|rapid-pvst)",
    r"ip route 10\.25\.14\.0 255\.255\.255\.0 172\.31\.13\.2(?: [0-9]+)?",
]
SAFE_NESTED = [
    r"ip address (?:10\.25\.13\.[12] 255\.255\.255\.0|172\.31\.13\.1 255\.255\.255\.252)",
    r"no ip redirects", r"no ip proxy-arp",
    r"(?:no )?shutdown", r"duplex (?:auto|full|half)",
    r"speed (?:auto|[0-9]+)",r"transport input ssh",
    r"exec-timeout [0-9]+ [0-9]+", r"login local",
    r"switchport mode (?:access|trunk)",
    r"switchport access vlan [0-9]+",
    r"spanning-tree portfast",
]
SAFE_BLOCK = r"(?:interface (?:GigabitEthernet[0-9]+/[0-9]+|Vlan[0-9]+)|line (?:vty [0-9]+(?: [0-9]+)?|con [0-9]+|aux [0-9]+))"


def allowed(text, expressions):
    return any(re.fullmatch(e, text) for e in expressions)


def redact_cisco(name, source):
    body = source.split("\n\n", 1)[-1]
    output = [f"! {name}: running-config CENSURADO (no restaurable)",
              "! Las lineas omitidas pueden contener valores reservados.",
              "! No publicar la salida SSH original.", ""]
    hidden, visible = 0, 0
    pending = 0
    context = False

    def flush():
        nonlocal pending
        if pending:
            output.append(f"! [OMITIDAS {pending} LINEAS NO AUTORIZADAS]")
            pending = 0

    for line in body.splitlines():
        raw = line.rstrip()
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped in ("!", "end"):
            flush()
            output.append(stripped)
            context = False
            continue
        if re.fullmatch(SAFE_BLOCK, stripped) and not line.startswith(" "):
            flush()
            context = True
            output.append(stripped)
            visible += 1
            continue
        if not line.startswith(" "):
            context = False
        is_allowed = (
            allowed(stripped, SAFE_NESTED) if context else
            allowed(stripped, SAFE_GLOBAL)
        )
        if is_allowed:
            flush()
            output.append((" " if context else "") + stripped)
            visible += 1
        else:
            pending += 1
            hidden += 1
    flush()
    return "\n".join(output) + "\n", visible, hidden


def main():
    os.umask(0o077)
    base = sorted((p for p in B.iterdir()
                   if p.is_dir() and re.fullmatch(r"[0-9]{8}T[0-9]{6}Z", p.name)),
                  key=lambda p: p.name)
    if not base:
        raise SystemExit("ERROR: faltan baselines privados.")
    last = base[-1]
    manifest = ROOT / "reportes" / f"baseline_{last.name}.json"
    if not manifest.exists():
        raise SystemExit("ERROR: falta el manifiesto de la ultima auditoria.")
    rows = json.loads(manifest.read_text(encoding="utf-8")).get("results", [])
    if len(rows) != 3 or any(
        row.get("status") != "OK" or len(row.get("files", [])) != 5
        for row in rows
    ):
        raise SystemExit("ERROR: auditoria no confirmada 15/15.")

    dest = ROOT / ("running-configs-para-revision-" + last.name)
    if dest.exists():
        raise SystemExit(f"ERROR: {dest} ya existe. No se sobrescribe.")
    dest.mkdir(mode=0o700)

    for name in CISCO:
        raw = last / (name + "_01.txt")
        if not raw.is_file() or raw.is_symlink():
            raise SystemExit(f"ERROR: falta {raw}")
        safe, good, masked = redact_cisco(name, raw.read_text(encoding="utf-8"))
        if good < 5:
            raise SystemExit(f"ERROR: pocas lineas verificadas en {name}")
        out = dest / (name + "-running-config-CENSURADO.txt")
        out.write_text(safe, encoding="utf-8")
        out.chmod(0o600)
        print(f"[OK] {out.name}: {good} lineas permitidas, {masked} censuradas.")

    # FGT: la exportacion segura anterior usa listas de campos autorizados;
    # el equipo FortiGate no usa el comando Cisco 'show running-config'.
    print("FortiGate: conservar el extracto seguro generado por")
    print("scripts/cis_exportar_publicables.py; no usar un backup de sistema completo.")
    print("\nArchivos privados para REVISION:", dest)
    print("No se han publicado archivos ni secretos en GitHub.")


if __name__ == "__main__":
    main()
