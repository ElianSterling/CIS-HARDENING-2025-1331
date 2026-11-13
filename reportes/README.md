# Informes del laboratorio CIS Hardening

**Estudiante:** Elian Sterling Severino Mejía — **2025-1331**

## Informes publicados

- [Informe técnico consolidado inicial/posterior](informe-final.md).
- [Validación integrada del 13/11/2026](validacion-integrada-20261113.md) — ejecución real del auditor integrado; FortiGate 900 s y resultado **6 CUMPLE / 1 NO CUMPLE** en siete controles CIS referenciados.
- Informes de línea base, verificación por equipo y comparaciones existentes en esta carpeta.

## Diferencias entre evaluadores

El evaluador original `cis_checks.py` verifica 19 aspectos locales de configuración. Tras el hardening de SW1 mostró **15 CUMPLE, 0 NO CUMPLE y 4 RIESGO**. Esa matriz **no representa 19 cláusulas de CIS Benchmark**.

El nuevo `cis_benchmark_reporte.py` correlaciona **siete comprobaciones** con recomendaciones seleccionadas y documentadas de los CIS Benchmarks. El 13/11/2026 mostró inicialmente **5 CUMPLE y 2 NO CUMPLE**, y después del ajuste FortiGate **6 CUMPLE y 1 NO CUMPLE**. La excepción pendiente es 2.4.5 por HTTP administrativo en `port1`.

## Trazabilidad de la ejecución del 13/11/2026

Los informes JSON originales de esa ejecución se guardaron en `/opt/cis-auditor/reportes` dentro del CT180. Entre ellos:

- `baseline_20261113T123310Z.json`
- `cis_inicial_20261113T123336Z.json`
- `r1_precheck_20261113T123337Z.json`
- `fortigate_apply_20261113T123259Z.json`
- `fortigate_verify_20261113T123352Z.json`
- `cis_benchmark_20261113T123356Z.json`
- `cis_benchmark_20261113T123356Z.md`

El informe [validación integrada](validacion-integrada-20261113.md) sintetiza la salida terminal auténtica proporcionada por el estudiante, sin sustituir los JSON originales. No se publican respaldos sin sanitizar, contraseñas ni claves de acceso.

## Limitaciones

- Las matrices informan **controles seleccionados**, no una certificación integral del CIS Benchmark.
- Las referencias Cisco proceden de una edición histórica (v2.2) y requieren validar su aplicabilidad a IOSv 15.9.
- El FortiGate es una edición de evaluación; conserva HTTP de administración en una red de laboratorio restringida.
