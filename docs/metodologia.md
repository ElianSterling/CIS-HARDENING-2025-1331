# Metodología y trazabilidad

## 1. Construcción del laboratorio

Se preparó una infraestructura en Proxmox + GNS3 con R1-CISCO, SW1-CISCO, FGT-01, PC1 y PC2. Se conectó el contenedor Debian CIS-AUDITOR a las redes de gestión necesarias.

## 2. Diagnóstico del canal de administración

Los paquetes SYN de CIS-AUDITOR llegaban al router, pero R1 registraba `TCP: checksum failure`. Se desactivó TX checksum offloading **únicamente en eth1 del CT 180**, lo que permitió restablecer SSH sin retirar AAA ni otros controles del equipo. Un servicio de systemd aplica el ajuste en futuros arranques del contenedor.

## 3. Auditoría inicial sin cambios

`cis_audit_baseline.py` recopiló cinco salidas por dispositivo, utilizando SSH. `cis_checks.py` evaluó 19 verificaciones predefinidas y produjo una línea base con 13 CUMPLE, 2 NO CUMPLE y 4 RIESGO.

## 4. Aplicación controlada

- `cis_apply_sw1.py` solicitó confirmación y desactivó HTTP/HTTPS en SW1.
- `cis_apply_r1.py` solicitó confirmación y aplicó desactivaciones de Proxy ARP, ICMP Redirects y Source Routing.
- `fortigate_cis.py apply` solicitó confirmación y ajustó Telnet, bloqueo administrativo y plazo de autenticación SSH.

Los scripts guardaron evidencia y realizaron verificaciones posteriores. Las aplicaciones con fallos pueden dejar cambios en la running-config o configuración activa; deben revisarse desde consola y **no se consideran transacciones con rollback garantizado**.

## 5. Verificación posterior

- El evaluador repitió las mismas 19 comprobaciones con 15 CUMPLE, 0 NO CUMPLE y 4 RIESGO.
- `r1_precheck.py` verificó las dos interfaces del router tras los ajustes.
- `fortigate_cis.py verify` verificó la persistencia de los parámetros administrativos.
- Se comprobaron los accesos SSH a los tres equipos y la conectividad de PC1 ↔ PC2.

## 6. Automatizador integrado y correlación CIS

El programa `cis_centro.py` ofrece `audit`, `apply --allow-changes`, `verify` y `report`. Reutiliza las automatizaciones anteriores y genera un reporte adicional con **7 controles referenciados** mediante `cis_benchmark_reporte.py`. Las 19 comprobaciones originales no se presentan como 19 recomendaciones oficiales.

En CIS Fortigate 7.0.x, el control 2.2.2 requiere 3 intentos y bloqueo de **900 segundos**. El 13/11/2026 se ejecutó el auditor integrado y se cambió el bloqueo de **300 s a 900 s**, verificado en la posterior lectura por SSH. El reporte de siete controles pasó de 5 CUMPLE/2 NO CUMPLE a **6 CUMPLE/1 NO CUMPLE**. La administración HTTP en port1 sigue como excepción del control CIS 2.4.5.

Consultar [referencias CIS y limitaciones](justificacion-hardening.md) y [comandos del auditor](operacion-auditor.md).

## 7. Evidencias y publicación

Los informes Markdown y JSON generados se conservan en CIS-AUDITOR. Para hacerlos públicos, revisar contenidos y sanitizar direcciones, identificadores, firmas de configuración y cualquier dato sensible.

Las capturas y el video demostrativo deben añadirse con resultados reales: no se usan imágenes o logs simulados.
