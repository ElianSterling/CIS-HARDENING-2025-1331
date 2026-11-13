#!/usr/bin/env python3
"""Extrae campos publicables (no restaura configuraciones originales)."""
import json, os, re
from pathlib import Path

root = Path('/opt/cis-auditor')
stamp = max(
    p.name for p in (root/'backups').iterdir()
    if p.is_dir() and re.fullmatch(r'[0-9]{8}T[0-9]{6}Z', p.name)
)
backup = root/'backups'/stamp
out = root/'configuraciones-publicables'/stamp
report = root/'reportes'/f'baseline_{stamp}.json'
os.umask(0o077)

records = json.loads(report.read_text())['results']
if {r['device'] for r in records if r['status']=='OK' and len(r['files'])==5} != {'R1-CISCO','SW1-CISCO','FGT-01'}:
    raise SystemExit('ERROR: El informe no confirma 15/15 evidencias.')

def leer(nombre):
    p = backup/nombre
    if not p.is_file() or p.is_symlink():
        raise SystemExit(f'ERROR: falta evidencia privada {nombre}')
    return p.read_text(encoding='utf-8').replace('\r','')

def cisco(nombre,interfaces):
    permitidos_global = [
        r'no ip source-route', r'ip ssh version 2',
        r'no ip http server',r'no ip http secure-server',
        r'ip route 10\.25\.14\.0 255\.255\.255\.0 172\.31\.13\.2(?: \d+)?'
    ]
    permitidos_if = [
        r'ip address (?:10\.25\.13\.[12] 255\.255\.255\.0|172\.31\.13\.1 255\.255\.255\.252)',
        r'no ip proxy-arp', r'no ip redirects',r'no shutdown'
    ]
    result = [f'# {nombre} — extracto de show running-config',
              '# Controles seleccionados: NO es backup restaurable',
              f'hostname {nombre}', '!']
    glob, ifs, actual = [], {i:[] for i in interfaces}, None
    for line in leer(nombre+'_01.txt').splitlines():
        if line.startswith('interface '):
            actual=line.split(' ',1)[1].strip()
            continue
        s=line.strip()
        if s=='!' or (line and not line.startswith(' ')):
            actual=None
        if actual in ifs and any(re.fullmatch(x,s) for x in permitidos_if):
            if s not in ifs[actual]: ifs[actual].append(s)
        elif actual is None and any(re.fullmatch(x,s) for x in permitidos_global):
            if s not in glob: glob.append(s)
    result += glob+['!']
    for i, values in ifs.items():
        if not values: raise SystemExit(f'ERROR: no hay configuración segura para {nombre}/{i}')
        result += ['interface '+i]+[' '+v for v in values]+['!']
    return '\n'.join(result)+'\n'

def bloques(texto, nombres, campos):
    resultado, actual = [], None
    for linea in texto.splitlines():
        s=linea.strip()
        m=re.fullmatch(r'edit\s+"?([A-Za-z0-9_.-]+)"?',s)
        if m:
            actual=m[1] if m[1] in nombres else None
            if actual: resultado.append(f'    edit "{actual}"')
            continue
        if s=='next':
            if actual: resultado.append('    next')
            actual=None
            continue
        m=re.fullmatch(r'set ([a-z][a-z0-9_-]*) (.+)',s)
        if actual and m and m[1] in campos and re.fullmatch(r'[A-Za-z0-9_.\-/ "\s]{1,120}',m[2]):
            resultado.append(f'        set {m[1]} {m[2]}')
    return resultado

def forti():
    lines=['# FGT-01 — extracto de configuración final',
           '# Controles seleccionados: NO es backup restaurable',
           'config system global']
    allowed={'admin-telnet','admin-lockout-duration','admin-lockout-threshold',
             'admin-ssh-grace-time','admin-ssh-v1','admintimeout'}
    found={}
    for line in leer('FGT-01_05.txt').splitlines():
        m=re.fullmatch(r'\s*set ([a-z][a-z0-9_-]*) ([A-Za-z0-9_-]+)\s*',line)
        if m and m[1] in allowed: found[m[1]]=m[2]
    if not {'admin-telnet','admin-lockout-duration','admin-ssh-grace-time'} <= found.keys():
        raise SystemExit('ERROR: faltan datos globales del FortiGate.')
    if found['admin-telnet']!='disable' or found['admin-lockout-duration']!='900' or found['admin-ssh-grace-time']!='30':
        raise SystemExit('ERROR: valores de FortiGate inesperados.')
    lines += [f'    set {k} {v}' for k,v in found.items()]+['end']
    spec=[
        ('system interface','FGT-01_02.txt',{'port1','port2','port3'}, {'ip','allowaccess','role','status'}),
        ('firewall policy','FGT-01_03.txt',{str(i) for i in range(1,10)}, {'name','srcintf','dstintf','srcaddr','dstaddr','service','action','schedule','nat','logtraffic'}),
        ('router static','FGT-01_04.txt',{str(i) for i in range(1,10)}, {'dst','gateway','device'})
    ]
    for section,file,names,fields in spec:
        b=bloques(leer(file),names,fields)
        if b: lines += ['config '+section]+b+['end']
    return '\n'.join(lines)+'\n'

outputs={
    'R1-CISCO-running-config-sanitizado.txt':cisco('R1-CISCO',['GigabitEthernet0/0','GigabitEthernet0/1']),
    'SW1-CISCO-running-config-sanitizado.txt':cisco('SW1-CISCO',['Vlan1']),
    'FGT-01-config-sanitizada.txt':forti()
}
if 'no ip source-route' not in outputs['R1-CISCO-running-config-sanitizado.txt'] or 'no ip http server' not in outputs['SW1-CISCO-running-config-sanitizado.txt']:
    raise SystemExit('ERROR: evidencia esperada no encontrada en Cisco.')
if out.exists(): raise SystemExit(f'ERROR: {out} ya existe. No se sobrescribe.')
out.mkdir(mode=0o700, parents=True)
for name,content in outputs.items():
    p=out/name
    p.write_text(content,encoding='utf-8')
    p.chmod(0o600)
    print(f'[OK] {name}: {len(content.splitlines())} líneas')
print(f'\nListo: {out}\nNo se ha publicado ningún respaldo privado.')
