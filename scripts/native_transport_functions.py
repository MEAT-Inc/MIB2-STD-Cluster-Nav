"""Follow native transport functions using prologue heuristics and annotated ARM literals."""
from pathlib import Path
import bisect,io,re,struct,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
P=BASE/'delphi-dump/extbin/apps/bin/NavigationServer';E=ELFFile(io.BytesIO(P.read_bytes()))
SEG=[(s['p_vaddr'],s.data()) for s in E.iter_segments() if s['p_type']=='PT_LOAD']
def read(va,n):
 for start,data in SEG:
  if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
 return b''
def string(va):
 for start,data in SEG:
  if start<=va<start+len(data):
   off=va-start;end=data.find(b'\0',off,min(off+600,len(data)));c=data[off:end]
   if end>=0 and len(c)>=4 and all(32<=x<127 for x in c):return c.decode()
 return ''
LABEL={}
for sec in E.iter_sections():
 if sec['sh_type'] in ('SHT_SYMTAB','SHT_DYNSYM'):LABEL.update({s['st_value']:s.name for s in sec.iter_symbols() if s['st_value']})
plt=E.get_section_by_name('.plt');rel=E.get_section_by_name('.rel.plt');sy=E.get_section(rel['sh_link'])
LABEL.update({plt['sh_addr']+20+12*i:sy.get_symbol(r['r_info_sym']).name+' [PLT]' for i,r in enumerate(rel.iter_relocations())})
sec=E.get_section_by_name('.ARM.exidx');raw=sec.data();bounds=[]
for off in range(0,len(raw),8):
 v=struct.unpack_from('<I',raw,off)[0]&0x7fffffff
 if v&0x40000000:v-=0x80000000
 bounds.append(sec['sh_addr']+off+v)
bounds=sorted(set(bounds)); md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
text=E.get_section_by_name('.text');allins=list(md.disasm_lite(text.data(),text['sh_addr']))
def fmt(x):
 va,sz,mn,op=x;note=''
 if mn.startswith('bl') or mn=='b':
  try:note=LABEL.get(int(op[1:],16),'')
  except:pass
 if mn.startswith('ldr') and '[pc' in op:
  m=re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?\d+))?\]',op)
  if m:
   raw=read(va+8+int(m.group(1) or '0',0),4)
   if len(raw)==4:
    v=struct.unpack('<I',raw)[0];note+=f' literal={v:#x} '+string(v)
 return f'{va:08x} {mn:8s} {op:42s} {note}'
seeds=[0x1ee75c,0x1ee308,0x22cdb4,0x21eaac,0x1e4744,0x1f593c,0x1fa4cc,0x1f535c,0x1ed8d0,0x1ed948,0x1ed9ec,0x1c6b00,0x1c6bb0]
out=[];ranges=[]
for seed in seeds:
 idx=bisect.bisect_right([x[0] for x in allins],seed)-1; starts=[j for j,x in enumerate(allins[:idx+1]) if x[2]=='push' and 'lr' in x[3] and 'r4' in x[3]]; first=starts[-1]; following=[x[0] for x in allins[idx+1:] if x[2]=='push' and 'lr' in x[3] and 'r4' in x[3]]; a=allins[first][0];b=following[0];ranges.append((a,b))
 out.append(f'\nSEED {seed:#x}; prologue-heuristic interval {a:#x}..{b:#x}')
 out.extend(fmt(x) for x in allins if a<=x[0]<b)
 out.append('INCOMING DIRECT CALLS to interval start:')
 for x in allins:
  if x[2] in ('b','bl') and x[3].startswith('#') and int(x[3][1:],16)==a:out.append(fmt(x))
(BASE/'delphi-analysis/native-transport-functions.txt').write_text('\n'.join(out),encoding='utf-8')
print('Heuristic ranges',[(hex(a),hex(b)) for a,b in ranges]);print('lines',len(out))




