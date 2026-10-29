"""Find candidate Android Auto shutdown string references. Static data only.
Constant propagation is linear and heuristic; emitted windows require manual review.
"""
from pathlib import Path
import io,json,re,struct,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from capstone.arm import ARM_OP_REG,ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC,ARM_REG_R4
p=ROOT/'delphi-dump/extbin/apps/bin/AndroidAuto';blob=p.read_bytes()
assert hashlib.sha256(blob).hexdigest()=='da1fd5776f6b85962b84ad77c6f564d3f09dd8079652229cda57b4138060c271'
e=ELFFile(io.BytesIO(blob));loads=[(s['p_vaddr'],s.data(),s['p_flags']) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def read(a,n):
 for start,data,_ in loads:
  if start<=a and a+n<=start+len(data):return data[a-start:a-start+n]
 return b''
strings={a+m.start():m.group().decode() for a,data,_ in loads for m in re.finditer(rb'[ -~]{6,}',data)}
md=Cs(CS_ARCH_ARM,CS_MODE_ARM);md.detail=True;md.skipdata=True
text=e.get_section_by_name('.text');ins=list(md.disasm(read(text['sh_addr'],text['sh_size']),text['sh_addr']))
# The reviewed onMessage prologue initializes r4 as a PIC base. Embedded literal
# pools interrupt linear disassembly; retain that function-local invariant there.
pic_base=(0x1104d4+8+struct.unpack('<I',read(0x110b00,4))[0])&0xffffffff
regs={};refs=[]
for idx,i in enumerate(ins):
 if not i.id:regs.clear();continue
 ops=i.operands;value=None
 if 0x1104d8<=i.address<0x1125e0:regs[ARM_REG_R4]=pic_base
 def val(op):
  if op.type==ARM_OP_IMM:return op.imm
  if op.type==ARM_OP_REG:return i.address+8 if op.reg==ARM_REG_PC else regs.get(op.reg)
  return None
 if i.mnemonic=='push':regs.clear()
 if i.mnemonic=='ldr' and len(ops)==2 and ops[1].type==ARM_OP_MEM and ops[1].mem.base==ARM_REG_PC:
  b=read(i.address+8+ops[1].mem.disp,4)
  if len(b)==4:value=struct.unpack('<I',b)[0]
 elif i.mnemonic in ('mov','movw') and len(ops)==2:value=val(ops[1])
 elif i.mnemonic=='movt' and len(ops)==2 and ops[0].reg in regs:value=(regs[ops[0].reg]&65535)|(ops[1].imm<<16)
 elif i.mnemonic in ('add','sub') and len(ops)==3:
  a,b=val(ops[1]),val(ops[2])
  if a is not None and b is not None:value=(a+b if i.mnemonic=='add' else a-b)&0xffffffff
 _,writes=i.regs_access()
 for r in writes:regs.pop(r,None)
 if value is not None and ops[0].type==ARM_OP_REG:
  regs[ops[0].reg]=value
  if value in strings and ('Server::onMessage' in strings[value] or 'exit' in strings[value].lower()):
   refs.append(dict(index=idx,va=i.address,target=value,text=strings[value]))
 if i.mnemonic in ('bl','blx'):
  for r in list(regs):
   if md.reg_name(r) in ("r0","r1","r2","r3","ip","lr"):regs.pop(r,None)
out=ROOT/'delphi-analysis/control-runtime'
(out/'android-shutdown.xrefs.json').write_text(json.dumps(refs,indent=2))
lines=[]
for r in refs:
 if 'EV_APP_EXIT' not in r['text']:continue
 lines.append('CANDIDATE STRING REFERENCE '+repr(r))
 for i in ins[max(0,r['index']-35):r['index']+70]:lines.append(f'{i.address:08x} {i.mnemonic:9} {i.op_str}')
(out/'android-shutdown.focused.txt').write_text('\n'.join(lines))
print('Candidate references:',len(refs))
print('\n'.join(lines))
