#!/usr/bin/env python3
"""Centro de auditoria de hardening: audit / apply / verify / report.

Integra scripts que YA se usaron en este laboratorio.
Ninguna opcion salvo 'apply --allow-changes' modifica dispositivos.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/opt/cis-auditor")
REPORTS = ROOT / "reportes"
SCRIPTS = {
    "baseline": "cis_audit_baseline.py",
    "checks": "cis_checks.py",
    "r1read": "r1_precheck.py",
    "forti": "fortigate_cis.py",
    "selected": "cis_benchmark_reporte.py",
    "r1apply": "cis_apply_r1.py",
    "sw1apply": "cis_apply_sw1.py",
}

def script(name, *args):
    script_path = ROOT / SCRIPTS[name]
    if not script_path.is_file():
        raise RuntimeError(f"Script requerido no encontrado: {script_path}")
    print("\n" + "=" * 68, flush=True)
    print("EJECUTANDO:", script_path.name, *args, flush=True)
    print("=" * 68, flush=True)
    completed = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(ROOT), check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script_path.name} devolvio codigo {completed.returncode}")


def newest(pattern):
    paths = sorted((p for p in REPORTS.glob(pattern) if p.is_file()),
                   key=lambda p: (p.stat().st_mtime_ns, p.name))
    if not paths:
        raise RuntimeError("No se encontro informe: " + pattern)
    return paths[-1]


def confirm_baseline():
    path = newest("baseline_*.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("results", [])
    if len(rows) != 3 or any(
        r.get("status") != "OK" or len(r.get("files", [])) != 5
        for r in rows
    ):
        raise RuntimeError("La auditoria no ha confirmado 15/15 evidencias.")
    print("[OK] Baseline: 15/15 evidencias", path.name)


def check_forti(mode):
    path = newest(f"fortigate_{mode}_*.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("mode") != mode or data.get("status") != "VERIFICADO":
        raise RuntimeError("FortiGate no verificado: " + path.name +
                           " (" + str(data.get("status")) + ")")
    print("[OK] FortiGate", mode, path.name)


def gather(mode):
    script("baseline")
    confirm_baseline()
    script("checks")
    script("r1read")
    script("forti", mode)
    # Se construye el informe CIS incluso si verify devuelve ERROR
    # en sus valores: esto ayuda a explicar la desviacion real.
    script("selected")
    check_forti(mode)


def do_apply():
    print("\nADVERTENCIA: APPLY PUEDE CAMBIAR LA CONFIGURACION ACTIVA.")
    print("El orden sera SW1, R1, FortiGate. Cada modulo pedira confirmacion.")
    print("FortiGate usa como objetivo CIS bloqueo de 900 s;")
    print("HTTP en port1 NO se modifica: permanece como excepcion.")
    response = input("Escribe APLICAR-HARDENING para continuar: ").strip()
    if response != "APLICAR-HARDENING":
        raise RuntimeError("Aplicacion cancelada; sin inicio de cambios.")

    # Actualiza los dispositivos SOLO con confirmaciones individuales.
    script("sw1apply")
    script("r1apply")
    script("forti", "apply")
    check_forti("apply")
    print("\n=== AUDITORIA POSTERIOR DE SOLO LECTURA ===")
    gather("verify")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["audit", "apply", "verify", "report"],
                   help="audit sin cambios; apply autorizado; verify sin cambios; report offline")
    p.add_argument("--allow-changes", action="store_true",
                   help="requerido SOLO para apply; se pide confirmacion adicional")
    args = p.parse_args()
    try:
        if args.command == "apply":
            if not args.allow_changes:
                p.error("apply requiere --allow-changes y confirmacion interactiva")
            do_apply()
        elif args.command in ("audit", "verify"):
            gather(args.command)
        else:
            script("selected")
    except (KeyboardInterrupt, EOFError):
        print("\nInterrumpido. Si hubo cambios, comprobar desde consola.", file=sys.stderr)
        return 130
    except Exception as exc:
        print("\n[ERROR]", exc, file=sys.stderr)
        print("No repetir apply hasta revisar cualquier cambio parcial.", file=sys.stderr)
        return 1
    print("\n=== PROCESO FINALIZADO ===")
    print("Los hallazgos NO CUMPLE o RIESGO pueden permanecer y deben documentarse.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
