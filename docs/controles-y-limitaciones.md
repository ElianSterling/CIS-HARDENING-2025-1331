# Matriz de hardening y limitaciones

## Entorno

- Router: R1-CISCO, IOSv 15.9.
- Switch: SW1-CISCO, IOSvL2 15.2.
- Firewall: FGT-01, FortiOS 7.0.3.
- Auditor: CT 180, Debian 12, Python con Netmiko y Paramiko.

## Controles ejecutados

| Equipo | Control | Estado previo | Estado posterior | Validación |
|---|---|---|---|---|
| SW1-CISCO | Desactivar servidor HTTP | Habilitado | Deshabilitado | `show ip http server status` |
| SW1-CISCO | Desactivar servidor HTTPS | Habilitado | Deshabilitado | `show ip http server status` |
| R1-CISCO | Desactivar Proxy ARP en Gi0/0 y Gi0/1 | Habilitado | Deshabilitado | `show ip interface` |
| R1-CISCO | Desactivar ICMP Redirects en Gi0/0 y Gi0/1 | Habilitado | Deshabilitado | `show ip interface` |
| R1-CISCO | Desactivar explícitamente IP Source Routing | No se encontró configuración explícita | Desactivación explícita comprobada | `show running-config` |
| FGT-01 | Deshabilitar Telnet administrativo | Habilitado | Deshabilitado | `show full-configuration system global` |
| FGT-01 | Aumentar duración del bloqueo administrativo | 60 s | 300 s | `show full-configuration system global` |
| FGT-01 | Reducir plazo de autenticación SSH | 120 s | 30 s | `show full-configuration system global` |

**Nota sobre Source Routing:** la ausencia inicial de `no ip source-route` no demuestra por sí misma que la función estuviera activada; lo que sí se documentó fue la aplicación y verificación de una desactivación explícita.

## Controles preservados

- SSH v2 en R1-CISCO y SW1-CISCO.
- Ruta estática de R1-CISCO hacia `10.25.14.0/24` a través de FortiGate.
- Políticas ICMP específicas entre las LAN de prueba, sin NAT.
- Acceso de administración SSH y HTTP en FGT-01.

## Riesgos residuales y excepciones

1. Los equipos Cisco IOSv admiten algoritmos SSH heredados y se mantuvieron por compatibilidad de la imagen de laboratorio.
2. FGT-01 ejecuta FortiOS 7.0.3 y utiliza una licencia de evaluación.
3. HTTP administrativo en FortiGate port1 continúa habilitado; debe aislarse en la red de laboratorio, sin exponerse a Internet.
4. Los scripts actuales y su inventario son específicos de esta topología: no equivalen a un sistema general de gestión de cumplimiento.

## Alcance CIS

Los resultados reportados corresponden a **19 verificaciones seleccionadas**, algunas de tipo informativo y de riesgo. **No equivalen a una certificación ni una revisión completa del CIS Benchmark.** No se atribuyen identificadores de sección del Benchmark sin verificar la edición aplicable y el contenido autorizado de ese documento.

El total de 19 se refiere al evaluador inicial/posterior; las pruebas separadas de R1 y FortiGate complementan esas evidencias y no se suman automáticamente a ese denominador.
