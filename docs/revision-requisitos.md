# Revisión de requisitos antes de la entrega

**Estudiante:** Elian Sterling Severino Mejía — **2025-1331**  
**Estado:** avances comprobados en repositorio; pendientes expresos antes de grabar el video.

## Repositorio y documentación

| Requisito | Evidencia | Estado |
|---|---|---|
| Un repositorio por infraestructura | Repositorio `CIS-HARDENING-2025-1331` | Cumple para una infraestructura |
| Propósito del laboratorio | `README.md` | Cumple |
| Imágenes y diagramas | 21 imágenes en `evidencias/`, diagrama Mermaid en README/docs | Cumple |
| Scripts usados | `scripts/` con módulos originales y orquestador | Cumple |
| Running-configs | `configuraciones/` contiene tres extractos sanitizados; candidato extendido en preparación | **Parcial** |
| Video al principio del repositorio | Encabezado de README reservado | **Pendiente de grabación** |

## Auditoría basada en CIS

| Requisito | Evidencia | Estado |
|---|---|---|
| Topología Router/Switch/Firewall | Diagrama, capturas y pruebas PC1↔PC2 | Cumple |
| Herramienta de análisis | `cis_checks.py`, `cis_benchmark_reporte.py` | Cumple como evaluador propio, no CIS-CAT |
| Reglas y justificación CIS | `docs/justificacion-hardening.md` con IDs de Cisco v2.2 y Fortigate 7.0.x | Documentado, con limitaciones de versión |
| Pruebas posteriores | Reportes SW1, R1, FGT y conectividad | Cumple |
| Informe sin cambios | `cis_centro.py audit` + reportes JSON/MD | **Probado en vivo el 13/11/2026: 15/15 evidencias** |
| Aplicación e informe posterior | `cis_centro.py apply --allow-changes` + `verify` | **Probado en vivo 13/11/2026: FGT 900 s; 6 CUMPLE, 1 NO CUMPLE** |

## Correcciones todavía pendientes en vivo

1. **COMPLETADO 13/11/2026:** FortiGate pasó de 300 a **900 s**, confirmado por auditoría posterior. El control CIS 2.2.2 ahora CUMPLE.
2. Mantener **CIS 2.4.5 NO CUMPLE** mientras `port1` permita HTTP. Registrar el aislamiento de la red como medida compensatoria; nunca afirmar cumplimiento total.
3. **COMPLETADO: pruebas offline del evaluador ejecutadas 13/11/2026.** `python -m unittest discover -s tests -v`: **3 pruebas, todas OK**, con escenarios simulados 300 s / 900 s y excepción HTTP. Estas pruebas no sustituyen la verificación real de los dispositivos.
4. **PUBLICADOS TRAS REVISIÓN:** versiones de presentación ampliadas y censuradas de R1 y SW1 en `configuraciones/`, basadas en la salida del baseline `20261113T123310Z`: R1 34 líneas permitidas/63 censuradas; SW1 24 permitidas/51 censuradas. El extracto de FortiGate refleja 900 s verificados. No son running-configs íntegros ni backups restaurables; los originales permanecen privados. Confirmar con el docente si acepta versiones censuradas.

## Video y entrega

- Video individual en YouTube, duración **máxima 10 min**.
- Mostrar fecha y hora, rostro y voz.
- En el video demostrar la topología, los comandos de auditoría, el hardening y las pruebas de red. No reejecutar cambios peligrosos solo para obtener escenas.
- Enlace al inicio de `README.md`.
- TXT con enlaces y nombre **`<Nombre>_<Matricula>_<P#>.txt`**. Confirmar identificador de práctica/parcial exacto para no inventar la nomenclatura.

## Integridad académica

Conservar los informes y capturas originales del laboratorio; no fabricar registros ni atribuir cumplimiento de controles no verificados. La evaluación se basa en la infraestructura real de una única persona.
