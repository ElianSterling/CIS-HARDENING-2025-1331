#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/cis-auditor/reportes")
BEFORE = ROOT / "cis_inicial_20261112T220010Z.json"
AFTER = ROOT / "cis_inicial_20261112T221143Z.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

initial = read(BEFORE)
final = read(AFTER)

def index(report):
    return {
        (item["device"], item["control"]): item
        for item in report["findings"]
    }

before = index(initial)
after = index(final)

if before.keys() != after.keys():
    raise SystemExit(
        "ERROR: los informes no tienen los mismos controles."
    )

changes = []
for key in sorted(before):
    a = before[key]
    b = after[key]
    if a["status"] != b["status"]:
        changes.append({
            "device": key[0],
            "control": key[1],
            "before": a["status"],
            "after": b["status"]
        })

counts_before = Counter(x["status"] for x in before.values())
counts_after = Counter(x["status"] for x in after.values())

lines = [
    "# Informe comparativo de Hardening",
    "",
    "**Infraestructura:** R1-CISCO, SW1-CISCO y FGT-01",
    "",
    f"**Auditoria inicial:** {BEFORE.name}",
    "",
    f"**Auditoria posterior:** {AFTER.name}",
    "",
    "## Resumen",
    "",
    "| Estado | Antes | Despues |",
    "|---|---:|---:|"
]

for status in ("CUMPLE", "NO CUMPLE", "RIESGO", "REVISAR"):
    lines.append(
        f"| {status} | "
        f"{counts_before[status]} | {counts_after[status]} |"
    )

lines.extend([
    "",
    "## Cambios comprobados",
    "",
    "| Dispositivo | Control | Antes | Despues |",
    "|---|---|---|---|"
])

for c in changes:
    lines.append(
        f"| {c['device']} | {c['control']} | "
        f"{c['before']} | {c['after']} |"
    )

lines.extend([
    "",
    "## Alcance y limitaciones",
    "",
    "Evaluacion de controles seleccionados de configuracion.",
    "No representa una auditoria CIS Benchmark completa.",
    "Permanecen riesgos de protocolos heredados y "
    "limitaciones del entorno de evaluacion.",
    "",
    "Los respaldos originales permanecen privados en "
    "el servidor de auditoria.",
    ""
])

output = ROOT / "comparativo_hardening_20261112.md"
output.write_text("\n".join(lines), encoding="utf-8")
output.chmod(0o600)

print("=== COMPARACION TERMINADA ===")
print("Controles evaluados:", len(before))
print("Controles modificados:", len(changes))
for c in changes:
    print(
        f"{c['device']} | {c['control']} | "
        f"{c['before']} -> {c['after']}"
    )
print("Informe:", output)
