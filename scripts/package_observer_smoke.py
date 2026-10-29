"""Build the small smoke release after QNX emulation; no vehicle connection."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
SMOKE=ROOT/'native/observer/smoke'
NAMES=('observer_smoke','observer_smoke_guard','libautoreceiver.so','libdelphi_observer.so')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    log=(SMOKE/'qemu/qemu.log').read_text(errors='replace')
    if 'DELPHI_SMOKE_QNX_SUITE_PASS' not in log or 'DELPHI_SMOKE_TIMEOUT child_reaped=1' not in log:
        raise RuntimeError('QNX smoke/control tests have not passed')
    tested={line.split()[1]:line.split()[0] for line in (SMOKE/'qemu/tested.sha256').read_text().splitlines()}
    sources={name:SMOKE/'build'/name for name in NAMES}
    sources['libdelphi_observer.so']=ROOT/'native/observer/release/libdelphi_observer.so'
    release_manifest=json.loads((ROOT/'native/observer/release/manifest.json').read_text())
    if sha(sources['libdelphi_observer.so'])!=release_manifest['sha256']: raise RuntimeError('Observer differs from release candidate')
    records={}
    for name,path in sources.items():
        if sha(path)!=tested[name]: raise RuntimeError('File differs from QNX-tested artifact: '+name)
        with path.open('rb') as stream:
            elf=ELFFile(stream)
            if elf['e_machine']!='EM_ARM' or elf.elfclass!=32 or not elf.little_endian or elf['e_flags']>>24!=5 or elf['e_flags']&0x400:
                raise RuntimeError('Wrong ARM ABI: '+name)
            needs=[]
            for seg in elf.iter_segments():
                if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1: raise RuntimeError('Executable stack')
                if seg['p_type']=='PT_DYNAMIC': needs += [tag.needed for tag in seg.iter_tags() if tag.entry.d_tag=='DT_NEEDED']
            expected={'libc.so.3','libautoreceiver.so'} if name=='observer_smoke' else {'libc.so.3'}
            if set(needs)!=expected: raise RuntimeError('Unexpected runtime dependency: '+name+repr(needs))
        records[name]=dict(sha256=sha(path),bytes=path.stat().st_size,needed=needs)
    release=SMOKE/'release';release.mkdir(exist_ok=True)
    for name,path in sources.items(): shutil.copy2(path,release/name)
    data=dict(kind='isolated_observer_smoke',files=records,qnx_emulation_passed=True,
        vehicle_validated=False,synthetic_provider='libautoreceiver.so',
        no_stock_app_control=True,qnx_log_sha256=sha(SMOKE/'qemu/qemu.log'))
    (release/'manifest.json').write_text(json.dumps(data,indent=2))
    if (SMOKE/'README.txt').exists(): shutil.copy2(SMOKE/'README.txt',release/'README.txt')
    bundle=SMOKE/'observer-smoke-laptop.zip'
    paths=[ROOT/'scripts'/name for name in ('run_observer_smoke.py','delphi_inventory.py','decode_delphi_observer.py')]
    paths += [release/name for name in (*NAMES,'manifest.json','README.txt')]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in paths: archive.write(path,path.relative_to(ROOT).as_posix())
    print('PASS: four QNX-tested ARM files; libc-only synthetic test; observer candidate hash unchanged.')
    print('Portable bundle:',bundle)
if __name__=='__main__': main()
