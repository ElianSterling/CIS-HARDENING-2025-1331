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

La evaluación original contiene **19 verificaciones locales**, no 19 controles CIS identificados. Se añadió un informe adicional que verifica **7 referencias CIS seleccionadas**, usando recomendaciones comprobadas de CIS Cisco IOS v2.2 (referencia histórica) y CIS Fortigate 7.0.x v1.3.0/v1.4.0 (sin cambios entre esas ediciones según CIS).

- Cisco IOS v2.2: **1.2.2.5** HTTP, **1.3.1.2** Source Routing y **2.3.3.2** Proxy ARP.
- CIS Fortigate 7.0.x: **2.2.2** reintentos/bloqueo (objetivo **900 s** con umbral 3); **2.4.4** timeout administrativo; **2.4.5** canales cifrados.
- El ajuste de **300 s** aplicado originalmente en FortiGate es insuficiente para 2.2.2 y debe verificarse de nuevo tras actualizar a 900 s.
- `port1` de FortiGate conserva HTTP por limitaciones de la instancia de evaluación: **2.4.5 NO CUMPLE**.

Consultar [la matriz identificada y justificada](justificacion-hardening.md) y [el auditor integrado](operacion-auditor.md).

El total de 19 corresponde solo al evaluador inicial/posterior. No se certifica conformidad integral del CIS Benchmark, ni se afirma que IOSv 15.9 sea idéntico al benchmark histórico.
