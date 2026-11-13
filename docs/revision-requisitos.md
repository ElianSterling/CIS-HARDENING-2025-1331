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
| Informe sin cambios | `cis_centro.py audit` + reportes JSON/MD | Script disponible; pendiente prueba de esta versión integrada |
| Aplicación e informe posterior | `cis_centro.py apply --allow-changes` + `verify` | Script disponible; pendiente ejecución del flujo integrado |

## Correcciones todavía pendientes en vivo

1. Cambiar el FortiGate de bloqueo 300 s a **900 s** con la versión actualizada de `fortigate_cis.py`, verificar y generar informes nuevos. No declararlo conforme antes de la evidencia.
2. Mantener **CIS 2.4.5 NO CUMPLE** mientras `port1` permita HTTP. Registrar el aislamiento de la red como medida compensatoria; nunca afirmar cumplimiento total.
3. Ejecutar y documentar el orquestador y las pruebas offline del evaluador.
4. Preparar versiones amplias de los running-configs, censurar cualquier línea no permitida y revisarlas antes de su publicación.

## Video y entrega

- Video individual en YouTube, duración **máxima 10 min**.
- Mostrar fecha y hora, rostro y voz.
- En el video demostrar la topología, los comandos de auditoría, el hardening y las pruebas de red. No reejecutar cambios peligrosos solo para obtener escenas.
- Enlace al inicio de `README.md`.
- TXT con enlaces y nombre **`<Nombre>_<Matricula>_<P#>.txt`**. Confirmar identificador de práctica/parcial exacto para no inventar la nomenclatura.

## Integridad académica

Conservar los informes y capturas originales del laboratorio; no fabricar registros ni atribuir cumplimiento de controles no verificados. La evaluación se basa en la infraestructura real de una única persona.
