"""Offline QNX IFS extraction and symbol inspection. Never executes vehicle files."""
from pathlib import Path, PurePosixPath
import hashlib, importlib.util, io, json, struct, sys
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / '.tools/python'))
from dissect.util.compression import lzo
from elftools.elf.elffile import ELFFile
sys.modules['lzo'] = lzo
spec = importlib.util.spec_from_file_location('upstream_dumpifs', BASE / '.tools/dumpifs/dumpifs.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
OUT = BASE / 'delphi-analysis'
OUT.mkdir(exist_ok=True)
records = []
for name in ['vwjxe.ifs', 'delphibin.ifs']:
    source = BASE / 'delphi-dump/extbin/apps/bin' / name
    image = module.qifs(str(source), quiet=True)
    raw = image.decomp_image
    expected = image.ifs['startup_header']['imagefs_size']
    if len(raw) != expected:
        raise ValueError(f'{name}: {len(raw)} != declared {expected}')
    signature = raw[:8]
    if signature != b'imagefs\0' and signature != b'\x00imagefs' and b'imagefs' not in signature:
        raise ValueError(f'Unexpected imagefs signature {signature!r}')
    target = OUT / 'extracted' / source.stem
    target.mkdir(parents=True, exist_ok=True)
    image_meta = {'source': str(source.relative_to(BASE)), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'expected_bytes':expected, 'decoded_bytes':len(raw), 'image_checksum_sum32': hex(sum(struct.unpack('<'+'I'*(len(raw)//4),raw)) & 0xffffffff) if len(raw)%4 == 0 else None, 'files':[], 'other_entries':[]}
    for ent in image.ifs['image']['entries']:
        if ent['type'] != 0x8000:
            image_meta['other_entries'].append(ent)
            continue
        pure = PurePosixPath(ent['name'])
        if pure.is_absolute() or not pure.parts or any(p in ('.', '..') or ':' in p or '\\' in p for p in pure.parts):
            raise ValueError(f'Unsafe image path: {ent["name"]}')
        off, size = ent['offset'], ent['size']
        if off < image.ifs['image']['hdr_dir_size'] or off+size > len(raw):
            raise ValueError('File range outside image payload')
        dest = target.joinpath(*pure.parts)
        data = raw[off:off+size]
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            if dest.read_bytes() != data: raise ValueError(f'Existing file differs: {dest}')
        else:
            with dest.open('xb') as f: f.write(data)
        image_meta['files'].append({'name':ent['name'],'bytes':size,'sha256':hashlib.sha256(data).hexdigest(),'magic':data[:16].hex()})
    records.append(image_meta)
    print(name, 'decoded',len(raw),'bytes;',len(image_meta['files']),'files; sum32',image_meta['image_checksum_sum32'])
(OUT/'extraction-manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

files = list((BASE/'delphi-dump/extbin/apps/bin').iterdir()) + list((BASE/'delphi-dump/extbin/apps/lib').iterdir()) + list((OUT/'extracted').rglob('*'))
info=[]
for path in files:
    if not path.is_file(): continue
    data=path.read_bytes()
    if data[:4]!=b'\x7fELF': continue
    elf=ELFFile(io.BytesIO(data))
    symbols=[]
    for sec in elf.iter_sections():
        if sec['sh_type'] not in ('SHT_SYMTAB','SHT_DYNSYM'): continue
        for sym in sec.iter_symbols():
            if sym.name: symbols.append({'name':sym.name,'address':sym['st_value'],'size':sym['st_size'],'type':sym['st_info']['type'],'section':sym['st_shndx']})
    needed=[]
    dyn=elf.get_section_by_name('.dynamic')
    if dyn:
        needed=[t.needed for t in dyn.iter_tags() if t.entry.d_tag=='DT_NEEDED']
    rec={'file':str(path.relative_to(BASE)),'entry':elf['e_entry'],'machine':elf['e_machine'],'needed':needed,'sections':[s.name for s in elf.iter_sections()],'symbols':symbols}
    info.append(rec)
    if path.name in ('AndroidAuto','NavigationServer','DisplayManagement','libautoreceiver.so','ClusterServices'):
        print(path.name,'entry',hex(elf['e_entry']),'symbols',len(symbols),'symtab',elf.get_section_by_name('.symtab') is not None)
        print('  needed:', ', '.join(needed))
(OUT/'elf-symbols.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
