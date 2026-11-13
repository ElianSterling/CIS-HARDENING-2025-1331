#!/usr/bin/env python3
"""Pruebas offline del evaluador CIS; no se conecta a ningun dispositivo."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cis_benchmark_reporte import generate  # noqa: E402


class SelectedCisTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.details = self.payload(300, "RIESGO")
        self.write()

    def payload(self, duration, port1):
        findings = [
            {"device": "R1-CISCO", "control": "HTTP deshabilitado", "status": "CUMPLE"},
            {"device": "SW1-CISCO", "control": "HTTP deshabilitado", "status": "CUMPLE"},
            {"device": "FGT-01", "control": "Acceso administrativo port1", "status": port1},
            {"device": "FGT-01", "control": "Acceso administrativo port2", "status": "CUMPLE"},
            {"device": "FGT-01", "control": "Acceso administrativo port3", "status": "CUMPLE"},
        ]
        findings += [
            {"device": "R1-CISCO", "control": f"control-demo-{i}", "status": "CUMPLE"}
            for i in range(14)
        ]
        return {
            "cis": {"findings": findings},
            "r1": {
                "device": "R1-CISCO",
                "mode": "solo lectura",
                "source_route_explicitly_disabled": True,
                "interfaces": {
                    "GigabitEthernet0/0": {"proxy_arp": "disabled", "icmp_redirects": "never"},
                    "GigabitEthernet0/1": {"proxy_arp": "disabled", "icmp_redirects": "never"},
                }
            },
            "fg": {
                "device": "FGT-01",
                "mode": "verify",
                "status": "VERIFICADO",
                "after": {
                    "admin-lockout-threshold": "3",
                    "admin-lockout-duration": str(duration),
                    "admintimeout": "5",
                    "admin-telnet": "disable",
                    "admin-ssh-v1": "disable",
                    "admin-ssh-grace-time": "30",
                }
            }
        }

    def write(self):
        files = (
            ("cis_inicial_20261113T010001Z.json", "cis"),
            ("r1_precheck_20261113T010002Z.json", "r1"),
            ("fortigate_verify_20261113T010003Z.json", "fg")
        )
        for name, key in files:
            (self.folder / name).write_text(
                json.dumps(self.details[key]), encoding="utf-8"
            )

    def test_300_s_is_not_cis(self):
        result = generate(self.folder)
        self.assertEqual(len(result["resultados"]), 7)
        self.assertEqual(result["resumen"]["CUMPLE"], 5)
        self.assertEqual(result["resumen"]["NO CUMPLE"], 2)

    def test_900_s_passes_but_http_remains_exception(self):
        self.details = self.payload(900, "RIESGO")
        self.write()
        result = generate(self.folder)
        self.assertEqual(result["resumen"]["CUMPLE"], 6)
        self.assertEqual(result["resumen"]["NO CUMPLE"], 1)
        failing = [x["cis_id"] for x in result["resultados"] if x["status"] == "NO CUMPLE"]
        self.assertEqual(failing, ["2.4.5"])

    def test_no_http_all_seven_pass(self):
        self.details = self.payload(900, "CUMPLE")
        self.write()
        result = generate(self.folder)
        self.assertEqual(result["resumen"]["CUMPLE"], 7)
        self.assertNotIn("NO CUMPLE", result["resumen"])


if __name__ == "__main__":
    unittest.main()
