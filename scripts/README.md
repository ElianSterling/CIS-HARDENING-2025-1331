# Scripts del laboratorio

Los scripts Python originales y sus informes se publicaron tras revisar el material del CT 180. Los módulos conservan las direcciones y expectativas del laboratorio; **no son herramientas generales listas para producción**.

## Entrada principal

`cis_centro.py` orquesta los módulos mediante:

- `python cis_centro.py audit` — solo lectura; genera baseline 15/15, evaluación de 19 comprobaciones, precheck R1, auditoría FGT y matriz de 7 referencias CIS.
- `python cis_centro.py apply --allow-changes` — requiere confirmación general e individual para modificar los dispositivos. FortiGate tiene como objetivo `admin-lockout-duration 900`.
- `python cis_centro.py verify` — consulta posterior; no aplica cambios.
- `python cis_centro.py report` — informe local a partir de archivos JSON existentes.

**Controles CIS verificados y limitaciones:** [Matriz técnica](../docs/justificacion-hardening.md). **Operación detallada:** [Guía](../docs/operacion-auditor.md).

## Módulos

| Archivo | Función |
|---|---|
| `cis_audit_baseline.py` | Recopila evidencias por SSH, sin cambios |
| `cis_checks.py` | Evalúa 19 verificaciones locales seleccionadas |
| `cis_benchmark_reporte.py` | Evalúa 7 controles con referencia CIS identificada |
| `cis_apply_sw1.py` | Desactiva HTTP/HTTPS de SW1 con autorización |
| `cis_apply_r1.py` | Aplica y verifica medidas R1 con autorización |
| `r1_precheck.py` | Verificación de Source Routing, Proxy ARP, Redirects |
| `fortigate_cis.py` | `audit` / `apply` / `verify` con objetivo CIS de 900 s |
| `cis_comparativo.py` | Compara la matriz original de 19 verificaciones |
| `cis_informe_final.py` | Consolida los informes históricos del laboratorio |
| `cis_exportar_publicables.py` | Crea extractos de configuración de campos permitidos |
| `cis_running_censurados.py` | Crea candidatos Cisco con líneas desconocidas censuradas |

**Advertencias:** los modos de aplicación no garantizan rollback automático; un error puede dejar cambios parciales. No publicar `backups/`, contraseñas, hashes ni otras credenciales. Nunca indicar `CUMPLE` en CIS 2.4.5 mientras FortiGate port1 permita HTTP.
