"""Offline inspection of newly acquired bridge/SAL files; never executes them."""
from pathlib import Path
import hashlib,io,json,re,struct,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
ROOT=BASE/'delphi-dump';OUT=BASE/'delphi-analysis';summaries=[]
report=next(p for p in sorted(ROOT.glob('_collection_*/runtime-targets.json'),reverse=True)
            if json.loads(p.read_text()).get('all_targets_available'))
meta=json.loads(report.read_text());records=[json.loads(x) for x in (report.parent/'manifest.jsonl').read_text().splitlines()]
for name in ('screen-cda','libXSAL.so'):
    transfer=next(x for x in meta['transfers'] if x['source_remote_path'].rsplit('/',1)[1]==name)
    record=next(x for x in records if x.get('remote_path')==transfer['ftp_remote_path'] and x['status']=='downloaded')
    path=ROOT/record['local_path'];blob=path.read_bytes()
    assert len(blob)==record['bytes'] and hashlib.sha256(blob).hexdigest()==record['sha256']
    elf=ELFFile(io.BytesIO(blob));segments=[(s['p_vaddr'],s.data(),s['p_flags']) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def read(va,n):
        for start,data,_ in segments:
            if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
        raise ValueError(f'VA outside file {va:#x}')
    dyn=next(s for s in elf.iter_segments() if s['p_type']=='PT_DYNAMIC')
    tags={t.entry.d_tag:t.entry.get('d_val',0) for t in dyn.iter_tags()}
    def cstr(va):
        for start,data,_ in segments:
            if start<=va<start+len(data):
                off=va-start;end=data.find(b'\0',off);return data[off:end].decode('ascii',errors='replace')
        return ''
    nsyms=struct.unpack('<II',read(tags['DT_HASH'],8))[1]
    symbols=[]
    for i in range(nsyms):
        sn,value,size,info,other,shndx=struct.unpack('<IIIBBH',read(tags['DT_SYMTAB']+16*i,16))
        if sn:symbols.append({'name':cstr(tags['DT_STRTAB']+sn),'value':value,'size':size,'defined':bool(shndx)})
    got={}
    for off in range(tags.get('DT_JMPREL',0),tags.get('DT_JMPREL',0)+tags.get('DT_PLTRELSZ',0),8):
        slot,info=struct.unpack('<II',read(off,8));sn=struct.unpack('<I',read(tags['DT_SYMTAB']+16*(info>>8),4))[0];got[slot]=cstr(tags['DT_STRTAB']+sn)
    strings={start+m.start():m.group().decode('ascii') for start,data,_ in segments for m in re.finditer(rb'[\x20-\x7e]{5,}',data)}
    (OUT/(name+'.runtime-strings.txt')).write_text('\n'.join(f'{va:08x} {text}' for va,text in strings.items()),encoding='utf-8')
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
    instructions=[x for start,data,flags in segments if flags&1 for x in md.disasm_lite(data,start)]
    labels={s['value']:s['name'] for s in symbols if s['value']}
    def immediate(word):
        x=word&255;r=((word>>8)&15)*2;return ((x>>r)|(x<<(32-r)))&0xffffffff if r else x
    for i,(a,sz,mn,op) in enumerate(instructions[:-2]):
        b,_,bn,bo=instructions[i+1];c,_,cn,co=instructions[i+2]
        if mn=='add' and op.startswith('ip, pc,') and bn=='add' and bo.startswith('ip, ip,') and cn=='ldr' and co.startswith('pc, [ip'):
            words=[struct.unpack('<I',read(v,4))[0] for v in (a,b,c)]
            slot=a+8+immediate(words[0])+immediate(words[1])+((words[2]&0xfff) if words[2]&(1<<23) else -(words[2]&0xfff))
            if slot in got:labels[a]=got[slot]+' [PLT]'
    assembly=[];events=[]
    for va,size,mn,op in instructions:
        note=''
        if mn in ('bl','b') and op.startswith('#0x'):note=labels.get(int(op[1:],16),'')
        assembly.append(f'{va:08x} {mn:8s} {op:42s} {note}')
        if mn in ('movw','cmp','mov') and any(s in op for s in ('#0x1693','#0x1694')):events.append({'va':hex(va),'instruction':mn+' '+op})
    (OUT/(name+'.runtime-assembly.txt')).write_text('\n'.join(assembly),encoding='utf-8')
    result={'name':name,'local_path':str(path.relative_to(BASE)),'sha256':record['sha256'],'bytes':len(blob),'entry':hex(elf['e_entry']),'section_count':elf.num_sections(),'needed':[t.needed for t in dyn.iter_tags() if t.entry.d_tag=='DT_NEEDED'],'symbols':symbols,'external_layer_event_immediates':events}
    summaries.append(result)
    print(name,'bytes',len(blob),'sections',elf.num_sections(),'symbols',len(symbols),'events',events)
    print('  dependencies:',','.join(result['needed']))
(OUT/'runtime-bridge-index.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
