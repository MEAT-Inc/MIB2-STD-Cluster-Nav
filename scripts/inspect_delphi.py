"""Offline inventory verification and ELF/string triage; never executes dump files."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(r'.\delphi-dump')
OUT = Path(__file__).resolve().parents[1] / 'delphi-analysis'
OUT.mkdir(exist_ok=True)
manifest = next(ROOT.glob('_collection_*/manifest.jsonl'))
checks = []
for line in manifest.read_text(encoding='utf-8').splitlines():
    row = json.loads(line)
    if row.get('status') != 'downloaded':
        continue
    path = ROOT / row['local_path']
    blob = path.read_bytes()
    checks.append({'path': row['local_path'], 'bytes': len(blob),
                   'ok': len(blob) == row['bytes'] and hashlib.sha256(blob).hexdigest() == row['sha256']})
(OUT / 'verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print('Manifest verification:', len(checks), 'files;', sum(not c['ok'] for c in checks), 'mismatches')

pattern = re.compile(r'cluster|secondary|video|h264|h\.264|mpeg|encoder|screen|display|most|resolution|surface|projection', re.I)
results = []
for folder in ('bin', 'lib'):
    for path in sorted((ROOT / 'extbin/apps' / folder).iterdir()):
        if not path.is_file():
            continue
        blob = path.read_bytes()
        strings = [m.group().decode('ascii') for m in re.finditer(rb'[\x20-\x7e]{5,}', blob)]
        (OUT / (path.name + '.strings.txt')).write_text('\n'.join(strings), encoding='utf-8')
        result = {'file': str(path.relative_to(ROOT)), 'magic': blob[:16].hex(), 'bytes': len(blob)}
        if blob[:5] == b'\x7fELF\x01' and blob[5] == 1:
            hdr = struct.unpack_from('<16sHHIIIIIHHHHHH', blob)
            shoff, shentsize, shnum, shstrndx = hdr[6], hdr[11], hdr[12], hdr[13]
            sections = [struct.unpack_from('<IIIIIIIIII', blob, shoff + i * shentsize) for i in range(shnum)]
            def zstr(data, offset):
                return data[offset:data.find(b'\0', offset)].decode('ascii', errors='replace')
            namesec = sections[shstrndx]
            names = blob[namesec[4]:namesec[4]+namesec[5]]
            result['machine'] = hdr[2]
            result['sections'] = [zstr(names, sec[0]) for sec in sections]
            result['needed'] = []
            symbols = []
            for sec in sections:
                if sec[1] in (2, 11):
                    strsec = sections[sec[6]]
                    table = blob[strsec[4]:strsec[4]+strsec[5]]
                    for pos in range(sec[4], sec[4]+sec[5], sec[9] or 16):
                        name, value, size, info, other, ndx = struct.unpack_from('<IIIBBH', blob, pos)
                        if name:
                            symbols.append({'name': zstr(table, name), 'value': hex(value), 'size': size, 'defined': ndx != 0})
                if sec[1] == 6:
                    strsec = sections[sec[6]]
                    table = blob[strsec[4]:strsec[4]+strsec[5]]
                    for pos in range(sec[4], sec[4]+sec[5], sec[9] or 8):
                        tag, value = struct.unpack_from('<iI', blob, pos)
                        if tag == 1:
                            result['needed'].append(zstr(table, value))
            result['symbols'] = symbols
            result['matching_symbols'] = [s for s in symbols if pattern.search(s['name'])]
        result['matching_strings'] = [s for s in strings if pattern.search(s)]
        results.append(result)
        print(path.name, 'ELF' if 'machine' in result else 'image', len(result.get('symbols', [])), 'symbols;', len(result['matching_strings']), 'matching strings')
(OUT / 'binary-triage.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

