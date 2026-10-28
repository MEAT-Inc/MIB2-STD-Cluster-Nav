"""Offline annotated ARM resource-manager disassembly. No vehicle access."""
from pathlib import Path
import io,re,struct,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
P=BASE/'delphi-dump/extbin/apps/bin/TransportServer';E=ELFFile(io.BytesIO(P.read_bytes()))
SEG=[(s['p_vaddr'],s.data()) for s in E.iter_segments() if s['p_type']=='PT_LOAD']
def read(va,n):
 for start,data in SEG:
  if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
 return b''
def string(va):
 for start,data in SEG:
  if start<=va<start+len(data):
   off=va-start;end=data.find(b'\0',off,min(off+500,len(data)));c=data[off:end]
   if end>=0 and len(c)>=3 and all(32<=x<127 for x in c):return c.decode()
 return ''
LABEL={}
for sec in E.iter_sections():
 if sec['sh_type'] in ('SHT_DYNSYM','SHT_SYMTAB'):LABEL.update({s['st_value']:s.name for s in sec.iter_symbols() if s['st_value']})
plt=E.get_section_by_name('.plt');rel=E.get_section_by_name('.rel.plt');sy=E.get_section(rel['sh_link'])
LABEL.update({plt['sh_addr']+20+12*i:sy.get_symbol(r['r_info_sym']).name+' [PLT]' for i,r in enumerate(rel.iter_relocations())})
md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
sec=E.get_section_by_name('.text');ins=list(md.disasm_lite(sec.data(),sec['sh_addr']));out=[];low={}
for va,sz,mn,op in ins:
 note=''
 if mn.startswith('bl') or mn=='b':
  try:note=LABEL.get(int(op[1:],16),'')
  except:pass
 if mn.startswith('ldr') and '[pc' in op:
  m=re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?\d+))?\]',op)
  if m:
   raw=read(va+8+int(m.group(1) or '0',0),4)
   if len(raw)==4:
    v=struct.unpack('<I',raw)[0];note+=f' literal={v:#x} '+string(v)
 if mn=='movw':
  m=re.match(r'(\w+), #(0x[0-9a-f]+|\d+)',op)
  if m:low[m.group(1)]=(va,int(m.group(2),0))
 if mn=='movt':
  m=re.match(r'(\w+), #(0x[0-9a-f]+|\d+)',op)
  if m and m.group(1) in low:
   prior,v=low[m.group(1)]
   if va-prior<=24:
    v|=int(m.group(2),0)<<16;note+=f' constant={v:#x} '+string(v)
 out.append(f'{va:08x} {mn:8s} {op:42s} {note}')
(BASE/'delphi-analysis/native-transport-server-disassembly.txt').write_text('\n'.join(out),encoding='utf-8')
print('TransportServer instructions',len(ins))
