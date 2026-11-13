# Ejecución verificada del auditor integrado — 13/11/2026

**Estudiante:** Elian Sterling Severino Mejía  
**Matrícula:** 2025-1331  
**Infraestructura:** R1-CISCO, SW1-CISCO, FGT-01 y CIS-AUDITOR  
**Fuente de este documento:** salida real de terminal aportada por el estudiante el 13/11/2026. Es una **síntesis fiel de esa ejecución**, no un archivo JSON exportado del contenedor.

## 1. Auditoría anterior al último ajuste

Comando ejecutado: `python cis_centro.py audit`.

- Baseline: `baseline_20261113T123119Z.json`, **15/15 evidencias** (5 por dispositivo), solo lectura.
- Evaluador propio de 19 comprobaciones: `cis_inicial_20261113T123145Z.json`, **15 CUMPLE, 0 NO CUMPLE, 4 RIESGO**.
- Router: `r1_precheck_20261113T123145Z.json`; source routing deshabilitado explícitamente, Proxy ARP deshabilitado en Gi0/0 y Gi0/1, ICMP Redirects deshabilitados en ambas interfaces.
- FortiGate previo: `fortigate_audit_20261113T123157Z.json`; `admin-telnet disable`, `admin-lockout-duration 300`, `admin-lockout-threshold 3`, `admin-ssh-grace-time 30`, `admin-ssh-v1 disable`, `admintimeout 5`.
- Referencias CIS: `cis_benchmark_20261113T123201Z.json`, **5 CUMPLE y 2 NO CUMPLE**. Las desviaciones eran 2.2.2 (bloqueo 300 s) y 2.4.5 (HTTP de administración).

## 2. Aplicación con autorización

Comando: `python cis_centro.py apply --allow-changes`.

- Confirmación general: `APLICAR-HARDENING`.
- **SW1-CISCO:** HTTP y HTTPS administrativos ya estaban deshabilitados; sin cambios.
- **R1-CISCO:** source routing, Proxy ARP e ICMP Redirects ya estaban deshabilitados; sin cambios.
- **FGT-01:** se confirmó `APLICAR-FGT` para aumentar `admin-lockout-duration` de **300 a 900 segundos**. El script devolvió estado **VERIFICADO** y guardó `fortigate_apply_20261113T123259Z.json`.

## 3. Auditoría y verificación posterior

- Baseline: `baseline_20261113T123310Z.json`, **15/15 evidencias**, sin cambios de configuración.
- Evaluador de 19 comprobaciones: `cis_inicial_20261113T123336Z.json`, **15 CUMPLE, 0 NO CUMPLE, 4 RIESGO**.
- Router: `r1_precheck_20261113T123337Z.json` confirmó que los controles seguían activos.
- FortiGate: `fortigate_verify_20261113T123352Z.json`, estado **VERIFICADO**, con los siguientes parámetros:

| Parámetro | Estado final |
|---|---|
| `admin-telnet` | `disable` |
| `admin-lockout-duration` | **`900`** |
| `admin-lockout-threshold` | `3` |
| `admin-ssh-grace-time` | `30` |
| `admin-ssh-v1` | `disable` |
| `admintimeout` | `5` |

- Informe de controles con referencia CIS: `cis_benchmark_20261113T123356Z.json` y `.md`, **6 CUMPLE y 1 NO CUMPLE**.

## 4. Matriz de los siete controles seleccionados

| Dispositivo | Referencia CIS | Comprobación | Resultado |
|---|---|---|---|
| R1-CISCO | IOS 1.2.2.5 | HTTP deshabilitado | CUMPLE |
| SW1-CISCO | IOS 1.2.2.5 | HTTP deshabilitado | CUMPLE |
| R1-CISCO | IOS 1.3.1.2 | Source Routing deshabilitado | CUMPLE |
| R1-CISCO | IOS 2.3.3.2 | Proxy ARP deshabilitado | CUMPLE |
| FGT-01 | Fortigate 2.2.2 | Reintentos y bloqueo administrativo | **CUMPLE** |
| FGT-01 | Fortigate 2.4.4 | Timeout administrativo | CUMPLE |
| FGT-01 | Fortigate 2.4.5 | Acceso administrativo exclusivamente cifrado | **NO CUMPLE** |

## 5. Riesgos, alcance y autenticidad

El firewall FortiGate utiliza una edición de evaluación y conserva `set allowaccess ping ssh http` en `port1` por las restricciones de administración del laboratorio. Por ello **no se atribuye cumplimiento del CIS 2.4.5**. El tráfico administrativo HTTP debe mantenerse aislado y nunca exponerse a Internet.

La matriz de **19 verificaciones locales** y la de **7 controles referenciados CIS** tienen alcances distintos: no se deben sumar ni presentar como un resultado de conformidad integral. Las referencias Cisco provienen de una edición histórica, y la compatibilidad exacta con IOSv 15.9 no constituye una certificación.

**Archivos originales:** los JSON y respaldos completos señalados permanecen en el CT 180, `/opt/cis-auditor/reportes` y `/opt/cis-auditor/backups` respectivamente. Este resumen no sustituye sus hashes o el contenido íntegro de esos archivos. Las configuraciones públicas deben sanitizarse antes de subirlas al repositorio.
