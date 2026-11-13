#!/usr/bin/env python3
"""Consolida resultados reales de auditoria y hardening."""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/cis-auditor/reportes")
FILES = {
    "sw_before": "cis_inicial_20261112T220010Z.json",
    "sw_after": "cis_inicial_20261112T221143Z.json",
    "r1_before": "r1_precheck_20261112T221710Z.json",
    "r1_after": "r1_precheck_20261112T222602Z.json",
    "fg_before": "fortigate_audit_20261112T223222Z.json",
    "fg_apply": "fortigate_apply_20261112T223231Z.json",
    "fg_after": "fortigate_verify_20261112T223456Z.json",
}

os.umask(0o077)
data = {}
for key, filename in FILES.items():
    path = ROOT / filename
    if not path.is_file():
        raise SystemExit(f"Falta evidencia: {path}")
    data[key] = json.loads(path.read_text(encoding="utf-8"))

initial = data["sw_before"]["findings"]
final = data["sw_after"]["findings"]

def control_index(items):
    return {
        (item["device"], item["control"]): item["status"]
        for item in items
    }

a = control_index(initial)
b = control_index(final)

if a.keys() != b.keys():
    raise SystemExit("Las auditorias no evalúan los mismos controles.")

counts_a = Counter(a.values())
counts_b = Counter(b.values())

if data["fg_apply"]["status"] != "VERIFICADO":
    raise SystemExit("No se verifico la aplicacion FortiGate.")
if data["fg_after"]["status"] != "VERIFICADO":
    raise SystemExit("No se verifico el estado posterior FortiGate.")

lines = [
    "# Informe técnico de auditoría y hardening",
    "",
    "**Infraestructura:** R1-CISCO, SW1-CISCO y FGT-01",
    "**Matrícula:** 2025-1331",
    f"**Generado (UTC):** {datetime.now(timezone.utc).isoformat()}",
    "",
    "## 1. Resumen de controles seleccionados",
    "",
    "| Resultado | Antes | Después |",
    "|---|---:|---:|",
]

for state in ("CUMPLE", "NO CUMPLE", "RIESGO", "REVISAR"):
    lines.append(
        f"| {state} | {counts_a[state]} | {counts_b[state]} |"
    )

lines += [
    "",
    "## 2. Cambios verificados en SW1-CISCO",
    "",
    "| Control | Antes | Después |",
    "|---|---|---|",
]

for name in ("HTTP deshabilitado", "HTTPS deshabilitado"):
    key = ("SW1-CISCO", name)
    lines.append(f"| {name} | {a[key]} | {b[key]} |")

r0 = data["r1_before"]
r1 = data["r1_after"]

lines += [
    "",
    "## 3. Cambios verificados en R1-CISCO",
    "",
    "| Control | Antes | Después |",
    "|---|---|---|",
    "| Desactivación explícita de IP Source Routing | "
    f"{r0['source_route_explicitly_disabled']} | "
    f"{r1['source_route_explicitly_disabled']} |",
]

for iface in ("GigabitEthernet0/0", "GigabitEthernet0/1"):
    for key, label in (
        ("proxy_arp", "Proxy ARP"),
        ("icmp_redirects", "ICMP Redirects"),
    ):
        old = r0["interfaces"][iface][key]
        new = r1["interfaces"][iface][key]
        lines.append(f"| {label} — {iface} | {old} | {new} |")

fg0 = data["fg_before"]["after"]
fg1 = data["fg_after"]["after"]

lines += [
    "",
    "## 4. Cambios verificados en FGT-01",
    "",
    "| Control | Antes | Después |",
    "|---|---|---|",
]

for key in (
    "admin-telnet",
    "admin-lockout-duration",
    "admin-ssh-grace-time",
    "admin-ssh-v1",
    "admintimeout",
):
    lines.append(f"| {key} | {fg0[key]} | {fg1[key]} |")

lines += [
    "",
    "## 5. Riesgos y limitaciones",
    "",
    "- Los Cisco IOSv utilizan algoritmos SSH heredados.",
    "- FortiOS 7.0.3 es una versión antigua de evaluación.",
    "- La administración HTTP en port1 permanece habilitada.",
    "- Los controles evaluados no constituyen una auditoría CIS completa.",
    "- Las pruebas PC1-PC2 requieren evidencia independiente.",
    "",
    "## 6. Trazabilidad de evidencias",
    "",
]

for key, filename in FILES.items():
    lines.append(f"- `{key}`: `{filename}`")

lines += [
    "",
    "## 7. Conclusión",
    "",
    "La infraestructura fue sometida a auditorías iniciales, "
    "aplicación automatizada de medidas de hardening y "
    "comprobaciones posteriores. Las configuraciones originales "
    "y los informes se conservan en el servidor CIS-AUDITOR.",
    "",
]

output = ROOT / "INFORME-FINAL-CIS-HARDENING-2025-1331.md"
output.write_text("\n".join(lines), encoding="utf-8")
output.chmod(0o600)

print("=== INFORME CONSOLIDADO GENERADO ===")
print("Controles evaluados:", len(a))
print("Incumplimientos iniciales:", counts_a["NO CUMPLE"])
print("Incumplimientos posteriores:", counts_b["NO CUMPLE"])
print("Archivo:", output)
