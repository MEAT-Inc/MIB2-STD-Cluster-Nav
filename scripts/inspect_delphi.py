"""Offline inventory verification and ELF/string triage; never executes dump files."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path, PureWindowsPath

BASE = Path(__file__).resolve().parents[1]


def manifest_path(root, name):
    """Accept either platform's relative separators without allowing escapes."""
    if not isinstance(name, str) or not name or PureWindowsPath(name).drive:
        raise ValueError('Manifest path must be relative to the dump')
    parts = name.replace('\\', '/').split('/')
    if any(part in ('', '.', '..') or ':' in part for part in parts):
        raise ValueError('Invalid relative manifest path')
    target = root.joinpath(*parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Manifest path escapes dump')
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', type=Path, default=BASE / 'delphi-dump')
    parser.add_argument('--output', type=Path, default=BASE / 'delphi-analysis')
    parser.add_argument('--manifest', type=Path, help='Explicit acquisition manifest (relative to cwd)')
    args = parser.parse_args(argv)
    ROOT, OUT = args.dump.resolve(), args.output.resolve()
    manifests = sorted(ROOT.glob('_collection_*/manifest.jsonl'))
    manifest = args.manifest.resolve() if args.manifest else (manifests[0] if manifests else None)
    if manifest is None or not manifest.is_file():
        parser.error('No acquisition manifest found; supply --dump or --manifest')
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    for line in manifest.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if row.get('status') != 'downloaded':
            continue
        path = manifest_path(ROOT, row['local_path'])
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



if __name__ == '__main__':
    main()
