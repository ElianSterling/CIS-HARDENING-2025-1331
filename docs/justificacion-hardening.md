# Matriz de referencias CIS, hardening y excepciones

**Laboratorio:** CIS-HARDENING-2025-1331  
**Dispositivos:** Cisco IOSv 15.9, IOSvL2 15.2 y FortiGate FortiOS 7.0.3  
**Alcance:** comprobaciones seleccionadas, sin certificación de cumplimiento global.

## Fuentes comprobadas

1. **CIS Cisco IOS Benchmark v2.2 (noviembre de 2007)**, publicado por CIS:  
   https://www.cisecurity.org/-/jssmedia/Project/cisecurity/cisecurity/data/media/files/uploads/2017/04/CIS_Cisco_IOS_Benchmark_v22.pdf  
   **Importante:** es una referencia histórica; su aplicación a Cisco IOSv 15.9 y IOSvL2 15.2 requiere considerar diferencias de plataforma y edición.
2. **CIS Fortigate 7.0.x Benchmark v1.3.0 (2024)**, cuyos controles específicos fueron cotejados:  
   https://1cdn.com.au/wp-content/uploads/2023/01/CIS_Fortigate_7.0.x_Benchmark_v1.3.0.pdf  
   El fabricante del benchmark anunció **v1.4.0 en enero de 2026 sin cambios respecto de la edición anterior**:  
   https://www.cisecurity.org/insights/blog/cis-benchmarks-january-2026-update  
   Catálogo oficial: https://www.cisecurity.org/benchmark/fortinet
3. **Referencias técnicas de fabricantes** para ajustes que no se atribuyen a un identificador CIS específico:
   - Cisco — https://sec.cloudapps.cisco.com/security/center/resources/IOS_XE_hardening
   - Fortinet — https://docs.fortinet.com/document/fortigate/7.0.3/cli-reference/1620/system-global

No se redistribuyen los PDF de terceros. Se identifican solamente números, objetivos y nuestros propios resultados de laboratorio.

## Controles identificados del CIS Benchmark

| Equipo | ID CIS | Objetivo | Configuración o resultado verificado | Situación |
|---|---|---|---|---|
| R1-CISCO | Cisco IOS v2.2 **1.2.2.5** | Desactivar servidor HTTP | `no ip http server` | CUMPLE |
| SW1-CISCO | Cisco IOS v2.2 **1.2.2.5** | Desactivar servidor HTTP | `no ip http server` | CUMPLE |
| R1-CISCO | Cisco IOS v2.2 **1.3.1.2** | Prohibir IP Source Routing | `no ip source-route` | CUMPLE |
| R1-CISCO | Cisco IOS v2.2 **2.3.3.2** | Desactivar IP Proxy ARP | `no ip proxy-arp` en Gi0/0 y Gi0/1 | CUMPLE |
| FGT-01 | Fortigate 7.0.x **2.2.2** | Limitar reintentos y duración de bloqueo | Threshold **3**, duración **900 s**; salida SSH verificada el 13/11/2026 | **CUMPLE** |
| FGT-01 | Fortigate 7.0.x **2.4.4** | Configurar timeout de inactividad | `admintimeout 5` | CUMPLE |
| FGT-01 | Fortigate 7.0.x **2.4.5** | Usar solo canales administrativos cifrados | port1 conserva HTTP por restricción de la edición de evaluación | **NO CUMPLE: EXCEPCIÓN DOCUMENTADA** |

**Estado verificado el 13/11/2026:** `cis_centro.py apply --allow-changes` ajustó `admin-lockout-duration` de 300 a **900**, y la verificación posterior confirmó la configuración. La matriz de siete controles terminó con **6 CUMPLE y 1 NO CUMPLE** (HTTP administrativo en FortiGate).

### Motivo de cada control

- **HTTP Cisco:** eliminar interfaces web innecesarias; sin cifrado, HTTP puede exponer credenciales.
- **Source Routing:** evitar rutas definidas por el origen que permitan eludir controles previstos por la infraestructura.
- **Proxy ARP:** reducir el riesgo de extender el perímetro entre segmentos L2 de forma no prevista.
- **Bloqueo administrativo:** ralentizar intentos reiterados de autenticación tras alcanzar el umbral.
- **Timeout de sesión:** reducir exposición de una sesión administrativa desatendida.
- **Cifrado administrativo FortiGate:** evitar credenciales transportadas mediante HTTP/Telnet; en este laboratorio no se completó por la limitación de acceso HTTPS.

## Buenas prácticas aplicadas adicionales (sin forzar equivalencia CIS)

| Equipo | Ajuste | Motivo |
|---|---|---|
| SW1-CISCO | Desactivar `ip http secure-server` | Servicio web no utilizado; SSH v2 permanece disponible |
| R1-CISCO | `no ip redirects` en Gi0/0 y Gi0/1 | Reducir anuncios ICMP Redirect innecesarios |
| FGT-01 | `admin-telnet disable` | Desactivar servicio remoto sin cifrado |
| FGT-01 | `admin-ssh-grace-time 30` | Reducir ventana de autenticación SSH |
| FGT-01 | `admin-ssh-v1 disable` | Mantener solo SSH versión 2 |

**No confundir:** desactivar Telnet globalmente **no demuestra** el cumplimiento de CIS 2.4.5 si HTTP sigue habilitado en `port1`.

## Herramientas y trazabilidad

- `scripts/cis_centro.py audit`: recopila nueva evidencia 15/15 por SSH sin aplicar cambios; ejecuta la evaluación de 19 comprobaciones, revisiones R1 y FGT y el reporte CIS de 7 controles.
- `scripts/cis_centro.py apply --allow-changes`: solo con autorización explícita; ejecuta scripts de aplicación SW1, R1 y FGT; luego verifica.
- `scripts/cis_centro.py verify`: comprobación de solo lectura posterior.
- `scripts/cis_centro.py report`: informe de los **7** controles referenciados, usando reportes locales existentes.
- `scripts/cis_checks.py`: evaluador original de **19 verificaciones de configuración**, que **no equivale** a 19 cláusulas CIS identificadas.
- `scripts/cis_benchmark_reporte.py`: evaluación de **7 referencias CIS verificadas**; deja visibles las desviaciones.

En el evaluador original se observaron 13 CUMPLE, 2 NO CUMPLE, 4 RIESGO antes, y 15 CUMPLE, 0 NO CUMPLE, 4 RIESGO después de SW1. Estos números se refieren **solo al evaluador original**, no a la matriz CIS de siete controles.

## Limitaciones y medidas compensatorias

- **FortiGate HTTP:** la interfaz `port1` permanece accesible por HTTP debido al comportamiento de la edición virtual de evaluación usada. Mantener el acceso en una **red de administración aislada**, no expuesta a Internet. Registrar explícitamente que **CIS 2.4.5 NO CUMPLE**. No forzar el cambio a HTTPS si la versión de evaluación no permite mantener administración.
- **SSH Cisco:** dispositivos IOSv usan algoritmos heredados; solo en entorno controlado.
- **Proxy ARP y Source Routing:** desactivar explícitamente `no ip source-route` no permite asegurar que la característica estuviera activada inicialmente solo porque faltaba la línea.
- **CIS-CAT:** no se ejecutó un escáner CIS-CAT oficial. La herramienta es un evaluador Python propio inspirado en recomendaciones CIS, cuya matriz documenta la fuente y el estado exacto.
- **Running-configs:** las versiones ya publicadas en `configuraciones/` son **extractos sanitizados**, no backups íntegros. Una revisión de archivos adicionales será necesaria antes de publicar versiones estructurales más extensas.
