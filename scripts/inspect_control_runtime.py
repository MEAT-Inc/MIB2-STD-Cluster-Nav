"""Verify a unit smoke capture and inspect native control files as data only."""
from pathlib import Path
import hashlib,io,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
from run_observer_smoke import assess

def inspect(path):
    blob=path.read_bytes();elf=ELFFile(io.BytesIO(blob))
    loads=[(s['p_vaddr'],s.data(),s['p_flags']) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def read(va,n):
        for start,data,flags in loads:
            if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
        raise ValueError('Unmapped file VA '+hex(va))
    def cstr(va):
        for start,data,flags in loads:
            if start<=va<start+len(data):
                off=va-start;end=data.find(b'\0',off)
                if end<0:raise ValueError('Unterminated string')
                return data[off:end].decode('ascii',errors='replace')
        raise ValueError('Unmapped string')
    dyn=next(s for s in elf.iter_segments() if s['p_type']=='PT_DYNAMIC')
    tags={t.entry.d_tag:t.entry.get('d_val',0) for t in dyn.iter_tags()}
    count=struct.unpack('<II',read(tags['DT_HASH'],8))[1]
    symbols=[]
    for i in range(count):
        name,va,size,info,other,section=struct.unpack('<IIIBBH',read(tags['DT_SYMTAB']+i*16,16))
        if name:symbols.append(dict(name=cstr(tags['DT_STRTAB']+name),value=va,size=size,defined=bool(section)))
    strings=[dict(va=start+m.start(),text=m.group().decode('ascii')) for start,data,flags in loads
             for m in re.finditer(rb'[\x20-\x7e]{5,}',data)]
    # Also preserve nonallocated usage strings which may survive section stripping.
    raw_strings=[dict(offset=m.start(),text=m.group().decode('ascii')) for m in re.finditer(rb'[\x09\x0a\x0d\x20-\x7e]{8,}',blob)]
    return dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),entry=elf['e_entry'],
        sections=elf.num_sections(),needed=[t.needed for t in dyn.iter_tags() if t.entry.d_tag=='DT_NEEDED'],
        symbols=symbols,strings=strings,raw_strings=raw_strings)

def main():
    run=max((ROOT/'delphi-dump').glob('_observer_smoke_*'),key=lambda p:p.name)
    summary=json.loads((run/'smoke-summary.json').read_text())
    checks=[]
    for row in summary['artifacts']:
        name=row['file']
        if Path(name).name!=name or name in ('.','..'):raise ValueError('Unexpected artifact name')
        data=(run/name).read_bytes()
        ok=len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
        if not ok:raise ValueError('Artifact mismatch: '+name)
        checks.append(dict(file=name,bytes=len(data),sha256=row['sha256']))
    blobs={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    result=assess(blobs)
    decoded=result.pop('decoded_log')
    if decoded!=json.loads((run/'observer-decoded.json').read_text()):raise ValueError('Decoded JSON differs from raw trace')
    out=ROOT/'delphi-analysis/control-runtime';out.mkdir(exist_ok=True)
    runtimes={name:inspect(run/(name+'.captured')) for name in ('procman','libc.so.3')}
    for name,data in runtimes.items():
        (out/(name+'.index.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
        (out/(name+'.strings.txt')).write_text('\n'.join(f"{r['va']:08x} {r['text']}" for r in data['strings']),encoding='utf-8')
        print(name, 'sections=',data['sections'],'symbols=',len(data['symbols']),'needed=',data['needed'])
    report=dict(collection=run.name,verified_artifacts=checks,isolated_hardware_smoke_passed=True,
        stock_processes_unchanged=result['stock_processes_unchanged'],stock_pids=result['stock_pids'],
        smoke_pid=decoded['pid'],records=decoded['count'],dropped=decoded['dropped'],
        actual_androidauto_interposition_tested=False,runtimes={n:{k:d[k] for k in ('bytes','sha256','entry','sections','needed')} for n,d in runtimes.items()})
    (out/'hardware-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PASS:',len(checks),'artifact hashes; raw trace independently decoded;',decoded['count'],'records;',decoded['dropped'],'drops; stock PID',result['stock_pids'])
    pattern=re.compile(r'usage|procman|restart|respawn|launch|relaunch|command|monitor|shutdown|suspend|resume|register|unregister|environment|terminate',re.I)
    for row in runtimes['procman']['raw_strings']:
        if pattern.search(row['text']):print(hex(row['offset']),row['text'][:2400])
if __name__=='__main__':main()
