# Configuraciones finales, extractos y privacidad

**Laboratorio:** CIS-HARDENING-2025-1331 — Seguridad de Redes

## Archivos públicos

- [R1-CISCO-running-config-sanitizado.txt](R1-CISCO-running-config-sanitizado.txt): extracto de los comandos de seguridad y conectividad observados en el Cisco IOSv.
- [SW1-CISCO-running-config-sanitizado.txt](SW1-CISCO-running-config-sanitizado.txt): extracto de la configuración del switch, incluyendo desactivación de servidores HTTP/HTTPS.
- [FGT-01-config-sanitizada.txt](FGT-01-config-sanitizada.txt): extracto de parámetros globales, interfaces, reglas ICMP y rutas del FortiGate.

**Última comprobación FortiGate:** 13/11/2026, ejecución de `cis_centro.py apply --allow-changes` y auditoría `verify`. El bloqueo administrativo pasó a 900 segundos con umbral de tres intentos; `port1` conserva HTTP como excepción CIS 2.4.5.

### Running-configs Cisco ampliados y censurados

- [R1-CISCO — running-config censurado](R1-CISCO-running-config-CENSURADO.txt)
- [SW1-CISCO — running-config censurado](SW1-CISCO-running-config-CENSURADO.txt)

Estos archivos de presentación se reconstruyeron a partir de las líneas permitidas en los resultados del sanitizador que el estudiante revisó. Se agruparon los marcadores de omisión para que la lectura sea clara: **no son una exportación literal byte a byte ni un backup restaurable**. El sanitizador informó 34 líneas permitidas/63 censuradas para R1 y 24 permitidas/51 censuradas para SW1.

## Alcance y autenticidad

Los tres archivos son **extractos sanitizados de configuraciones reales**. No son copias restaurables completas. Los `show running-config` originales de Cisco se conservaron en la carpeta privada `/opt/cis-auditor/backups/20261113T123310Z` del CT180. FortiGate no utiliza el comando Cisco `show running-config`; sus evidencias proceden de consultas `show system ...`, `show firewall policy` y `show router static`.

Los archivos originales pueden contener **hashes, contraseñas, comunidades SNMP, identificadores PKI y claves**. Por ello **no se publican literalmente**. La edición pública se genera por lista cerrada de campos permitidos, con revisión antes de subir.

Para aproximarse a los running-configs completos que solicita la asignación, se ofrece `scripts/cis_running_censurados.py`, que preserva la estructura de secciones Cisco y coloca marcadores por cada grupo de líneas omitidas. Estos candidatos también requieren revisión manual antes de publicarse.

## Verificación adicional pendiente

- Ejecutar `python cis_running_censurados.py` en CT180 para crear candidatos ampliados.
- Ejecutar `python cis_exportar_publicables.py` para una exportación nueva basada en el baseline posterior del 13/11/2026.
- Revisar los archivos generados línea por línea, especialmente antes de incorporarlos al repositorio público.
- No afirmar que la copia pública contiene todos los comandos del equipo cuando existan líneas censuradas.
