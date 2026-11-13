# Informe técnico de auditoría y hardening

**Infraestructura:** R1-CISCO, SW1-CISCO y FGT-01
**Matrícula:** 2025-1331
**Generado (UTC):** 2026-11-12T22:40:42.043258+00:00

## 1. Resumen de controles seleccionados

| Resultado | Antes | Después |
|---|---:|---:|
| CUMPLE | 13 | 15 |
| NO CUMPLE | 2 | 0 |
| RIESGO | 4 | 4 |
| REVISAR | 0 | 0 |

## 2. Cambios verificados en SW1-CISCO

| Control | Antes | Después |
|---|---|---|
| HTTP deshabilitado | NO CUMPLE | CUMPLE |
| HTTPS deshabilitado | NO CUMPLE | CUMPLE |

## 3. Cambios verificados en R1-CISCO

| Control | Antes | Después |
|---|---|---|
| Desactivación explícita de IP Source Routing | False | True |
| Proxy ARP — GigabitEthernet0/0 | enabled | disabled |
| ICMP Redirects — GigabitEthernet0/0 | always | never |
| Proxy ARP — GigabitEthernet0/1 | enabled | disabled |
| ICMP Redirects — GigabitEthernet0/1 | always | never |

## 4. Cambios verificados en FGT-01

| Control | Antes | Después |
|---|---|---|
| admin-telnet | enable | disable |
| admin-lockout-duration | 60 | 300 |
| admin-ssh-grace-time | 120 | 30 |
| admin-ssh-v1 | disable | disable |
| admintimeout | 5 | 5 |

## 5. Riesgos y limitaciones

- Los Cisco IOSv utilizan algoritmos SSH heredados.
- FortiOS 7.0.3 es una versión antigua de evaluación.
- La administración HTTP en port1 permanece habilitada.
- Los controles evaluados no constituyen una auditoría CIS completa.
- Las pruebas PC1-PC2 requieren evidencia independiente.

## 6. Trazabilidad de evidencias

- `sw_before`: `cis_inicial_20261112T220010Z.json`
- `sw_after`: `cis_inicial_20261112T221143Z.json`
- `r1_before`: `r1_precheck_20261112T221710Z.json`
- `r1_after`: `r1_precheck_20261112T222602Z.json`
- `fg_before`: `fortigate_audit_20261112T223222Z.json`
- `fg_apply`: `fortigate_apply_20261112T223231Z.json`
- `fg_after`: `fortigate_verify_20261112T223456Z.json`

## 7. Conclusión

La infraestructura fue sometida a auditorías iniciales, aplicación automatizada de medidas de hardening y comprobaciones posteriores. Las configuraciones originales y los informes se conservan en el servidor CIS-AUDITOR.
