"""Sectionless DisplayManagement ELF analysis; offline reads only."""
import io,json,re,struct,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM,ARM_REG_PC,ARM_REG_IP
OUT=BASE/'delphi-analysis';p=OUT/'extracted/delphibin/DisplayManagement';blob=p.read_bytes();elf=ELFFile(io.BytesIO(blob));segs=[(s['p_vaddr'],s.data(),s['p_flags']) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
def rd(va,n):
 for start,data,_ in segs:
  if start<=va and va+n<=start+len(data):return data[va-start:va-start+n]
 return b''
def cstr(va):
 for start,data,_ in segs:
  if start<=va<start+len(data):
   o=va-start;return data[o:data.find(b'\0',o)].decode('ascii',errors='replace')
 return ''
dyn=next(s for s in elf.iter_segments() if s['p_type']=='PT_DYNAMIC');tags={t.entry.d_tag:t.entry.get('d_val',0) for t in dyn.iter_tags()};names={}
for reladdr in range(tags['DT_JMPREL'],tags['DT_JMPREL']+tags['DT_PLTRELSZ'],8):
 off,info=struct.unpack('<II',rd(reladdr,8));idx=info>>8;sn=struct.unpack('<I',rd(tags['DT_SYMTAB']+idx*16,4))[0];names[off]=cstr(tags['DT_STRTAB']+sn)
md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.detail=True;md.skipdata=True
instructions=[]
for start,data,flags in segs:
 if flags&1:instructions.extend(md.disasm(data,start))
labels={}
for i,a in enumerate(instructions[:-2]):
 b,c=instructions[i+1:i+3]
 try:
  if a.mnemonic=='add' and b.mnemonic=='add' and c.mnemonic=='ldr' and a.operands[0].reg==ARM_REG_IP and a.operands[1].reg==ARM_REG_PC and b.operands[0].reg==ARM_REG_IP and c.operands[0].reg==ARM_REG_PC:
   def armimm(ins):
    v=int.from_bytes(ins.bytes,'little');x=v&255;n=((v>>8)&15)*2;return ((x>>n)|(x<<(32-n)))&0xffffffff if n else x
   got=a.address+8+armimm(a)+armimm(b)+c.operands[1].mem.disp
   if got in names:labels[a.address]=names[got]
 except (IndexError,AttributeError):pass
strings={}
for start,data,_ in segs:
 for m in re.finditer(rb'[\x20-\x7e]{5,}',data):strings[start+m.start()]=m.group().decode()
wanted={a:s for a,s in strings.items() if any(n in s for n in ['switchContextCluster','handleExtLayer','setUpdateRate','initExtLayerStates','getDisplayType','handleMessageSCDAExternalLayerResponse'])}
refs=[];prologs=[];wide={}
for i,ins in enumerate(instructions):
 if not ins.id:continue
 if (ins.mnemonic=='push' and 'lr' in ins.op_str) or (ins.mnemonic=='str' and ins.op_str.startswith('lr, [sp, #-4]!')):prologs.append(ins.address)
 if ins.mnemonic=='movw':wide[ins.operands[0].reg]=ins.operands[1].imm
 if ins.mnemonic=='movt' and ins.operands[0].reg in wide:
  va=wide[ins.operands[0].reg]|(ins.operands[1].imm<<16)
  if va in wanted:refs.append({'instruction':hex(ins.address),'string_va':hex(va),'text':wanted[va],'candidate_function_start':hex(prologs[-1]) if prologs else None,'index':i})
 if ins.mnemonic=='ldr' and len(ins.operands)>1 and ins.operands[1].type==ARM_OP_MEM and ins.operands[1].mem.base==ARM_REG_PC:
  data=rd(ins.address+8+ins.operands[1].mem.disp,4)
  if len(data)==4 and (va:=struct.unpack('<I',data)[0]) in wanted:
   refs.append({'instruction':hex(ins.address),'string_va':hex(va),'text':wanted[va],'candidate_function_start':hex(prologs[-1]) if prologs else None,'index':i})
def fmt(ins):
 note=''
 if ins.id and ins.mnemonic in ('bl','b'):
  note=labels.get(ins.operands[0].imm,'')
 return f'{ins.address:08x} {ins.mnemonic:8s} {ins.op_str:40s} {note}'
(OUT/'display-hmi-native-assembly.txt').write_text('\n'.join(map(fmt,instructions)),encoding='utf-8')
(OUT/'display-hmi-native-xrefs.json').write_text(json.dumps({'imports':names,'plt':{hex(k):v for k,v in labels.items()},'refs':refs},indent=2),encoding='utf-8')
windows=[]
for r in refs:
 windows.append('\n'+json.dumps({k:v for k,v in r.items() if k!='index'}))
 i=r['index'];windows.extend(fmt(x) for x in instructions[max(0,i-15):i+35])
(OUT/'display-hmi-native-xref-windows.txt').write_text('\n'.join(windows),encoding='utf-8')
print('Recovered imports',len(names),'PLT labels',len(labels),'target string refs',len(refs))
for r in refs:print(r['candidate_function_start'],r['instruction'],r['text'])


