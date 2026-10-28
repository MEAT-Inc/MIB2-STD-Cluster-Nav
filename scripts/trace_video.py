"""Offline ARM disassembly and protocol field inventory; no binary execution."""
from pathlib import Path
import io,json,re,struct,sys,zipfile
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'.tools/python'))
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM,CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM,ARM_REG_PC
OUT=BASE/'delphi-analysis'
R=json.loads((OUT/'elf-symbols.json').read_text())
report=[]
for rec in R:
    path=BASE/rec['file']
    if path.name not in ('AndroidAuto','NavigationServer','libautoreceiver.so','ClusterServices'):continue
    elf=ELFFile(io.BytesIO(path.read_bytes()))
    def readva(va,n):
        for seg in elf.iter_segments():
            if seg['p_type']=='PT_LOAD' and seg['p_vaddr']<=va and va+n<=seg['p_vaddr']+seg['p_filesz']:
                off=va-seg['p_vaddr'];return seg.data()[off:off+n]
        return b''
    syms={s['name']:s for s in rec['symbols']}
    labels={s['address']:s['name'] for s in syms.values() if s['address']}
    report.append('\nFILE '+rec['file'])
    md=Cs(CS_ARCH_ARM,CS_MODE_ARM|CS_MODE_LITTLE_ENDIAN);md.detail=True;md.skipdata=True
    if path.name=='libautoreceiver.so':
        for name,s in syms.items():
            if 'FieldNumber' in name and any(k in name for k in ('MediaSinkService','VideoConfiguration','ServiceDiscoveryResponse')):
                data=readva(s['address'],4)
                report.append(f'FIELD {name}: {struct.unpack("<I",data)[0]}')
        wanted=['_ZN9VideoSink16addDiscoveryInfoEP24ServiceDiscoveryResponse','_ZN9VideoSink25addSupportedConfigurationEiiiiiii','_ZNK16MediaSinkService24SerializeWithCachedSizesEPN6google8protobuf2io17CodedOutputStreamE','_ZNK18VideoConfiguration24SerializeWithCachedSizesEPN6google8protobuf2io17CodedOutputStreamE']
        for name in wanted:
            s=syms[name];report.append('\nFUNCTION '+name+' '+hex(s['address']))
            for ins in md.disasm(readva(s['address'],s['size']),s['address']):
                extra=''
                if ins.id and ins.mnemonic in ('bl','b'):
                    try: extra=labels.get(ins.operands[0].imm,'')
                    except Exception:pass
                report.append(f'{ins.address:08x} {ins.mnemonic:8s} {ins.op_str} {extra}')
    else:
        needles= {'AndroidAuto':['AaVideoSink.cpp','serviceDiscoveryRequestCallback','addSupportedConfigurations'], 'NavigationServer':['/dev/transport_server/spawn/isoTX','::renderedFPK(..) VE_Encode','::transportStreamPackagesReady('], 'ClusterServices':['Registering GfxStreamSink on MOST']}[path.name]
        targets={}
        for sec in elf.iter_sections():
            if sec['sh_flags']&2 and not sec['sh_flags']&4 and sec['sh_type']!='SHT_NOBITS':
                blob=sec.data()
                for needle in needles:
                    p=blob.find(needle.encode())
                    if p>=0:targets[sec['sh_addr']+p]=needle
        report.append('STRING TARGETS '+repr({hex(k):v for k,v in targets.items()}))
        text=elf.get_section_by_name('.text'); instructions=list(md.disasm(text.data(),text['sh_addr']))
        seen=set()
        for i,ins in enumerate(instructions):
            if not ins.id:continue
            if ins.mnemonic=='ldr' and len(ins.operands)>1 and ins.operands[1].type==ARM_OP_MEM and ins.operands[1].mem.base==ARM_REG_PC:
                addr=ins.address+8+ins.operands[1].mem.disp
                v=readva(addr,4)
                if len(v)==4:
                    val=struct.unpack('<I',v)[0]
                    if val in targets:
                        report.append(f'XREF {targets[val]} @ {ins.address:#x} literal {addr:#x}')
                        for line in instructions[max(0,i-12):i+35]:
                            if line.address not in seen:
                                report.append(f'{line.address:08x} {line.mnemonic:8s} {line.op_str}')
                                seen.add(line.address)
        # Also record literal pool words containing target VAs, for manual PIC analysis.
        blob=path.read_bytes()
        for va,label in targets.items():
            needle=struct.pack('<I',va);start=0;offs=[]
            while (pos:=blob.find(needle,start))>=0:
                offs.append(hex(pos));start=pos+1
            report.append('POINTER FILE OFFSETS '+label+': '+repr(offs))
(OUT/'protocol-and-xrefs.txt').write_text('\n'.join(report),encoding='utf-8')
for path in (OUT/'extracted/vwjxe').iterdir():
    with zipfile.ZipFile(path) as z:
        print(path.name,[(i.filename,i.file_size) for i in z.infolist()][:12])
print('Saved',len(report),'lines to protocol-and-xrefs.txt')
