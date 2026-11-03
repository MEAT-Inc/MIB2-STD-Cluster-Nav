"""Focused offline ARM disassembly of the acquired process manager. Never executes it."""
from project_console import console_session, log as print
with console_session(__file__, __doc__, enabled=__name__ == '__main__'):
    from pathlib import Path
    import bisect,io,json,re,struct,sys
    ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.tools/python'))
    from elftools.elf.elffile import ELFFile
    from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
    OUT=ROOT/'delphi-analysis/control-runtime'
    index=json.loads((OUT/'procman.index.json').read_text())
    review=json.loads((OUT/'hardware-review.json').read_text())
    blob=(ROOT/'delphi-dump'/review['collection']/'procman.captured').read_bytes()
    elf=ELFFile(io.BytesIO(blob))
    loads=[(s['p_vaddr'],s.data(),s['p_flags']) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    def read(va,n):
     for start,data,flags in loads:
      if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
     return b''
    strings={r['va']:r['text'] for r in index['strings']}
    dyn=next(s for s in elf.iter_segments() if s['p_type']=='PT_DYNAMIC')
    tags={t.entry.d_tag:t.entry.get('d_val',0) for t in dyn.iter_tags()}
    def cstr(va):
     for start,data,flags in loads:
      if start<=va<start+len(data):
       off=va-start;end=data.find(b'\0',off);return data[off:end].decode('ascii',errors='replace')
     return ''
    got={}
    for va in range(tags.get('DT_JMPREL',0),tags.get('DT_JMPREL',0)+tags.get('DT_PLTRELSZ',0),8):
     slot,info=struct.unpack('<II',read(va,8));name=struct.unpack('<I',read(tags['DT_SYMTAB']+16*(info>>8),4))[0]
     got[slot]=cstr(tags['DT_STRTAB']+name)
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
    ins=[i for start,data,flags in loads if flags&1 for i in md.disasm_lite(data,start)]
    labels={s['value']:s['name'] for s in index['symbols'] if s['defined'] and s['value']}
    def imm(word):
     value=word&255;rot=((word>>8)&15)*2
     return ((value>>rot)|(value<<(32-rot)))&0xffffffff if rot else value
    for n,(va,sz,mn,op) in enumerate(ins[:-2]):
     if mn=='add' and op.startswith('ip, pc,') and ins[n+1][2]=='add' and ins[n+1][3].startswith('ip, ip,') and ins[n+2][2]=='ldr' and ins[n+2][3].startswith('pc, [ip'):
      a,b,c=[struct.unpack('<I',read(x[0],4))[0] for x in ins[n:n+3]]
      slot=va+8+imm(a)+imm(b)+((c&4095) if c&(1<<23) else -(c&4095))
      if slot in got:labels[va]=got[slot]+' [PLT]'
    refs=[];formatted=[];constants={}
    for va,sz,mn,op in ins:
     note=''
     if mn in ('movw','movt'):
      m=re.fullmatch(r'(\w+), #(0x[0-9a-f]+|[0-9]+)',op)
      if m:
       reg=m[1];value=int(m[2],0)
       if mn=='movw': constants[reg]=value
       elif reg in constants:
        constants[reg]=(constants[reg]&65535)|(value<<16)
        target=constants[reg]
        if target in strings:
         note=' address='+hex(target)+' '+strings[target];refs.append(dict(va=va,target=target,text=strings[target]))
     elif mn in ('bl','blx'):
      for reg in ('r0','r1','r2','r3','ip'):constants.pop(reg,None)
     elif mn not in ('str','strb','strh','cmp','tst','b','beq','bne','bgt','blt','bhs','blo'):
      constants.pop(op.split(',')[0],None)
     if mn in ('bl','b') and op.startswith('#0x'):note+=labels.get(int(op[1:],16),'')
     if mn.startswith('ldr') and '[pc' in op:
      m=re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?\d+))?\]',op)
      if m:
       data=read(va+8+int(m[1] or '0',0),4)
       if len(data)==4:
        value=struct.unpack('<I',data)[0]
        note+=' literal='+hex(value)
        if value in strings:
         note+=' '+strings[value];refs.append(dict(va=va,target=value,text=strings[value]))
     formatted.append(f'{va:08x} {mn:9s} {op:42s} {note}')
    (OUT/'procman.assembly.txt').write_text('\n'.join(formatted),encoding='utf-8')
    (OUT/'procman.xrefs.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
    prologues=[va for va,sz,mn,op in ins if mn=='push' and 'lr' in op]
    seeds=[r for r in refs if any(t in r['text'] for t in ('App %s - killed','doesn\'t send APP_INITIALIZED','App %s exited','App %s - spawned','pm_parser.c','Unrecognized option','EV_START_APP','EV_PROCESS_EXIT','EV_GET_APP_STATE','EV_APP_SPAWN','All processes stopped'))]
    ranges=[]
    for r in seeds:
     n=bisect.bisect_right(prologues,r['va'])-1
     if n<0:continue
     a=prologues[n];b=prologues[n+1] if n+1<len(prologues) else a+1024
     if (a,b) not in ranges:ranges.append((a,b))
    lines=[]
    for a,b in ranges:
     lines.append('\nPROLOGUE-HEURISTIC WINDOW '+hex(a)+'..'+hex(b))
     lines.extend(formatted[n] for n,i in enumerate(ins) if a<=i[0]<b)
    (OUT/'procman.focused.txt').write_text('\n'.join(lines),encoding='utf-8')
    print('PLT labels:',len(labels),'string references:',len(refs),'focused windows:',len(ranges))
    for r in seeds:print(hex(r['va']),r['text'])
    print('Process-control imported functions:',{hex(k):v for k,v in labels.items() if v.split(' ')[0] in ('spawnp','kill','getopt','getenv','chdir','waitpid','sigwaitinfo')})
