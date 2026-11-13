#!/usr/bin/env python3
"""Cotejo de controles CIS seleccionados a partir de informes existentes.

Solo lectura: nunca accede a dispositivos ni modifica configuraciones.
No sustituye a CIS-CAT ni representa una auditoría completa.
"""
import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEFAULT = Path("/opt/cis-auditor/reportes")
CISCO_SOURCE = (
    "CIS Cisco IOS Benchmark v2.2 (2007), referencia historica, "
    "NO validado como equivalente a IOSv 15.9"
)
FORTI_SOURCE = (
    "CIS Fortigate 7.0.x v1.3.0 (2024); CIS anuncia v1.4.0 "
    "(2026) sin cambios respecto de la version anterior"
)


def newest(folder, patterns):
    choices = []
    for pat in patterns:
        choices.extend(folder.glob(pat))
    choices = [p for p in choices if p.is_file()]
    if not choices:
        raise FileNotFoundError("No hay reportes para: " + ", ".join(patterns))
    return max(choices, key=lambda p: (p.stat().st_mtime_ns, p.name))


def load(path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("JSON invalido: " + str(path))
    return obj


def generate(folder, outfile=None):
    # El ultimo informe del evaluador de 19 controles,
    # la ultima consulta R1, y el ultimo audit/verify FortiGate.
    p19 = newest(folder, ["cis_inicial_*.json"])
    pr1 = newest(folder, ["r1_precheck_*.json"])
    pfg = newest(folder, ["fortigate_audit_*.json", "fortigate_verify_*.json",
                          "fortigate_apply_*.json"])
    a19, r1, fg = load(p19), load(pr1), load(pfg)

    findings = a19.get("findings")
    if not isinstance(findings, list) or len(findings) != 19:
        raise ValueError("El evaluador de 19 comprobaciones no tiene 19 hallazgos.")
    if r1.get("device") != "R1-CISCO" or r1.get("mode") != "solo lectura":
        raise ValueError("Informe R1 no verificado o no es de solo lectura.")
    if fg.get("device") != "FGT-01" or fg.get("status") != "VERIFICADO":
        raise ValueError("Informe de FortiGate no verificado.")
    after = fg.get("after")
    if not isinstance(after, dict):
        raise ValueError("El informe FGT no incluye after.")

    by_key = {(x["device"], x["control"]): x for x in findings}
    outcomes = []

    def add(device, cid, title, success, rationale, evidence, source, remark=""):
        status = "CUMPLE" if success is True else (
            "NO CUMPLE" if success is False else "REVISAR"
        )
        outcomes.append(dict(device=device, cis_id=cid, control=title,
                             status=status, razon=rationale,
                             evidencia=evidence, fuente=source, observacion=remark))

    for device in ("R1-CISCO", "SW1-CISCO"):
        obj = by_key.get((device, "HTTP deshabilitado"))
        add(device, "1.2.2.5", "Desactivar servidor HTTP",
            obj["status"] == "CUMPLE" if obj and obj["status"] != "REVISAR" else None,
            "Evitar administracion y autenticacion por HTTP sin cifrar.",
            p19.name + ": HTTP deshabilitado", CISCO_SOURCE)

    disabled = r1.get("source_route_explicitly_disabled")
    add("R1-CISCO", "1.3.1.2", "Prohibir IP source-route",
        disabled if isinstance(disabled, bool) else None,
        "Evitar rutas elegidas por el origen del paquete.",
        pr1.name + ": source_route_explicitly_disabled", CISCO_SOURCE,
        "El estado inicial sin 'no ip source-route' no probaba habilitacion.")
    interfaces = r1.get("interfaces", {})
    expected = ("GigabitEthernet0/0", "GigabitEthernet0/1")
    proxy = None if not all(i in interfaces for i in expected) else all(
        interfaces[i].get("proxy_arp") == "disabled" for i in expected
    )
    add("R1-CISCO", "2.3.3.2", "Desactivar Proxy ARP",
        proxy, "Evitar extender el perimetro LAN mediante respuestas ARP de proxy.",
        pr1.name + ": interfaces", CISCO_SOURCE)

    threshold = after.get("admin-lockout-threshold")
    duration = after.get("admin-lockout-duration")
    verified = (threshold == "3" and duration == "900") if threshold and duration else None
    add("FGT-01", "2.2.2", "Limitar reintentos y bloqueo administrativo",
        verified, "Retrasar intentos repetidos de autenticacion.",
        pfg.name + ": admin-lockout-threshold/admin-lockout-duration",
        FORTI_SOURCE, f"Observado: threshold={threshold}, duracion={duration}s; objetivo CIS: 3 y 900s.")
    admintimeout = after.get("admintimeout")
    add("FGT-01", "2.4.4", "Timeout administrativo de inactividad",
        admintimeout == "5" if admintimeout else None,
        "Reducir riesgo de sesiones administrativas desatendidas.",
        pfg.name + ": admintimeout", FORTI_SOURCE)

    adminports = [by_key.get(("FGT-01", f"Acceso administrativo port{i}"))
                  for i in (1, 2, 3)]
    secure = (all(x["status"] == "CUMPLE" for x in adminports)
              if all(adminports) and all(x["status"] != "REVISAR" for x in adminports)
              else None)
    add("FGT-01", "2.4.5", "Solo canales cifrados en interfaces de gestion",
        secure, "Evitar credenciales por protocolos administrativos sin cifrar.",
        p19.name + ": Acceso administrativo port1/port2/port3",
        FORTI_SOURCE,
        "Excepcion conocida: port1 conserva HTTP por limitaciones del laboratorio; "
        "no declarar cumplimiento de este control.")

    counts = Counter(x["status"] for x in outcomes)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result = dict(
        fecha_utc=stamp,
        alcance="7 comprobaciones seleccionadas con referencias CIS; no certificacion",
        origenes={"cis19": p19.name, "r1": pr1.name, "fortigate": pfg.name},
        resumen=dict(counts),
        resultados=outcomes,
        riesgos_no_resueltos=[
            "HTTP en port1 de FortiGate impide CIS 2.4.5",
            "Cisco v2.2 es una referencia historica, no validacion IOSv 15.9",
            "Algoritmos SSH heredados en dispositivos IOSv",
        ]
    )
    folder.mkdir(parents=True, exist_ok=True)
    json_out = folder / ("cis_benchmark_" + stamp + ".json")
    md_out = folder / ("cis_benchmark_" + stamp + ".md")
    if outfile:
        md_out = outfile

    lines = ["# Verificacion de recomendaciones CIS seleccionadas", "",
             "**Matricula:** 2025-1331",
             "**Alcance:** 7 controles documentados; no auditoria integral.", "",
             "| Equipo | CIS ID | Recomendacion | Estado |",
             "|---|---|---|---|"]
    for x in outcomes:
        lines.append(f"| {x['device']} | {x['cis_id']} | "
                     f"{x['control']} | {x['status']} |")
    lines += ["", "## Justificacion y trazabilidad", ""]
    for x in outcomes:
        lines += [f"### {x['device']} — {x['cis_id']}",
                  f"- **Referencia:** {x['fuente']}",
                  f"- **Motivo:** {x['razon']}",
                  f"- **Evidencia:** {x['evidencia']}",
                  f"- **Estado:** {x['status']}",
                  f"- **Nota:** {x['observacion']}" if x["observacion"] else "", ""]
    lines += ["## Fuentes",
              "- [CIS Cisco IOS Benchmark v2.2 (2007)](https://www.cisecurity.org/-/jssmedia/Project/cisecurity/cisecurity/data/media/files/uploads/2017/04/CIS_Cisco_IOS_Benchmark_v22.pdf)",
              "- [CIS Fortigate 7.0.x — catalogo](https://www.cisecurity.org/benchmark/fortinet)",
              "- [CIS: version 1.4.0 sin cambios desde version anterior](https://www.cisecurity.org/insights/blog/cis-benchmarks-january-2026-update)",
              "- [CIS Fortigate 7.0.x v1.3.0 — referencia consultada](https://1cdn.com.au/wp-content/uploads/2023/01/CIS_Fortigate_7.0.x_Benchmark_v1.3.0.pdf)",
              "", "## Limitaciones",
              "- Se registran excepciones e incumplimientos: no se ocultan.",
              "- Las referencias Cisco son de una edicion historica; comprobar aplicabilidad por plataforma.",
              "- El informe combina evidencias de fechas diferentes cuando se genera sin una auditoria nueva.",
              ""]
    os.umask(0o077)
    json_out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    md_out.write_text("\n".join(lines), encoding="utf-8")
    json_out.chmod(0o600)
    md_out.chmod(0o600)
    print("\n=== CONTROLES CIS SELECCIONADOS ===")
    for item in outcomes:
        print(f"{item['device']:12} | {item['cis_id']:10} | {item['status']:9} | {item['control']}")
    print(f"Resumen: {dict(counts)}")
    print("Informe Markdown:", md_out)
    print("Informe JSON:", json_out)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT)
    args = parser.parse_args()
    generate(args.report_dir)


if __name__ == "__main__":
    main()
