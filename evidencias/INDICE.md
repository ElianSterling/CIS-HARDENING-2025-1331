# Evidencias del laboratorio CIS Hardening

Capturas de pantalla originales del laboratorio GNS3 / Proxmox / Cisco / FortiGate.

**Estudiante:** Elian Sterling Severino Mejía — **Matrícula:** 2025-1331.

## Arquitectura y configuración

| Evidencia | Captura |
|---|---|
| Topología de GNS3 con direcciones IP | [20-topologia-gns3-con-ip.png](20-topologia-gns3-con-ip.png) |
| Router: rutas y conectividad | [01-router-rutas-y-conectividad.png](01-router-rutas-y-conectividad.png) |
| PC1 y PC2: direccionamiento | [02-pc1-direccionamiento.png](02-pc1-direccionamiento.png) y [03-pc2-direccionamiento.png](03-pc2-direccionamiento.png) |
| FortiGate: interfaces, rutas y objetos | Capturas 04 a 09 |
| FortiGate: políticas ICMP y contadores | Capturas 10, 11 y 14 |

> Nota: el FortiGate se ejecuta como VM externa de Proxmox; por eso no aparece como nodo de GNS3. La nube CLOUD-WAN corresponde al enlace hacia FGT-01 y CLOUD-FGT-LAN a la red remota.

## Auditoría y hardening

| Evidencia | Captura |
|---|---|
| Auditoría inicial | [15-auditoria-inicial.png](15-auditoria-inicial.png) |
| Verificación del router | [16-verificacion-r1.png](16-verificacion-r1.png) |
| Aplicación de ajustes de FortiGate | [17-fortigate-hardening-apply.png](17-fortigate-hardening-apply.png) |
| Resumen final a partir de informes guardados | [21-informe-hardening-resumen.png](21-informe-hardening-resumen.png) |

Los resultados del evaluador inicial fueron 13 CUMPLE, 2 NO CUMPLE y 4 RIESGO. Tras deshabilitar HTTP/HTTPS en SW1, el mismo conjunto de 19 comprobaciones produjo 15 CUMPLE, 0 NO CUMPLE y 4 RIESGO. Las verificaciones específicas de R1 y FGT se documentan por separado.

## Pruebas de conectividad

| Evidencia | Captura |
|---|---|
| PC1 a PC2 — prueba inicial | [12-ping-pc1-a-pc2-inicial.png](12-ping-pc1-a-pc2-inicial.png) |
| PC2 a PC1 — prueba inicial | [13-ping-pc2-a-pc1-inicial.png](13-ping-pc2-a-pc1-inicial.png) |
| PC1 a PC2 — prueba posterior | [18-ping-pc1-a-pc2-posterior.png](18-ping-pc1-a-pc2-posterior.png) |
| PC2 a PC1 — prueba posterior | [19-ping-pc2-a-pc1-posterior.png](19-ping-pc2-a-pc1-posterior.png) |

## Limitaciones

- Algunas capturas corresponden a etapas de construcción, no exclusivamente al resultado final.
- El hardening seleccionado no representa cumplimiento integral de CIS Benchmark.
- Las imágenes registran direcciones privadas y nombres de dispositivos de un entorno de laboratorio.
- La administración HTTP de FortiGate se mantuvo disponible en la red de gestión por las limitaciones del entorno de evaluación.
- Nunca incluir contraseñas ni respaldos originales de configuración sin sanitizar.
