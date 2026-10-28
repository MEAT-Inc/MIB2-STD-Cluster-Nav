"""Read-only offline ARM transport trace. Produces snippets, never runs acquired files."""
from pathlib import Path
import io,json,re,struct,sys
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
OUT=BASE/'delphi-analysis';out=[]
for filename in ['NavigationServer','TransportServer','Most']:
 p=BASE/'delphi-dump/extbin/apps/bin'/filename;e=ELFFile(io.BytesIO(p.read_bytes()))
 segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 def read(va,n):
  for start,data in segments:
   if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
  return b''
 def string(va):
  for start,data in segments:
   if start<=va<start+len(data):
    off=va-start;end=data.find(b'\0',off,min(off+500,len(data)));chunk=data[off:end]
    if end>=0 and len(chunk)>=4 and all(32<=c<127 for c in chunk):return chunk.decode()
  return ''
 labels={}
 for s in e.iter_sections():
  if s['sh_type'] in ('SHT_SYMTAB','SHT_DYNSYM'):
   labels.update({x['st_value']:x.name for x in s.iter_symbols() if x['st_value']})
 plt=e.get_section_by_name('.plt');rel=e.get_section_by_name('.rel.plt')
 if plt and rel:
  sy=e.get_section(rel['sh_link'])
  labels.update({plt['sh_addr']+20+12*i:sy.get_symbol(r['r_info_sym']).name+' [PLT]' for i,r in enumerate(rel.iter_relocations())})
 md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.skipdata=True
 sec=e.get_section_by_name('.text');ins=list(md.disasm_lite(sec.data(),sec['sh_addr']))
 def fmt(item):
  va,size,mn,op=item;note=''
  if mn in ('bl','b') and op.startswith('#'):note=labels.get(int(op[1:],16),'')
  if mn.startswith('ldr') and '[pc' in op:
   m=re.search(r'\[pc(?:, #(-?0x[0-9a-f]+|-?\d+))?\]',op)
   if m:
    off=int(m.group(1) or '0',0);data=read(va+8+off,4)
    if len(data)==4:
     val=struct.unpack('<I',data)[0]; note+=f' literal={val:#x} '+string(val)
  return f'{va:08x} {mn:8s} {op:42s} {note}'
 out.append('\nFILE '+filename)
 chosen=[]
 if filename=='NavigationServer':
  for i,x in enumerate(ins):
   va,size,mn,op=x
   if ('#0x128]' in op and mn.startswith(('str','ldr'))) or (mn=='bl' and labels.get(int(op[1:],16),'').split(' ')[0] in ('open','open64','close','write','devctl','ioctl')):
    chosen.append((i,'DESCRIPTOR/IO '+fmt(x)))
 else:
  for i,x in enumerate(ins):
   text=fmt(x)
   if any(n in text for n in ['spawn/','connect/','isoTX','TransportServerConfig','MOST_ISO','isochronous','ts_packet','ringBuffer']):chosen.append((i,text))
 seen=set()
 for i,title in chosen:
  out.append('\nHIT '+title)
  for j in range(max(0,i-28),min(len(ins),i+35)):
   if j not in seen:out.append(fmt(ins[j]));seen.add(j)
 print(filename,'instructions',len(ins),'hits',len(chosen))
(OUT/'native-transport-snippets.txt').write_text('\n'.join(out),encoding='utf-8')
print('Output lines',len(out))
