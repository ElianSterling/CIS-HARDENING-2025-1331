# Justificación de controles de hardening y referencias CIS

**Alcance:** controles seleccionados de configuración en laboratorio. **No certifica conformidad integral ni equivale a ejecutar CIS-CAT Pro.**

## 1. Fuentes de referencia

- [CIS Benchmarks — familia Cisco](https://www.cisecurity.org/benchmark/cisco)
- [CIS Benchmarks — familia Fortinet](https://www.cisecurity.org/benchmark/fortinet)
- [Catálogo oficial de CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

En el catálogo de CIS se ofrece **CIS Fortigate 7.0.x Benchmark, versión 1.4.0**, familia compatible con la versión de laboratorio FortiOS 7.0.3. El catálogo público actual de Cisco muestra, entre otras, ediciones para IOS 16/17, pero **no demuestra equivalencia automática con Cisco IOSv 15.9**, que es la imagen usada.

**Estado de la correlación:** falta descargar y revisar la edición aplicable de los PDF oficiales, contrastar los textos/números de las recomendaciones e identificar cuáles coinciden exactamente con cada control. Por tanto, los controles de la tabla se documentan por sus **objetivos técnicos** y no se les atribuyen identificadores CIS aún no comprobados.

## 2. Recomendaciones técnicas aplicadas

| Equipo | Parámetro de hardening | Razón | Verificación | Estado |
|---|---|---|---|---|
| SW1-CISCO | `no ip http server` | Eliminar administración HTTP sin cifrado, reduciendo exposición y superficie de ataque | `show ip http server status` | Verificado |
| SW1-CISCO | `no ip http secure-server` | Eliminar un servicio web de administración que no se necesita en el laboratorio; SSH queda disponible | `show ip http server status`, `show ip ssh` | Verificado |
| R1-CISCO | `no ip proxy-arp` en Gi0/0 y Gi0/1 | Evitar respuestas ARP por hosts ajenos al segmento cuando no forman parte del diseño de red | `show ip interface` | Verificado |
| R1-CISCO | `no ip redirects` en Gi0/0 y Gi0/1 | Reducir la posibilidad de anuncios de redirección ICMP no deseados a hosts | `show ip interface` | Verificado |
| R1-CISCO | `no ip source-route` | Prohibir explícitamente el uso de source routing IPv4 que permitiría rutas elegidas por el emisor | `show running-config` | Verificado |
| FGT-01 | `set admin-telnet disable` | Deshabilitar administración remota sin cifrado | `show full-configuration system global` | Verificado |
| FGT-01 | `set admin-lockout-duration 300` | Aumentar el tiempo de bloqueo después de intentos fallidos de autenticación | `show full-configuration system global` | Verificado |
| FGT-01 | `set admin-ssh-grace-time 30` | Limitar el tiempo permitido para completar la autenticación SSH | `show full-configuration system global` | Verificado |

**Matices técnicos:** que `no ip source-route` no figurara inicialmente en el running-config no prueba por sí solo que source routing estuviera habilitado. En SW1 se conserva SSH, con las limitaciones criptográficas de la imagen de laboratorio. En FortiGate la administración HTTP de port1 permanece habilitada por las restricciones de evaluación; se trata como riesgo residual y no como un control corregido.

## 3. Herramienta utilizada

El equipo Debian `CIS-AUDITOR` ejecutó scripts Python con Netmiko y Paramiko:
- `cis_audit_baseline.py` obtiene evidencias de los tres equipos **sin modificar su configuración**.
- `cis_checks.py` analiza automáticamente **19 verificaciones seleccionadas**; no las equipara a conformidad integral.
- `cis_apply_sw1.py` y `cis_apply_r1.py` solicitan confirmación, aplican cambios y verifican estado posterior.
- `fortigate_cis.py` ofrece los modos `audit`, `apply` y `verify`, con informes JSON de ejecución.
- `cis_comparativo.py` y `cis_informe_final.py` documentan diferencias y resultados específicos.

El evaluador de 19 verificaciones arrojó **13 CUMPLE, 2 NO CUMPLE, 4 RIESGO** al inicio y **15 CUMPLE, 0 NO CUMPLE, 4 RIESGO** tras los cambios de SW1. Los cambios R1/FGT se verificaron mediante informes **adicionales**, no como parte del denominador de las 19 verificaciones.

## 4. Limitaciones y pendientes

1. Falta **correlación control por control con una edición comprobada de los PDF CIS** para satisfacer literalmente el apartado «recomendaciones del CIS Benchmark».
2. Los scripts de escaneo y aplicación son **módulos separados**. Falta una interfaz única de `audit`/`apply`/`report` para toda la infraestructura si se exige expresamente «el script» en singular.
3. Los archivos de `configuraciones/` son **extractos sanitizados no restaurables**. Si el profesor requiere running-configs íntegros, generar versiones completas **con secretos e identificadores sensibles debidamente ocultados**, después de una revisión manual.
4. La evidencia no constituye una auditoría exhaustiva o certificación CIS.
