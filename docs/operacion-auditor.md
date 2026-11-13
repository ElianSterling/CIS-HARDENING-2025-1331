# Operación del auditor integrado

**Asignatura:** Seguridad de Redes  
**Estudiante:** Elian Sterling Severino Mejía — **2025-1331**

## Entorno de ejecución

Los scripts originales fueron diseñados para el CT 180 `cis-auditor` con Debian 12, Python y un virtualenv en `/opt/cis-auditor/.venv`. Las conexiones SSH utilizan verificación de huellas del archivo `/root/.ssh/known_hosts`.

Antes de ejecutar los programas en otro equipo, adaptar el inventario, las credenciales, los rangos, las claves de host verificadas y la estrategia de recuperación. **No ejecutar cambios automáticos en una red productiva.**

## Interfaz única

```bash
cd /opt/cis-auditor
source .venv/bin/activate

python cis_centro.py audit
python cis_centro.py report
python cis_centro.py verify

# Solo cuando se autorice la aplicación:
python cis_centro.py apply --allow-changes
```

### Modo `audit` — solo lectura

1. `cis_audit_baseline.py` recopila cinco salidas por dispositivo (15 en total).
2. `cis_checks.py` evalúa las **19 verificaciones locales** de configuración.
3. `r1_precheck.py` revisa Source Routing, Proxy ARP e ICMP Redirects.
4. `fortigate_cis.py audit` consulta parámetros administrativos globales.
5. `cis_benchmark_reporte.py` contrasta los informes disponibles con **7 referencias CIS identificadas**.

El modo no modifica configuraciones y genera informes JSON/Markdown.

### Modo `apply` — cambios con consentimiento

**No se ejecuta por defecto.** Requiere `--allow-changes`, confirmación general `APLICAR-HARDENING` y confirmaciones de cada módulo cuando existen cambios. Orquesta, en este orden:

1. SW1-CISCO — desactivar servidores HTTP/HTTPS si continúan habilitados.
2. R1-CISCO — desactivar Proxy ARP, ICMP Redirects y Source Routing si hace falta.
3. FGT-01 — desactivar Telnet global, ajustar tiempo SSH y establecer **`admin-lockout-duration 900`**, conforme con CIS 2.2.2.

Al finalizar, ejecuta `verify` y guarda nuevos reportes. Los scripts son idempotentes en sus ajustes previstos, pero **no forman una transacción atómica ni aseguran rollback automático**. Un error puede dejar cambios parciales; revisar la consola del dispositivo y el respaldo privado antes de reintentar.

**Restricción del laboratorio:** no se modifica `allowaccess http` en FortiGate `port1`. Permanece como desviación explícita del control CIS 2.4.5 para no perder acceso a la GUI HTTP de la VM de evaluación.

### Modo `verify` — comprobación posterior

Recopila nueva evidencia, ejecuta los chequeos originales y valida los valores del FortiGate contra el objetivo de 900 segundos. **No aplica comandos de configuración.**

Si FortiGate devuelve un estado incorrecto, el flujo lo informa como error y genera el reporte CIS para no ocultar desviaciones.

### Modo `report` — sin SSH

Usa los informes JSON ya guardados para generar una matriz de **7 controles identificados**. No es necesario conectarse a los dispositivos ni escribir contraseñas.

## Registros generados

- `reportes/baseline_*.json/md` — manifiesto de 15 evidencias.
- `reportes/cis_inicial_*.json/md` — 19 verificaciones de configuración.
- `reportes/r1_precheck_*.json` — indicadores del router.
- `reportes/fortigate_{audit,apply,verify}_*.json` — valores y ejecución en FGT.
- `reportes/cis_benchmark_*.json/md` — **7 comprobaciones vinculadas a recomendaciones CIS** con estados reales.

## Pruebas offline del evaluador

```bash
python -m compileall -q scripts tests
python -m unittest discover -s tests -v
```

Las pruebas verifican escenarios 300/900 segundos y la excepción HTTP sin conectarse al laboratorio.

## Running-configs y privacidad

Las salidas originales residen en la carpeta privada `/opt/cis-auditor/backups/`. Nunca subir esos archivos directamente a un repositorio público.

`scripts/cis_exportar_publicables.py` genera extractos mediante lista cerrada de campos permitidos. `scripts/cis_running_censurados.py` produce versiones Cisco estructurales que sustituyen líneas no permitidas por marcadores de omisión. **Antes de publicar una versión ampliada, revisar visualmente su contenido.**

## Consideraciones sobre CIS

Las referencias y justificaciones se encuentran en [Justificación del hardening](justificacion-hardening.md). En particular:

- La correlación Cisco se basa en un **benchmark histórico** (IOS v2.2 de 2007), no en una validación formal de compatibilidad IOSv 15.9.
- El informe de 19 controles del laboratorio no debe presentarse como 19 cláusulas del CIS Benchmark.
- La matriz CIS de 7 verificaciones mantiene las excepciones no conformes visibles y no equivale a CIS-CAT Pro.
