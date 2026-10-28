"""Bounded peer-side corroboration of DisplayManagement native event contracts."""
from pathlib import Path
import io,json,struct,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
OUT=BASE/'delphi-analysis';p=BASE/'delphi-dump/extbin/apps/bin/NavigationServer';e=ELFFile(io.BytesIO(p.read_bytes()));segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def rd(va,n):
 for start,data in segments:
  if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
 return b''
labels={}
for sec in e.iter_sections():
 if sec['sh_type'] in ('SHT_DYNSYM','SHT_SYMTAB'):labels.update({s['st_value']:s.name for s in sec.iter_symbols() if s['st_value']})
plt=e.get_section_by_name('.plt');rel=e.get_section_by_name('.rel.plt');symbols=e.get_section(rel['sh_link'])
for i,r in enumerate(rel.iter_relocations()):labels[plt['sh_addr']+20+12*i]=symbols.get_symbol(r['r_info_sym']).name+' [PLT]'
text=e.get_section_by_name('.text');md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
ins=list(md.disasm_lite(text.data(),text['sh_addr']));hits=[i for i,(_,_,op,args) in enumerate(ins) if op in ('movw','cmp','mov') and any(k in args for k in ['#0x1693','#0x1694'])]
lines=[]
def fmt(x):
 a,size,op,args=x;note=''
 if op in ('bl','b') and args.startswith('#0x'):note=labels.get(int(args[1:],16),'')
 return f'{a:08x} {op:8s} {args:40s} {note}'
for i in hits:
 lines.append(f'\nHIT {ins[i][0]:#x} {ins[i][2]} {ins[i][3]}')
 lines.extend(fmt(x) for x in ins[max(0,i-45):i+70])
(OUT/'display-hmi-peer-event-scan.txt').write_text('\n'.join(lines),encoding='utf-8')
print('Event hits',[(hex(ins[i][0]),ins[i][3]) for i in hits])
# Additional bounded string-xref and screen-cda bridge inventory.
targets={}
for sec in e.iter_sections():
 if sec['sh_flags']&2 and sec['sh_type']!='SHT_NOBITS':
  data=sec.data()
  for needle in ['::onMessage(SCDA_EV_EXT_MAP_ACTIVATE_REQ)','::onMessage(SCDA_EV_EXT_MAP_DEACTIVATE_REQ)','::onMessage(SCDA_EV_EXT_MAP_RATE_REQ)']:
   off=data.find(needle.encode())
   if off>=0:targets[sec['sh_addr']+off]=needle
references=[];index={v[0]:i for i,v in enumerate(ins)};raw=text.data()
for off in range(0,len(raw)-3,4):
 word=struct.unpack_from('<I',raw,off)[0];va=text['sh_addr']+off
 if word&0x0f1f0000==0x051f0000:
  lit=va+8+((word&0xfff) if word&(1<<23) else -(word&0xfff));value=rd(lit,4)
  if len(value)==4 and (target:=struct.unpack('<I',value)[0]) in targets:
   references.append({'instruction':hex(va),'literal':hex(lit),'text':targets[target]});i=index.get(va)
   if i is not None:
    lines.append('\nMAP EVENT STRING '+json.dumps(references[-1]));lines.extend(fmt(x) for x in ins[max(0,i-30):i+80])
(OUT/'display-hmi-peer-event-scan.txt').write_text('\n'.join(lines),encoding='utf-8')
print('Map event refs',references)
# The bridge executable is only named in runtime inventory, not acquired.
