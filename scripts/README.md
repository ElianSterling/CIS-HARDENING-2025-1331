# Scripts del laboratorio

Los archivos Python originales se incorporarán después de revisar las copias ejecutadas en CIS-AUDITOR.

| Archivo | Función |
|---|---|
| `cis_audit_baseline.py` | Recopilación de evidencia inicial/posterior mediante SSH |
| `cis_checks.py` | Evaluación de 19 controles seleccionados |
| `cis_apply_sw1.py` | Desactivar HTTP/HTTPS en el switch |
| `cis_apply_r1.py` | Desactivar Proxy ARP, ICMP Redirects e IP Source Routing |
| `r1_precheck.py` | Consultar estado de controles en el router |
| `fortigate_cis.py` | Subcomandos `audit`, `apply`, `verify` del FortiGate |
| `cis_comparativo.py` | Comparar dos evaluaciones de controles |
| `cis_informe_final.py` | Consolidar informes del laboratorio |

## Precauciones

El código depende de una topología de evaluación, versiones heredadas y rutas de archivos del CT 180. **No utilizar fuera del entorno de prácticas sin revisar cada comando y la estrategia de recuperación.**

No subir `backups/`, credenciales, archivos SSH locales ni running-configs originales. Las operaciones de aplicación requieren autorización explícita en consola y pueden producir cambios activos antes de una validación completa.

Para reproducir el entorno de dependencias, usar `requirements.txt` desde un virtualenv aislado.
